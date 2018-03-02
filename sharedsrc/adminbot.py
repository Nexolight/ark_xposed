from sharedsrc.logger import ADMINBOT_LOG
import logging.config
logging.config.dictConfig(ADMINBOT_LOG)
from sharedsrc.cmd_helper import CMD
import re
import os
from sharedsrc.conf_helper import ConfHelper
from sharedsrc.playerdb_helper import Player
from sharedsrc.chatline import Chatline
cfgh = ConfHelper(update=True, autoupdate=True)

class Adminbot(object):
    '''
    Just the main class
    '''

    def __init__(self,mcrconpath):
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.info("Initialized ARK adminbot tool")
        self.mcrconpath=mcrconpath
        self.cmd = CMD()
        
    def react(self,chatlineObj,playerObj,callback=None):
        '''
        Parses a given chatmessage and reacts with an rcon command
        depending on the settings. Then it calls the callback function.
        '''
        try:
            command=self.parseAndGet(playerObj,chatlineObj)
            if(command):
                output = self.cmd.proc(
                    args=[
                        self.mcrconpath, "-c",
                        "-H", "127.0.0.1",
                        "-P", chatlineObj.port,
                        "-p", cfgh.readGUSCfg("ServerAdminPassword"),
                        command
                    ]
                )
                if output[1]:
                    self.l.warn("Adminbot command failed!")
                    self.l.error(output[1])
                if output[0]:
                    pass
        finally:
            if(callback):
                callback()
            
    def parseAndGet(self,playerObj,chatlineObj):
        '''
        Compares the given chatmsg with the settings
        and returns the appropriate rcon command
        '''
        callmsg=cfgh.readCfg("CHATBOT_CALL_MSG")
        if(not callmsg in chatlineObj.msg):
            return None
        self.l.debug("process with adminbot:"+chatlineObj.msg)
        resp=""
        if(int(cfgh.readCfg("CHATBOT_FNC_HELP")) == 1):#help enabled
            if(cfgh.readCfg("CHATBOT_FNC_HELP_MSG") in chatlineObj.msg):#help command
                self.l.info("Return help")
                resp="ServerChatTo \""+playerObj.steamid+"\n"
                resp+=self.getDesc("CHATBOT_FNC_HELP")
                if(int(cfgh.readCfg("CHATBOT_FNC_SUICIDE")) == 1):#suicide command
                    resp+=self.getDesc("CHATBOT_FNC_SUICIDE")
                #TODO: more
                return resp
        if(int(cfgh.readCfg("CHATBOT_FNC_SUICIDE")) == 1):#suicide enabled
            if(cfgh.readCfg("CHATBOT_FNC_SUICIDE_MSG") in chatlineObj.msg):
                playerID=self.getPlayerID(playerObj.steamid,chatlineObj.port)
                if(playerID):
                    return "KillPlayer "+playerID
            
    def getPlayerID(self,steamid64,port):
        '''
        returns the player id by calculating the steamid32 from the steamid64 and using the
        rcon command
        '''
        steamid32 = Player.getSteamID32(steamid64)
        output = self.cmd.proc(
            args=[
                self.mcrconpath, "-c",
                "-H", "127.0.0.1",
                "-P", port,
                "-p", cfgh.readGUSCfg("ServerAdminPassword"),
                "GetPlayerIDForSteamID "+steamid32
            ]
        )
        if output[1]:
            self.l.warn("Could not get steamid32 for "+steamid64+"!")
            self.l.error(output[1])
        if output[0]:
            pidsearch = re.search('.*PlayerID\:\s*([0-9]+).*',output[0])
            return str(pidsearch.group(1))
        return None
            
    def getDesc(self,bCfgName):
            return cfgh.readCfg("CHATBOT_CALL_MSG")+" "+cfgh.readCfg(bCfgName+"_MSG")+" : "+cfgh.readCfg(bCfgName+"_DESC")+"\n"
            
            
            
            
            
            
            
            
            
            
            
        