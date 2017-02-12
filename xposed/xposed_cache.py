from xposed import cfgh,l


class FileCache(object):
    '''
    An instance of this class is supposed to be
    the central access point when it comes to read
    data from a file. 
    
    It is supposed to hold this data in ram 
    and update it whenever the underlying file changes
    '''
    
    cache = {}
    
    def __init__(self):
        pass
    
    def enableCaching(self, filepath, autoupdate=True, postprocess=None):
        pass
    
    def disableCaching(self, filepath):
        pass
    
    def readFile(self, filepath):
        pass
    
    