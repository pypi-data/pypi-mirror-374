from PyQt5.QtWidgets import (QApplication,
                             QTableWidget,
                             QTableWidgetItem,
                             QWidget,
                             QMainWindow,
                             QDockWidget,
                             QFormLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QVBoxLayout,
                             QPushButton,
                             QGroupBox,
                             QGridLayout,
                             QTreeWidgetItem,
                             QTreeView,
                             QTextEdit,
                             QPlainTextEdit,
                             QLineEdit,
                             QScrollArea,
                             QCheckBox,
                             QComboBox,
                             QListWidget,
                             QLabel,
                             QProgressBar,
                             QFileDialog,
                             QMessageBox,
                             QDesktopWidget,
                             QListWidgetItem,
                             QFileSystemModel,
                             QAbstractItemView,
                             QTabWidget,
                             QMenu,
                             QDialog,
                             QDialogButtonBox,
                             QAction)

from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItem, QStandardItemModel,QColor
from PyQt5.QtCore import Qt, QTimer,QMimeData
GUI_UPDATE = QApplication.processEvents

from .utils import *

class ServerCopyWidget(QMainWindow):
    def __init__(self, 
                 src_filepaths, 
                 name = None,
                 upload_rule = None,
                 local_path = None,
                 server_path = None,
                 upload_storage = None,
                 subject_name = None, 
                 session_name = None,
                 dataset_name = None,
                 parse_filename = True,
                 overwrite = True,
                 user_confirmation = True,
                 **kwargs):
        '''Function to copy data and show progress.
        To run in a separate process 
        '''
        super(ServerCopyWidget,self).__init__()
        from pathlib import Path
        from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QStyle
        
        name = f'[labdata] server copy {name}'
        self.setWindowTitle(f'{name}')
        icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        self.setWindowIcon(icon)

        doneicon = self.style().standardIcon(QStyle.SP_DialogApplyButton)
        notyeticon = self.style().standardIcon(QStyle.SP_DialogCancelButton)
        workingonit = self.style().standardIcon(QStyle.SP_ArrowForward)
        
        from .schema import UploadJob,Setup,Subject,Session,Dataset,dj
        if local_path is None:  # get the local_path from the preferences
            if not 'local_paths' in prefs.keys():
                raise OSError('Local data path [local_paths] not specified in the preference file.')
            local_path = Path(prefs['local_paths'][0])
        if server_path is None: # get the upload_path from the preferences
            if not 'upload_path' in prefs.keys():
                raise OSError('Upload storage [upload_path], not specified in the  preference file.') 
            server_path = prefs['upload_path']
        if server_path is None:
            server_path = local_path
        if upload_storage is None: # get the upload_storage name from the preferences
            if not 'upload_storage' in prefs.keys():
                raise OSError('Upload storage [upload_storage], not specified in the  preference file.')    
            upload_storage = prefs['upload_storage']
        if not type(src_filepaths) is list: # Check if the filepaths are in a list
            raise ValueError('Input filepaths must be a list of paths.')
        # replace local_path if the user passed it like that by accident.
        src_filepaths = [str(Path(f).resolve()).replace(str(local_path),'') for f in src_filepaths]
        # remove trailing / or \
        src_filepaths = [f if not f.startswith(pathlib.os.sep) else f[1:] for f in src_filepaths]
        # make unique
        src_filepaths = [f for f in np.unique(src_filepaths)]
        
        from .copy import any_path_uploaded
        replace = False
        if not upload_rule is None:
            if 'replace' in upload_rule:
                replace = True
        if any_path_uploaded(src_filepaths) and not replace:
            msgBox = QMessageBox( icon=QMessageBox.Critical)
            msgBox.setWindowTitle("Data copy: files already copied?")
            msgBox.setText('At least one of the selected paths was already uploaded {0}'.format(
            Path(src_filepaths[0]).parent))
            msgBox.exec_()
            raise(OSError('At least one of the selected paths was already uploaded {0}'.format(
                Path(src_filepaths[0]).parent)))
        
        args = dict(**kwargs)
        args['subject_name'] = subject_name
        args['session_name'] = session_name
        args['dataset_name'] = dataset_name
        if parse_filename: # parse filename based on the path rules
            tmp = parse_filepath_parts(src_filepaths[0])
            for k in tmp.keys():
                args[k] = tmp[k]        

        for src in src_filepaths:
            src = Path(local_path)/src
            if not src.exists():
                msgBox = QMessageBox( icon=QMessageBox.Critical)
                msgBox.setWindowTitle("Data copy: source does not exist!")
                msgBox.setText("File {0} does not exist?".format(src))
                msgBox.exec_()
                raise(OSError(f"{tcolor['r']('Upload failed')} {src} does not exist."))
        # Add it to the upload table
        filelist = QListWidget()
        self.files_to_copy = [Path(f) for f in src_filepaths]
        file_items = []
        itemnames = []
        for i,f in  enumerate(self.files_to_copy):
            itemnames.append(str(f.name))
            file_items.append(QListWidgetItem(notyeticon,itemnames[-1]))
            # file_items[-1].setIcon(workingonit)
            filelist.addItem(file_items[-1])
        if user_confirmation:
            msgBox = QMessageBox(icon = QMessageBox.Information)
            msgBox.setWindowTitle("[labdata] user input required")
            msgBox.setText(f"Copying {len(self.files_to_copy)} files to the server for upload to {upload_storage} storage.")
            msgBox.setInformativeText("Do you want to continue?")
            msgBox.setStandardButtons( QMessageBox.Cancel | QMessageBox.Ok );
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)
            res = msgBox.exec_()
            if res == QMessageBox.Cancel:
                print(tcolor['r']("User CANCELED the server upload."))
                return
        # copy and compute checksum for all paths in parallel.
        from .copy import _copyfile_to_upload_server
        res = Parallel(n_jobs = DEFAULT_N_JOBS,
                       return_as = 'generator_unordered')(delayed(_copyfile_to_upload_server)(
                           path,
                           local_path = local_path,
                           server_path = server_path,
                           overwrite = overwrite) for path in src_filepaths)
        layout = QVBoxLayout(self)
        # self.setLayout(layout)
        layout.addWidget(filelist)
        self.setCentralWidget(filelist)
        # now dow the actual copy
        self.show()
        GUI_UPDATE()
        # does the checksum and copy
        completed = []
        for i,src in enumerate(res):
            GUI_UPDATE()
            item = file_items[itemnames.index(src['src_path'].split('/')[-1])]
            item.setIcon(doneicon)
            completed.append(src)
            GUI_UPDATE()
        # Add it to the upload table
        # check the job id
        with dj.conn().transaction:
            if "setup_name" in args.keys():
                Setup.insert1(args, skip_duplicates = True,ignore_extra_fields = True) # try to insert setup
            if "dataset_name" in args.keys() and "session_name" in args.keys() and "subject_name" in args.keys():
                if not len(Subject() & dict(subject_name=args['subject_name'])):
                    # subject not on the database..
                    msgBox = QMessageBox(icon = QMessageBox.Information)
                    msgBox.setWindowTitle("[labdata] user input required")
                    msgBox.setText(f"Subject {args['subject_name']} was not on the database. ")
                    msgBox.setInformativeText("You can add the subject now or skip associating the session with a Dataset. Did you add the subject?")
                    msgBox.setStandardButtons( QMessageBox.No | QMessageBox.Yes );
                    msgBox.setDefaultButton(QMessageBox.No)
                    msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)
                    #print(args)
                    res = msgBox.exec_()
                    if res == QMessageBox.No:
                        print(tcolor['r']("User selected not to add the Dataset but files are still uploaded."))
                        args = dict()  
                # Subject.insert1(args, skip_duplicates = True,ignore_extra_fields = True) # try to insert subject, needs date of birth and sex
                if not len(Session() & dict(subject_name=args['subject_name'],
                                            session_name = args['session_name'])):
                    Session.insert1(args, skip_duplicates = True,ignore_extra_fields = True) # try to insert session
                if not len(Dataset() & dict(subject_name = args['subject_name'],
                                            session_name = args['session_name'],
                                            dataset_name = args['dataset_name'])):
                    Dataset.insert1(args, skip_duplicates = True,ignore_extra_fields = True) # try to insert dataset
            jobid = UploadJob().fetch('job_id')
            if len(jobid):
                jobid = np.max(jobid) + 1
            else:
                jobid = 1
            jb = dict(job_id = jobid, 
                      job_status = "ON SERVER",
                      upload_storage = upload_storage,
                      job_rule = upload_rule,
                      **args)
            if 'upload_host' in prefs.keys():
                if not 'job_host' in jb.keys():
                    jb['job_host'] = prefs['upload_host']
            UploadJob.insert1(jb,
                              ignore_extra_fields = True) # Need to insert the dataset first if not there
            res = [dict(r, job_id = jobid) for r in completed] # add dataset through kwargs
            UploadJob.AssignedFiles.insert(res, ignore_extra_fields=True)
        import time
        # show it for some time
        for t in range(60):
            time.sleep(0.15)
            GUI_UPDATE()
        print(f"{tcolor['g']('Upload:')} {completed}")
        return 

def build_tree(item,parent):
    for k in item.keys():
        child = QStandardItem(k)
        child.setFlags(child.flags() |
                       Qt.ItemIsSelectable |
                       Qt.ItemIsEnabled)
        child.setEditable(False)
        if type(item[k]) is dict:
            build_tree(item[k],child)
        parent.appendRow(child)

def make_tree(item, tree):
    if len(item) == 1:
        if not item[0] == '':
            tree[item[0]] = item[0]
    else:
        head, tail = item[0], item[1:]
        tree.setdefault(head, {})
        make_tree(
            tail,
            tree[head])
class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
                return str(self._data.index[section])

class TableView(QTreeView):
    def __init__(self, *args):
        QTreeView.__init__(self, *args)
        self.header = ['folder','n_files','subject_name','session_name','dataset_name']
        self.setHorizontalHeaderLabels(self.header)

    def setData(self,data):
        self.data = data
        model = TableModel(pd.DataFrame(data))
        
        self.setModel(model)
        # for i,item in enumerate(self.data):
        #     for j,k in enumerate(self.header):
        #         newitem = QTableWidgetItem(item[k])
        #         self.insertRow(i+1)
        #         self.setItem(i, j, newitem)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

def get_tree_path(items,root = ''):
    ''' Get the paths from a QTreeView item'''
    paths = []
    for item in items:
        level = 0
        index = item
        paths.append([index.data()])
        while index.parent().isValid():
            index = index.parent()
            level += 1
            paths[-1].append(index.data())
        for i,p in enumerate(paths[-1]):
            if p is None :
                paths[-1][i] = ''
        paths[-1] = '/'.join(paths[-1][::-1])
    return paths

class FileView(QTreeView):
    def __init__(self,prefs,parent=None):
        super(FileView,self).__init__()
        self.prefs = prefs
        self.parent = parent
        rootfolder = self.prefs['local_paths'][0]
        self.fs_model = QFileSystemModel(self)
        self.fs_model.setReadOnly(True)
        self.setModel(self.fs_model)
        self.folder = rootfolder
        self.setRootIndex(self.fs_model.setRootPath(rootfolder))
        self.fs_model.removeColumn(1)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(3)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)
        [self.hideColumn(i) for i in range(1,4)]
        self.setColumnWidth(0,int(self.width()*.4))
        def pathnofolder(p):
            return str(p).replace(rootfolder,'').strip(pathlib.os.sep)
        def handle_click(val):
            path = Path(get_tree_path([val])[0])
            allfiles = list(filter(lambda x: x.is_file(),path.rglob('*')))
            allfolders = np.unique(list(map(lambda x: x.parent,allfiles)))
            to_upload = []
            for f in allfolders:
                f = str(f)
                files = list(filter(lambda x: str(f) in str(x),list(allfiles)))
                header = ['folder','n_files','subject_name','session_name','dataset_name','rule','paths']
                ff = pathnofolder(f)                
                t = dict(folder = ff,
                         files = [pathnofolder(p) for p in files],
                         paths = files,
                         subject_name = None,
                         session_name = None,
                         dataset_name = None,
                         rule = None,
                         n_files = len(files))
                to_upload.append(t)
            self.parent.table.setData(to_upload)
            
            # put this in the other side.
        self.clicked.connect(handle_click)
        
class LABDATA_PUT(QMainWindow):
    def __init__(self, preferences = None):
        super(LABDATA_PUT,self).__init__()
        self.setWindowTitle('labdata')
        self.prefs = preferences
        if self.prefs is None:
            self.prefs = prefs
        mainw = QWidget()
        self.setCentralWidget(mainw)
        lay = QHBoxLayout()
        mainw.setLayout(lay)
        # Add the main file view
        self.table = TableView()
        self.fs_view = FileView(self.prefs,parent=self)
        lay.addWidget(self.fs_view)

        w = QGroupBox('Database ingestion')
        
        l = QFormLayout()
        w.setLayout(l)
        # self.skip_database = False
        # skipwidget = QCheckBox()
        # skipwidget.setChecked(self.skip_database)
        # def _skipwidget(value):
        #     self.skip_database = value>0
        # skipwidget.stateChanged.connect(_skipwidget)
        # l.addRow(skipwidget,QLabel('Files only'))
        l.addRow(self.table)
        lay.addWidget(w)
        self.show()

class FilesystemView(QTreeView):
    def __init__(self,folder,parent=None):
        super(FilesystemView,self).__init__()
        self.parent = parent
        self.fs_model = QFileSystemModel(self)
        self.fs_model.setReadOnly(True)
        self.setModel(self.fs_model)
        self.folder = folder
        self.setRootIndex(self.fs_model.setRootPath(folder))
        #self.fs_model.removeColumn(1)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(3)
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        #self.setDragDropMode(QAbstractItemView.DragDrop)
        #self.setDropIndicatorShown(True)
        self.setColumnWidth(0,int(self.width()*.7))
        self.expandAll()
    def change_root(self):
        folder = QFileDialog().getExistingDirectory(self,"Select directory",os.path.curdir)
        self.setRootIndex(self.fs_model.setRootPath(folder))
        self.expandAll()
        self.folder = folder
        if hasattr(self.parent,'folder'):
            self.parent.folder.setText('{0}'.format(folder))
