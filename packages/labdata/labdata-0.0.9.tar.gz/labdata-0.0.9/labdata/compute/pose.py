from ..utils import *
from .utils import BaseCompute

class DeeplabcutCompute(BaseCompute):
    container = 'labdata-deeplabcut'
    cuda = True
    name = 'deeplabcut'
    url = 'http://github.com/DeepLabCut/DeepLabCut'
    def __init__(self,job_id, allow_s3 = None, delete_results = True, **kwargs):
        '''
        Run deeplabcut on video or train a model
        '''
        super(DeeplabcutCompute,self).__init__(job_id, allow_s3 = allow_s3)
        self.file_filters = ['.avi','.mov','.mp4','.zarr'] # allowed file extensions..
        # default parameters
        self.parameters = dict(algorithm = 'deeplabcut',
                               mode = None, # select 'train' or 'infer'
                               model_num = None,
                               label_set = None,
                               video_name = None,
                               net_type = 'resnet_50',
                               batch_size = 8,
                               iteractions = 100000)
        self._init_job()
        if not self.job_id is None:
            self.add_parameter_key()

        self.delete_results = delete_results

    def add_parameter_key(self):
        model_num, parameters = self._get_parameter_number()
        from ..schema import PoseEstimationModel
        if self.parameters['mode'] == 'train':
            #if not model_num in parameters.model_num.values:
            #    PoseEstimationModel().insert1(dict(model_num = model_num,
            #                                       pose_label_set_num = self.parameters['label_set'], 
            #                                      algorithm_name = self.name,
            #                                       parameters_dict = json.dumps(self.model_parameters),
            #                                       code_link = self.url),
            #                                  skip_duplicates=True) # these will be updated later
            self.model_num = model_num
        # check here if it was already infered with this model.

    def _get_parameter_number(self):
        self.model_parameters = dict(algorithm = self.parameters['algorithm'],
                                     net_type = self.parameters['net_type'],
                                     batch_size = self.parameters['batch_size'],
                                     iteractions = self.parameters['iteractions'])
        parameter_set_num = None
        from ..schema import PoseEstimationModel
        parameters = pd.DataFrame(PoseEstimationModel().fetch())
        model_num = None
        if self.parameters['mode'] == 'train':
            for i,r in parameters.iterrows():
                # go through every parameter and label_set
                if (self.model_parameters == json.loads(r.parameters_dict) and 
                    self.parameters['model_num'] is None and 
                    self.parameters['pose_label_set_num'] == r['pose_label_set_num']):
                    model_num = r.model_num
            if model_num is None:
                if not self.parameters['model_num'] is None:
                    model_num = self.parameters['model_num']
                elif len(parameters) == 0:
                    model_num = 1
                else:
                    model_num = np.max(parameters.model_num.values)+1
            self.parameters['model_num'] = model_num
            return model_num,parameters
        else:
            return self.parameters['model_num'],parameters
    
    def _secondary_parse(self,arguments,parameters = None):
        '''
        Handles parsing the command line interface
        '''
        if not parameters is None: # can just pass the parameters
            self.parameters = parameters
        else:
            import argparse
            parser = argparse.ArgumentParser(
                description = 'Pose estimation analysis using DeepLabCut',
                usage = '''
    deeplabcut -a <SUBJECT> -s <SESSION> -- <TRAIN|INFER> <PARAMETERS>
    
    Example for inference using a trained model (-m 1):
    
        labdata2 run deeplabcut -a JC131 -s 20231025_194303 -- infer -m 1 -v side_cam            
                
                ''')
            
            parser.add_argument('mode',action='store', type = str,
                                help = '[required] Specifies what to do (train or infer)')
            parser.add_argument('-v','--video-name',
                                action='store', type = str, default = None,
                                help = "Select files to analyze (DatasetVideo.video_name)")
            parser.add_argument('-l','--label-set',
                                action='store', default=None, type = int,
                                help = "Label set to run training.")
            parser.add_argument('-m','--model-num',
                                action='store', default=None, type = int,
                                help = "Model number to run inference.")
            parser.add_argument('--net-type',
                                action='store', type = str, default = 'resnet_50',
                                help = "Network to run (has to be in the container - resnet_50; resnet_101)")
            parser.add_argument('-i','--iteractions',
                                action='store', default=300000, type = int,
                                help = "Number of iteractions for training")
            args = parser.parse_args(arguments[1:])
            self.parameters['mode'] = args.mode
            self.parameters['video_name'] = args.video_name
            self.parameters['label_set'] = args.label_set
            self.parameters['model_num'] = args.model_num
            self.parameters['net_type'] = args.net_type
            self.parameters['iteractions'] = args.iteractions
        if 'train' in  self.parameters['mode']:
            if self.parameters['label_set'] is None:
                raise(ValueError('Need to define a label-set to train a model.'))
        else:
            if self.parameters['model_num'] is None:
                raise(ValueError('Need to specify a model.'))
            from ..schema import PoseEstimationModel
            if not len(PoseEstimationModel & f'model_num = {self.parameters["model_num"]}'):
                raise(ValueError(f'Could not find model {self.parameters["model_num"]}'))
        
    def find_datasets(self, subject_name = None, session_name = None):
        '''
        Searches for subjects and sessions 
        '''
        if self.parameters['mode'] ==  'train':
            # check that the label set exists...
            from ..schema import PoseEstimationLabelSet
            pose_label_set = (PoseEstimationLabelSet() & f'pose_label_set_num = {self.parameters["label_set"]}').fetch()
            return 
        if subject_name is None and session_name is None and self.parameters['mode'] == 'infer':
            raise(ValueError('Need to select a dataset to infer using a deeplabcut model.'))
        keys = []
        if not subject_name is None:
            if len(subject_name) > 1:
                raise ValueError(f'Please submit one subject at a time {subject_name}.')
            if not subject_name[0] == '':
                subject_name = subject_name[0]
        if not session_name is None:
            for s in session_name:
                if not s == '':
                    keys.append(dict(subject_name = subject_name,
                                     session_name = s))
        else:
            raise(NotImplementedError('Specifying no session is not yet implemented'))
        from ..schema import DatasetVideo
        datasets = []
        for k in keys:
            datasets += (DatasetVideo()& k).fetch(as_dict = True)
        datasets = [dict(subject_name = d['subject_name'],
                         session_name = d['session_name'],
                         dataset_name = d['dataset_name']) for d in datasets]
        datasets = list({v['session_name']:v for v in datasets}.values())
        return datasets

    def _compute(self):
        import deeplabcut
        from ..schema import PoseEstimationLabelSet, PoseEstimationModel, DatasetVideo, File, PoseEstimation
        if self.parameters['mode'] ==  'train':
            # check that the label set exists...
            print(self.parameters)
            print(f'pose_label_set_num = {self.parameters["label_set"]}')
            pose_label_set = PoseEstimationLabelSet() & f'pose_label_set_num = {self.parameters["label_set"]}'
            cfgfile = create_project(self.parameters,self.parameters['model_num'])
            #print("Checking the labels.")
            #deeplabcut.check_labels(cfgfile)
            print("Generating the training dataset")
            deeplabcut.create_training_dataset(cfgfile)
            print("Training network")
            deeplabcut.train_network(cfgfile, maxiters = self.parameters['iteractions'])
            # once training completes, create a zip with the model and upload.
            PoseEstimationModel().insert_model(self.parameters['model_num'], 
                     model_folder=Path(cfgfile).parent,
                     pose_label_set_num = self.parameters["label_set"],
                     algorithm_name = self.parameters['algorithm'],
                     parameters = self.model_parameters,
                     training_datetime=datetime.now(),
                     container_name = self.container,
                     code_link = self.url)
            # Save to PoseEstimationModel()
        elif self.parameters['mode'] == 'infer':
            # download the model if needed
            cfgfile = (PoseEstimationModel() & f'model_num = {self.parameters["model_num"]}').get_model()
            datasets = (File() & (DatasetVideo.File() & self.dataset_key)).fetch(as_dict = True)
            if not len(datasets):
                raise(ValueError(f"Could not find {self.dataset_key}"))
            if len(datasets) > 1:
                # select the video to analyse
                datasets = (File() & (DatasetVideo.File() & dict(
                    self.dataset_key,
                    video_name = self.parameters['video_name']))).fetch(as_dict = True)
            localfiles = self.get_files(datasets)
            resfile = deeplabcut.analyze_videos(cfgfile,[str(f) for f in localfiles], videotype='.avi')
            
            # Save the results to PoseEstimation()
            if len(localfiles)>1:
                print(f'Not sure how to insert multiple files.. Check the inputs {localfiles}.')
            resfile = Path(str(localfiles[0].with_suffix(''))+resfile).with_suffix('.h5') # assuming there is only one file
            bodyparts,xyl = read_dlc_file(resfile)  
            toinsert = []
            for i,b in enumerate(bodyparts):
                toinsert.append(dict(self.dataset_key,
                                     video_name = self.parameters['video_name'],
                                     model_num = self.parameters["model_num"],
                                     label_name = b,
                                     x = xyl[:,i,0],
                                     y = xyl[:,i,1],
                                     likelihood = xyl[:,i,2]))
            PoseEstimation().insert(toinsert)
            
def create_project(parameters,model_num):
    import deeplabcut
    from ..schema import PoseEstimationLabelSet
    print(f'Creating model {model_num} from pose_label_set_num {parameters["label_set"]}')
    
    parameter_set_key = (PoseEstimationLabelSet() & f'pose_label_set_num = {parameters["label_set"]}').proj().fetch1()
    parameter_set = (PoseEstimationLabelSet & parameter_set_key).fetch1()
    labels = (PoseEstimationLabelSet.Label & parameter_set_key).fetch()

    project_path,frames,frames_labels = (PoseEstimationLabelSet & parameter_set_key).export_labeling(
        model_num = model_num,
        export_only_labeled = True)
    print(f'Exporting to {project_path}.')
    F = frames['frame'].iloc[0]
    project_path = project_path.parent.parent
    bodyparts = [a for a in np.unique(labels['label_name'])]

    cfg_file, ruamelFile = deeplabcut.utils.auxiliaryfunctions.create_config_template(multianimal= False)
    
    cfg_file["multianimalproject"] = False
    cfg_file["bodyparts"] = bodyparts 
    cfg_file["skeleton"] = [bodyparts,bodyparts]
    cfg_file["default_augmenter"] = "default"
    cfg_file["default_net_type"] = parameters['net_type']

    # common parameters:
    cfg_file["Task"] = f'model_{model_num}'
    cfg_file["scorer"] = parameter_set['labeler']
    cfg_file["video_sets"] = {f'label_set_{parameters["label_set"]}':dict(crop=[0,F.shape[0],0,F.shape[1]])}
    cfg_file["project_path"] = str(project_path)
    cfg_file["date"] = datetime.now().strftime('%b%d')
    cfg_file["cropping"] = False
    cfg_file["batch_size"] = parameters["batch_size"]
    cfg_file["start"] = 0
    cfg_file["stop"] = 1
    cfg_file["numframes2pick"] = 20
    cfg_file["TrainingFraction"] = [0.95]
    cfg_file["iteration"] = 0
    cfg_file["snapshotindex"] = -1
    cfg_file["x1"] = 0
    cfg_file["x2"] = 640
    cfg_file["y1"] = 277
    cfg_file["y2"] = 624
    cfg_file["corner2move2"] = (50, 50)
    cfg_file["move2corner"] = True
    cfg_file["skeleton_color"] = "black"
    cfg_file["pcutoff"] = 0.6
    cfg_file["dotsize"] = 12  # for plots size of dots
    cfg_file["alphavalue"] = 0.7  # for plots transparency of markers
    cfg_file["colormap"] = "rainbow"  # for plots type of colormap
    for p in ['videos','training-datasets','dlc-models']:
        (project_path/p).mkdir(exist_ok = True)
    projconfigfile = os.path.join(str(project_path), "config.yaml")
    # Write dictionary to yaml  config file
    deeplabcut.utils.auxiliaryfunctions.write_config(projconfigfile, cfg_file)
    return projconfigfile


def read_dlc_file(filepath):
    posture = pd.read_hdf(filepath)

    scorer = np.unique(posture.columns.get_level_values(0))[0]
    bodyparts = np.unique(posture.columns.get_level_values(1))
    xyl = []
    for part in bodyparts:            
        xyl.append(np.vstack([posture[scorer][part]['x'].values,posture[scorer][part]['y'].values,posture[scorer][part]['likelihood'].values]))
    xyl = np.stack(xyl).transpose(2,0,1) #frames,bodyparts,x-y-likelihood
    return bodyparts, xyl
