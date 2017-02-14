import chardet
import os
import sys
import re
import logging
from sharedsrc.file_watch import FileWatch

class ConfHelper(object):
    '''
    A little helper which allos reading the 
    config files. The config files may be cached for
    faster access.
    '''
    def __init__(self, update=True, autoupdate=True):
        '''
        :param update: Initialy read all configs. Set this to false when you don't need all of them.
        :param autoupdate: Update cache on changes. This is triggered after initially updating the files.
        '''
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.xposed_cfg=[]
        self.arkgus=[]
        self.fw = None
        if autoupdate==True:
            self.fw = FileWatch()
            self.fw.startWatching()
        if update==True:
            self.updateCfg()
            self.updateARKGus()


    def updateCfg(self):
        '''
        Cache the xposed.cfg
        '''
        self.l.info("Caching xposed.cfg")
        configpath = os.path.join(os.path.dirname(sys.argv[0]),"xposed.cfg")
        if self.fw:
            self.fw.registerObserver(filepath=configpath, interval=1, callback=self.updateCfg, unique=True, gone=None)
        try:
            with open(configpath, "r") as f:
                self.xposed_cfg=f.readlines()
        except Exception as e:
            e.print_stack_trace()
            self.xposed_cfg=[]
    
    
    def updateARKGus(self):
        '''
        Cache GameUserSettings.ini
        '''
        self.l.info("Caching GameUserSettings.ini")
        arkdir=self.readCfg("ARKDIR");
        guspath=os.path.join(arkdir, "ShooterGame/Saved/Config/LinuxServer/GameUserSettings.ini")
        if self.fw:
            self.fw.registerObserver(filepath=guspath, interval=1, callback=self.updateARKGus, unique=True, gone=None)
        try:
            enc=""
            with open(guspath, "rb") as gus:
                enc = chardet.detect(gus.read()).get("encoding")
                if enc == "windows-1252":
                    enc = "cp1252"
            with open(guspath, encoding=enc) as gus:        
                self.arkgus=gus.readlines()
        except Exception as e:
            e.print_stack_trace()
            self.arkgus=[]
        
    def readCfg(self, setting):
        '''
        Read setting from cache
        :param setting:
        '''
        for l in self.xposed_cfg:
            matches = re.search("^\s*"+setting+"\s*\=\s*(.+)$",l)
            if matches:
                return matches.group(1)
        return None
    
    def readGUSCfg(self, setting, filterPW=False):
        '''
        Read setting from cache
        :param setting:
        '''
        if filterPW and "password" in setting.lower():
            return None
        for l in self.arkgus:
            matches = re.search("^\s*"+setting+"\s*\=\s*(.+)$",l)
            if matches:
                return matches.group(1)
        return None
    
    def readGUSCfgDict(self,filterPW=True):
        '''
        Reads the whole cfg and returns a dict
        :param filterPW: default true
        '''
        dict={}
        for l in self.arkgus:
            matches = re.search("^\s*([a-zA-Z0-9]+)\s*\=\s*(.+)$",l.strip())
            if matches and len(matches.groups()) == 2:
                if filterPW :
                    if not "password" in matches.group(1).lower():
                        dict.update({matches.group(1):matches.group(2)})
                else:
                    dict.update({matches.group(1):matches.group(2)})
        return dict
    
    def readGUSCfgPlain(self,filterPW=True):
        '''
        Reads the whole cfg as is
        :param filterPW: default true
        '''
        out=""
        for l in self.arkgus:
            add=l
            if filterPW:
                matches = re.search("^\s*([a-zA-Z0-9]+)\s*\=\s*(.+)$",l.strip())
                if matches and len(matches.groups()) > 1 and "password" in matches.group(1).lower():
                    add=""
            out+=add
        return out