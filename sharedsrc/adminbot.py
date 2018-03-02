#!/usr/bin/python3
# -*- coding: utf-8 -*-
from sharedsrc.logger import ADMINBOT_LOG
import logging.config
logging.config.dictConfig(ADMINBOT_LOG)
from sharedsrc.cmd_helper import CMD
import re
import os
from sharedsrc.conf_helper import ConfHelper
cfgh = ConfHelper(update=True, autoupdate=True)

class Adminbot(object):
    '''
    Just the main class
    '''

    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.info("Initialized ARK adminbot tool")
        self.cmd = CMD()
        
    def react(self,port,steamid,chatmsg,callaback=None):
        '''
        Parses a given chatmessage and reacts with an rcon command
        depending on the settings. Then it calls the callback function.
        '''
        try:
            command=self.parseAndGet(steamid,chatmsg)
            if(command):
                output = self.cmd.proc(
                    args=[
                        os.path.join(self.spath, "thirdparty/mcrcon"), "-c",
                        "-H", "127.0.0.1",
                        "-P", port,
                        "-p", cfgh.readGUSCfg("ServerAdminPassword"),
                        
                    ]
                )
                if output[1]:
                    self.l.warn("Adminbot command failed!")
                    self.l.error(output[1])
                if output[0]:
                    pass
        finally:
            callback()
            
    def parseAndGet(self,steamid,chatmsg):
        '''
        Compares the given chatmsg with the settings
        and returns the appropriate rcon command
        '''
        callmsg=cfgh.readCfg("CHATBOT_CALL_MSG")
        if(not callmsg in chatmsg):
            return None
        resp=""
        if(int(cfgh.readCfg("CHATBOT_FNC_HELP")) == 1):#help enabled
            if(cfgh.readCfg("CHATBOT_FNC_MSG") in chatmsg):#help command
                resp="ServerChatTo "+steamid+"\n"
                resp+=getDesc("CHATBOT_FNC_HELP")
                if(int(cfgh.readCfg("CHATBOT_FNC_UNSTUCK")) == 1):#unstuck command
                    resp+=getDesc("CHATBOT_FNC_UNSTUCK")
                #TODO:more to come
                return resp
            
    def getDesc(self,bCfgName):
            return cfgh.readCfg("CHATBOT_CALL_MSG")+" "+cfgh.readCfg(bCfgName+"_MSG")+" : "+cfgh.readCfg(bCfgName+"_DESC")+"\n"
            
            
            
            
            
            
            
            
            
            
            
        