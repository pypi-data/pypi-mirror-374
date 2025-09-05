from .general import *

@dataschema
class DatasetVideo(dj.Manual):
    definition = '''
    -> Dataset
    video_name           : varchar(56)
    ---
    frame_times = NULL   : longblob
    frame_rate = NULL    : float
    n_frames = NULL      : float
    '''

    class File(dj.Part):
        definition = '''
        -> master
        -> File
        '''

    class Frame(dj.Part):
        definition = '''
        -> master
        frame_num      : int
        ---
        frame          : longblob
        '''

######################################################
############      POSE ESTIMATION      ###############
######################################################
@analysisschema
class PoseEstimationLabelSet(dj.Manual):
    definition = '''
    pose_label_set_num    : int
    ---
    description = NULL    :  varchar(512)
    -> [nullable] LabMember.proj(labeler = "user_name")
    '''
    class Frame(dj.Part):
        definition = '''
        -> master
        -> DatasetVideo
        frame_num : int
        ---
        frame     : longblob
        '''
    class Label(dj.Part):
        definition = '''
        -> master
        -> DatasetVideo
        frame_num  : int
        label_name : varchar(54)
        ---
        x          : float
        y          : float
        z = NULL   : float 
        '''
    def export_labeling(self, model_num = None, bodyparts = None, disperse_labels = False, export_only_labeled = False):
        '''
        Exports labeling for PoseEstimation (for use with napari-deeplabcut)
        '''
        assert len(self) == 1, ValueError('PoseEstimationLabelSet, select only one set to export.')
        k = self.proj().fetch1()
        
        if export_only_labeled:
            frames = pd.DataFrame((PoseEstimationLabelSet()*PoseEstimationLabelSet.Frame() & (PoseEstimationLabelSet.Label() & k)).fetch())
        else:
            frames = pd.DataFrame((PoseEstimationLabelSet()*PoseEstimationLabelSet.Frame() & k).fetch())
        frame_labels = pd.DataFrame((PoseEstimationLabelSet()*PoseEstimationLabelSet.Label() & k).fetch())
        
        if model_num is None:
            folder = (Path(prefs['local_paths'][0])/'pose_estimation_models')/f'pose_label_set_num_{k["pose_label_set_num"]}'
        else:
            folder = (Path(prefs['local_paths'][0])/'pose_estimation_models')/f'model_{model_num}'
        data_path = (folder / "labeled-data") / f'label_set_{k["pose_label_set_num"]}'
        data_path.mkdir(parents=True, exist_ok=True)
        if bodyparts is None:
            bodyparts = np.unique(frame_labels.label_name.values)
        from natsort import natsorted
        bodyparts = natsorted(bodyparts) # this is an attempt to sort the labels
        labeler = frames['labeler'].iloc[0]
        from skimage.io import imsave
        from tqdm import tqdm
        todlc = []
        for i,f in tqdm(enumerate(frames.frame_num.values),desc = "Exporting labeling dataset:",total = len(frames)):
            im_name = 'im_{0:06d}_session{2}_frame{1:06d}'.format(i,f,frames.session_name.iloc[i])
            for bpart in bodyparts:
                t = (PoseEstimationLabelSet.Label & dict(
                    pose_label_set_num = k['pose_label_set_num'],
                    frame_num = f,
                    label_name = bpart)).fetch()
                x = np.nan
                y = np.nan
                if disperse_labels:
                    if i == 0:
                        x = i*20
                        y = 100
                if len(t):
                    x = t['x'][0]
                    y = t['y'][0]
                todlc.append(dict(scorer = labeler,
                                bodyparts = bpart,
                                level_0 = 'labeled-data',
                                level_1 = f'label_set_{k["pose_label_set_num"]}',
                                level_2 = f'{im_name}.png',
                                x = x,
                                y = y))
            fname = data_path/f'{im_name}.png'
            if not fname.exists():
                imsave(fname,frames.iloc[i].frame)
        df = pd.DataFrame(todlc)
        df = df.set_index(["scorer", "bodyparts","level_0","level_1","level_2"]).stack()
        df.index.set_names("coords", level=-1, inplace=True)
        df = df.unstack(["scorer", "bodyparts", "coords"])
        df.index.name = None
        df.to_hdf(data_path/f'CollectedData_{labeler}.h5',key='keypoints')
        return data_path,frames,frame_labels

    def update_labeling(self, labeling_file):
        '''
        (PoseEstimationLabelSet() & 'pose_label_set_num =3').update_labeling('filename.h5')

        Updates the labels in the PoseEstimationLabelSet from a file.
        Currently only DLC format is supported.

        Reach out if you need other formats.
         Joao Couto 2023
        '''
        dlcres = pd.read_hdf(labeling_file)
        scorer = np.unique(dlcres.columns.get_level_values(0))[0]
        bodyparts = np.unique(dlcres.columns.get_level_values(1))
        frame_nums = [int(f.split('frame')[-1].strip('.png')) 
                    for f in dlcres.reset_index()['level_2'].values]
        frame_names = dlcres.reset_index()['level_2'].values
        labels = []
        from tqdm import tqdm
        labels_to_insert = [] # insert the labels in parallel will be faster.
        labels_to_delete = [] # need to delete all labels for a frame before adding the new ones
        for iframe,frame_name in tqdm(enumerate(frame_names),desc = 'Updating labels',total = len(frame_names)):
            frame_num = int(frame_name.split('frame')[-1].strip('.png'))
            frame_key = dict(frame_num = frame_num)
            if 'session' in frame_name: # get the session name so there are no conflicting frame numbers
                 frame_key['session_name'] = frame_name.split('session')[-1].split('_frame')[0]
            frame_key = (PoseEstimationLabelSet.Frame() & self.proj().fetch1() & frame_key).proj().fetch1()
            labels_to_delete.extend((PoseEstimationLabelSet.Label() & frame_key).proj().fetch(as_dict = True))
            for dlcname in bodyparts:
                if np.isnan(dlcres[scorer][dlcname].iloc[iframe]['x']):
                    continue # if it is NaN, don't add
                if dlcres[scorer][dlcname].iloc[iframe]['x'] == 0 and dlcres[scorer][dlcname].iloc[iframe]['y'] == 0:
                    continue # if the label is at 0,0  don't add
                label = dict(dict(frame_key,label_name = dlcname),
                            label_name = dlcname,
                            x = dlcres[scorer][dlcname].iloc[iframe]['x'],
                            y = dlcres[scorer][dlcname].iloc[iframe]['y'])
                labels_to_insert.append(label)
        (PoseEstimationLabelSet.Label() & labels_to_delete).delete(force = True) # ask the user to confirm
        PoseEstimationLabelSet.Label.insert(labels_to_insert)
                    

@analysisschema
class PoseEstimationModel(dj.Manual):
    definition = '''
    model_num                : int
    ---
    algorithm_name           : varchar(24)    # Algorithm for pose estimation
    -> [nullable] AnalysisFile                # zipped model; no videos.
    -> [nullable] PoseEstimationLabelSet 
    parameters_dict = NULL   : varchar(2000)  # parameters json formatted dictionary
    training_datetime = NULL : datetime
    container_name = NULL    : varchar(64)    # Name of the container to use
    code_link = NULL         : varchar(300)   # link to the github of the algorithm
    '''
    
    def insert_model(self, model_num, 
                     model_folder=None,
                     pose_label_set_num = None,
                     algorithm_name = None,
                     parameters = None,
                     training_datetime=None,
                     container_name = None,
                     code_link = None):    
        import shutil
        if training_datetime is None:
            today = datetime.now()
        else:
            today = training_datetime
        dataset_name = datetime.strftime(today,'%Y%m%d_%H%M%S')

        # check if this model_number exists for another pose_label_set_num
        allmodels = pd.DataFrame(PoseEstimationModel.fetch())
        sel = allmodels[(allmodels.model_num.values == model_num) & (allmodels.pose_label_set_num.values != pose_label_set_num)]
        if len(sel):
            model_num = np.max(allmodels.model_num.values)+1
                    
        if model_folder is None:
            model_folder = ((Path(prefs['local_paths'][0])/'pose_estimation_models')/f'{dataset_name}')/f'model_{model_num}'
        filepath = ((Path(prefs['local_paths'][0])/'pose_estimation_models')/f'{dataset_name}')/f'model_{model_num}'
        print(f'Creating archive {filepath}')
        shutil.make_archive(filepath, 'zip', model_folder)
        filepath = filepath.with_suffix('.zip')

        key = AnalysisFile().upload_files([filepath],dataset = dict(subject_name = 'pose_estimation_models',
                                                                  session_name = f'model_{model_num}',
                                                                  dataset_name = dataset_name))
        key = dict((AnalysisFile & key).proj().fetch1(),
                          model_num = model_num,
                          algorithm_name = algorithm_name,
                          training_datetime = today,
                          pose_label_set_num = pose_label_set_num,
                          parameters_dict = json.dumps(parameters) if not parameters is None else None,
                          container_name = container_name,
                          code_link = code_link)
        if not len(PoseEstimationModel & f'model_num = {model_num}'):
            self.insert1(key)
        else:
            print(f'Model {model_num} already exists. Updating but keeping last version in AWS.')        
            oldentry = (PoseEstimationModel & f'model_num = {model_num}').fetch1()
            for k in key.keys():
                if key[k] is None:
                    key[k] = oldentry[k]
            self.update1(key)
        # need to add a model evaluation part table here
    def get_model(self):
        filepath = (AnalysisFile & self).get()
        
        filepath = filepath[0]
        if not (filepath.parent/'config.yaml').exists():
            import shutil 
            shutil.unpack_archive(filepath,extract_dir = filepath.parent)
        return filepath.parent/'config.yaml' # return the path to the config file.
        
@analysisschema
class PoseEstimation(dj.Manual):
    definition = '''
    -> PoseEstimationModel
    -> DatasetVideo
    label_name : varchar(54)
    ---
    x                 : longblob
    y                 : longblob
    z = NULL          : longblob
    likelihood = NULL : longblob
    '''
