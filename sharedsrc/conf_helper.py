import chardet
import os
import sys
import re
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-11s %(message)s")

class ConfHelper(object):
    def __init__(self, update=True):
        self.l = logging.getLogger(self.__class__.__name__)
        self.xposed_cfg=[]
        self.arkgus=[]
        if update==True:
            self.updateCfg()
            self.updateARKGus()

    def updateCfg(self):
        '''
        Cache the xposed.cfg
        '''
        self.l.info("Caching xposed.cfg")
        configpath = os.path.join(os.path.dirname(sys.argv[0]),"xposed.cfg")
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