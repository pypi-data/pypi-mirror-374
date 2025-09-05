from ..utils import *
# some functions used in the schema imports

__all__ = ['read_camlog']

def read_camlog(log):
    '''
    Adapted from github.com/jcouto/labcams 
    '''
    
    logheaderkey = '# Log header:'
    comments = []
    with open(log,'r',encoding = 'utf-8') as fd:
        for line in fd:
            if line.startswith('#'):
                line = line.strip('\n').strip('\r')
                comments.append(line)
                if line.startswith(logheaderkey):
                    columns = line.strip(logheaderkey).strip(' ').split(',')
    camlog = pd.read_csv(log, delimiter = ',',
                         header = None,
                         comment = '#',
                         engine = 'c')
    return comments,camlog

