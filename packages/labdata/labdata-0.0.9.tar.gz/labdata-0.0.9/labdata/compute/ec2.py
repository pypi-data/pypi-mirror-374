from ..utils import *

def ec2_connect(access_key = None,secret_key = None, region = None):
    import boto3
    if 'aws' in prefs['compute'].keys():
        if 'access_key' in prefs['compute']['aws'].keys():
            access_key = prefs['compute']['aws']['access_key']
            secret_key = prefs['compute']['aws']['secret_key']
            region = prefs['compute']['aws']['region']
        if access_key is None:
            raise ValueError('Need to supply an access key to access ec2, set compute:aws:access_key in the preference file.')
    if region[-1].isalpha(): # then it includes the availability zone
        region = region[:-1]
    botosession = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key, region_name = region)
    
    ec2 = botosession.resource('ec2',region_name = region)
    return (botosession,ec2)

def ec2_get_key(ec2 = None, keyname = None):
    keyspath = Path(prefs['compute']['aws']['access_key_folder'])
    keys = list(keyspath.glob('*'))
    if not len(keys):
        date = datetime.now().strftime('%Y%m%d_%H:%M:%S')
        keyname = f"ec2-labdata-{prefs['hostname']}-{date}"
        if ec2 is None:
            session,ec2 = ec2_connect()
        key = ec2.create_key_pair(KeyName=keyname)
        # save key info
        keyspath.mkdir(parents=True, exist_ok=True)
        with open(keyspath/keyname,'w') as fd:
            keyinfo = dict(key_name = key.key_name,
                           key_material = key.key_material,
                           key_pair_id = key.key_pair_id)
            json.dump(keyinfo, 
                      fd, 
                      indent = 4)
    else:
        with open(keys[0],'r') as fd:
            keyinfo = json.load(fd)
    return keyinfo

def ec2_instance_from_id(ec2,instance_id):
    if ec2 is None:
        session,ec2 = ec2_connect()
    instances = list(ec2.instances.filter(InstanceIds=[instance_id]))
    if not len(instances):
        print(f'There are no instances with id: {instance_id}')
    elif len(instances)!=1:
        print(f'There are multiple instances with id: {instance_id}')
        return instances
    else:
        return instances[0]
        
def ec2_create_instance(ec2,
                        image_id = "linux",
                        instance_type = "t2.micro", 
                        key_name = None,
                        availability_zone = None,
                        security_groups = None, # these should come from the preferences
                        user_data = 'echo hostname'):
    if not image_id in prefs['compute']['aws']['image_ids'].keys():
        raise ValueError(f'image_id {image_id} is not in the preference_file {list(prefs["compute"]["aws"]["image_ids"].keys())}')

    if ec2 is None:
        session,ec2 = ec2_connect()
    if security_groups is None:
        security_groups = prefs['compute']['aws']['security_groups']
    image_id = prefs['compute']['aws']['image_ids'][image_id]
    if key_name is None:
        keyinfo = ec2_get_key(ec2)
        key_name = keyinfo['key_name']
    if availability_zone is None:
        availability_zone = prefs['compute']['aws']['region']
    insdict = dict(instance = ec2.create_instances(
        ImageId = image_id['ami'],
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        KeyName=key_name,
        InstanceInitiatedShutdownBehavior='terminate',
        UserData = user_data,
        Placement={'AvailabilityZone':availability_zone},
        SecurityGroups=security_groups)[0],
                   key_name = key_name,
                   instance_type = instance_type,
                   user_name = image_id['user'],
                   ami = image_id['ami'])
    insdict['id'] = insdict['instance'].id
    #print(user_data)
    return insdict

def ec2_wait_for_instance(ec2,instancedict,desired = 'running',interval = 0.05):
    if ec2 is None:
        session,ec2 = ec2_connect()

    instance = ec2_instance_from_id(instancedict['id'])
    instance.wait_until_running()
    import time
    while instance.state['Name'] != desired:
        time.sleep(interval)
        instance = ec2_instance_from_id(ins['id'])
    instancedict['instance'] = instance
    return instance


def ec2_instance_ssh(instance,  user = 'ubuntu'):
    import paramiko 
    
    ip_address = instance.public_dns_name
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    privkey = ec2_get_key()['key_material']
    try:
        from StringIO import StringIO 
    except ImportError:
        from io import StringIO # Python3
    privkey = paramiko.RSAKey.from_private_key(StringIO(privkey)) 
    
    print('SSH into the instance: {}'.format(ip_address))
    ssh.connect(hostname=ip_address,
                username=user, pkey=privkey)
    return ssh

def ec2_cmd_for_launch(singularity_container,
                       singularity_command,
                       singularity_cuda = False,
                       nvme = 'nvme1n1',
                       shutdown_when_done = True,
                       is_self_contained = True,
                       append_log = True):
    userdata = ''
    if not nvme is None:
        userdata += f'''#! /bin/bash
# mount  the data drive and set permissions 
mkfs -t ext4 /dev/{nvme}
mkdir /data
mount /dev/{nvme} /data/
chown -R ubuntu /data
# make home point to /data where there is space
export HOME="/data"  
'''


    storage = prefs['storage'][prefs['compute']['containers']['storage']]

    userdata += f'''
mkdir $HOME/.aws
echo "[default]" > $HOME/.aws/credentials
echo aws_access_key_id={storage['access_key']} >> $HOME/.aws/credentials
echo aws_secret_access_key={storage['secret_key']} >> $HOME/.aws/credentials
mkdir -p $HOME/labdata/containers
echo "Downloading container"
aws s3 cp s3://{storage['bucket']}/containers/{singularity_container}.sif  $HOME/labdata/containers/

'''
    if is_self_contained:
        ec2pref = json.dumps(dict(compute = dict(containers=dict(local = '/data'),
                                                 analysis = prefs['compute']['analysis'],
                                                 default_target = 'local'),
                                  database = prefs['database'],
                                  local_paths = ['/data'],
                                  scratch_path = '/data',
                                  path_rules = prefs['path_rules'],
                                  storage = prefs['storage'],
                                  allow_s3_download = True,
                                  use_awscli = True))
        cuda = ''
        if singularity_cuda:
            cuda = '--nv'
            userdata += '''
modprobe nvidia-uvm
nvidia-container-cli -k list
'''
        userdata += f'''
cat > $HOME/labdata/user_preferences.json << EOL
{ec2pref}
EOL

mkdir -p /home/ubuntu/labdata
cp $HOME/labdata/user_preferences.json /home/ubuntu/labdata/
mkdir -p /home/ubuntu/.cache/torch/kernels
sudo chown -R ubuntu /home/ubuntu

sudo -u ubuntu bash -c "cd /home/ubuntu; singularity exec {cuda} --bind /data:/data $HOME/labdata/containers/{singularity_container}.sif {singularity_command}'''
        if not append_log is None:
            userdata += f' |& singularity exec $HOME/labdata/containers/{singularity_container}.sif labdata2 logpipe {append_log}'
        userdata += '"'
    if shutdown_when_done:
        userdata += '''

shutdown now -h
'''

    return userdata
