from sharedsrc.logger import ADMINBOT_LOG
import logging.config
logging.config.dictConfig(ADMINBOT_LOG)
from sharedsrc.cmd_helper import CMD
import re
import threading
import os
import random
import json
from urllib.request import urlopen, Request
from sharedsrc.conf_helper import ConfHelper
from sharedsrc.playerdb_helper import Player
from sharedsrc.chatline import Chatline
import time
cfgh = ConfHelper(update=True, autoupdate=True)


class Vote(object):
    def __init__(self,key,user,time,agree=True):
        self.user=user
        self.key=key
        self.time=time
        self.agree=agree
        
class VoteTimer(threading.Thread):
    def __init__(self,seconds,voteendfnc,votekey):
        super(VoteTimer, self).__init__()
        self.seconds = seconds
        self.voteendfnc = voteendfnc
        self.votekey = votekey
    
    def run(self):
        while self.seconds > 0:
            time.sleep(1)
            self.seconds -= 1
        self.voteendfnc(self.votekey)

class Adminbot(object):
    '''
    Just the main class
    '''

    def __init__(self,mcrconpath,pdbh):
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.info("Initialized ARK adminbot tool")
        self.mcrconpath=mcrconpath
        self.cmd = CMD()
        self.votes = {}
        self.pdbh = pdbh
        self.webheader = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        
        
    def reactRaw(self, command, port):
        if(command):
            self.l.info("Execute command: "+str(command))
            output = self.cmd.proc(
                args=[
                    self.mcrconpath, "-c",
                    "-H", "127.0.0.1",
                    "-P", port,
                    "-p", cfgh.readGUSCfg("ServerAdminPassword"),
                    command
                ]
            )
            if output[1]:
                    self.l.warn("Adminbot command failed!")
                    self.l.error(output[1])
            if output[0]:
                pass
        
    def react(self,chatlineObj,playerObj,callback=None):
        '''
        Parses a given chatmessage and reacts with an rcon command
        depending on the settings. Then it calls the callback function.
        '''
        try:
            command=self.parseAndGet(playerObj,chatlineObj)
            self.reactRaw(command,chatlineObj.port)
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
                resp="ServerChatTo \""+playerObj.steamid+"\"\n"
                resp+=self.getDesc("CHATBOT_FNC_HELP")+"\n"
                if(int(cfgh.readCfg("CHATBOT_FNC_SUICIDE")) == 1):#suicide command
                    resp+=self.getDesc("CHATBOT_FNC_SUICIDE")
                if(int(cfgh.readCfg("CHATBOT_FNC_MKDAY")) == 1):#day command
                    resp+=self.getDesc("CHATBOT_FNC_MKDAY")
                if(int(cfgh.readCfg("CHATBOT_FNC_MKNIGHT")) == 1):#night command
                    resp+=self.getDesc("CHATBOT_FNC_MKNIGHT")
                if(int(cfgh.readCfg("CHATBOT_FNC_SHUTDOWN")) == 1):#shutdown command
                    resp+=self.getDesc("CHATBOT_FNC_SHUTDOWN")
                if(int(cfgh.readCfg("CHATBOT_FNC_ARKSERVERSNET_VOTE")) == 1):#arkservesnet vote claim command
                    resp+=self.getDesc("CHATBOT_FNC_ARKSERVERSNET_VOTE")
                #TODO: more
                return resp
        if(int(cfgh.readCfg("CHATBOT_FNC_SUICIDE")) == 1):#suicide enabled
            if(cfgh.readCfg("CHATBOT_FNC_SUICIDE_MSG") in chatlineObj.msg):
                playerID=str(self.pdbh.getSvgPlayerID(playerObj.steamid))
                if(playerID):
                    return "KillPlayer \""+playerID+"\""
                
        if(int(cfgh.readCfg("CHATBOT_FNC_MKDAY")) == 1):#day enabled
            if(cfgh.readCfg("CHATBOT_FNC_MKDAY_MSG") in chatlineObj.msg):
                self.letsVote("CHATBOT_FNC_MKDAY",chatlineObj,"settimeofday 08:00:00")
                
        if(int(cfgh.readCfg("CHATBOT_FNC_MKNIGHT")) == 1):#night enabled
            if(cfgh.readCfg("CHATBOT_FNC_MKNIGHT_MSG") in chatlineObj.msg):
                self.letsVote("CHATBOT_FNC_MKNIGHT",chatlineObj,"settimeofday 22:00:00")
                
        if(int(cfgh.readCfg("CHATBOT_FNC_SHUTDOWN")) == 1):#shutdown enabled
            if(cfgh.readCfg("CHATBOT_FNC_SHUTDOWN_MSG") in chatlineObj.msg):
                self.letsVote("CHATBOT_FNC_SHUTDOWN",chatlineObj,[
                    "ServerChat Saving world - Shutdown in 30s",
                    "SaveWorld",
                    30,
                    "ServerChat world saved - exit now!",
                    5,
                    "DoExit"])
                
        if(int(cfgh.readCfg("CHATBOT_FNC_ARKSERVERSNET_VOTE")) == 1):#night enabled
            if(cfgh.readCfg("CHATBOT_FNC_ARKSERVERSNET_VOTE_MSG") in chatlineObj.msg):
                self.claimASNVote(chatlineObj,playerObj)
            
    def claimASNVote(self,chatlineObj,playerObj):
        apikeys = json.loads(cfgh.readCfg("CHATBOT_FNC_ARKSERVERSNET_VOTE_SRVKEYS"))
        playerID=self.pdbh.getSvgPlayerID(playerObj.steamid)
        reward = json.loads(cfgh.readCfg("CHATBOT_FNC_ARKSERVERSNET_VOTE_REWARD"))
        rng = int(cfgh.readCfg("CHATBOT_FNC_ARKSERVERSNET_VOTE_RNG"))
        rngItems = int(cfgh.readCfg("CHATBOT_FNC_ARKSERVERSNET_VOTE_RNG_ITEMS"))
        apiurl = cfgh.readCfg("CHATBOT_FNC_ARKSERVERSNET_VOTE_APIURL")
        once=True
        for apikey in apikeys:
            
            url = apiurl
            url += "object=votes&element=claim"
            url += "&key="+str(apikey)
            url += "&steamid="+str(playerObj.steamid)
            
            #check unclaimed vote            
            rq = Request(url,headers=self.webheader)
            voted = urlopen(rq).read()
            if once:
                voted = "1"
                once=False
            
            urlACK = apiurl
            urlACK += "action=post&object=votes&element=claim"
            urlACK += "&key="+str(apikey)
            urlACK += "&steamid="+str(playerObj.steamid)
            
            
            if len(voted) == 1 and int(voted) == 1:
                try:
                    self.reactRaw("ServerChatTo \""+str(playerObj.steamid)+"\" Granting reward for Server with API key: "+str(apikey),chatlineObj.port)
                    finalReward = []
                    if(rng > 0): #pick a random reward
                        for x in range(rngItems): #pick x random rewards
                            randomReward = random.choice(reward)
                            for repeat in range(int(item.get("repeat"))):#item amounts are capped - repeat n times
                                finalReward.append(
                                    str("\""+randomReward.get("item"))+"\" "+
                                    str(randomReward.get("amount"))+" "+
                                    str(randomReward.get("quality"))+" "+
                                    str(randomReward.get("fBP"))
                                )
                    else:
                        for item in reward: #pick all rewards
                            for repeat in range(int(item.get("repeat"))):#item amounts are capped - repeat n times
                                finalReward.append(
                                    str("\""+item.get("item"))+"\" "+
                                    str(item.get("amount"))+" "+
                                    str(item.get("quality"))+" "+
                                    str(item.get("fBP"))
                                )
                            
                    for grantItem in finalReward: #execute reward commands
                        self.reactRaw("GiveItemToPlayer "+str(playerID)+" "+grantItem,chatlineObj.port)
                    
                    #claim vote for the next 24h
                    rq = Request(urlACK,headers=self.webheader)
                    urlopen(rq)
                except Exception as e:
                    self.l.error(str(e))
                    self.reactRaw("ServerChatTo \""+str(playerObj.steamid)+"\" whoops - something went wrong.",chatlineObj.port)
            else:
                self.reactRaw("ServerChatTo \""+str(playerObj.steamid)+"\" Nothing to claim for Server with API key: "+str(apikey),chatlineObj.port)
                
    def __voteEnd(self,key,chatlineObj,onSuccess,delayAfterVote=0):
        purekey=key
        key=chatlineObj.port+"_"+key
        seconds = int(cfgh.readCfg(purekey+"_VOTETIME"))
        self.l.info("Votetimer on server "+chatlineObj.port+" for "+cfgh.readCfg(purekey+"_MSG")+" started.")
        while seconds > 0:
            seconds -= 1
            time.sleep(1)
        
        votes = self.votes.get(key)
        if not votes:
            votes = {}
        vAgree = self._voteP(votes)
        minvotes = int(cfgh.readCfg(purekey+"_MINVOTE"))
        
        self.reactRaw("ServerChat Vote for "+cfgh.readCfg(purekey+"_MSG")+" ended. Agreement: "+str(vAgree)+"/"+str(minvotes)+"%",chatlineObj.port)
        
        if vAgree >= minvotes:
            
            if delayAfterVote > 0:
                time.sleep(delayAfterVote)
                
            if isinstance(onSuccess,list):
                for cmd in onSuccess:
                    if isinstance(cmd,int):
                        time.sleep(cmd)
                    else:
                        self.reactRaw(cmd,chatlineObj.port)
            else:
                self.reactRaw(onSuccess,chatlineObj.port)
            
        self.votes.pop(key,None)
        self.l.info("Votetimer on server "+chatlineObj.port+" for "+cfgh.readCfg(purekey+"_MSG")+" ended.")
        
    def letsVote(self,key,chatlineObj,onSuccess,delayAfterVote=0):
        self.l.info("Vote on server "+chatlineObj.port+" for "+cfgh.readCfg(key+"_MSG")+"started")
        now=time.time()
        purekey=key
        key=chatlineObj.port+"_"+key
        retArr=[]
        votes = self.votes.get(key)
                
        if not votes:
            votes = {}
        
        firstvote = True
        if len(votes.items()) > 0:
            firstvote = False
        
        if (firstvote):
            ret = ""
            ret+="ServerChat Vote for "+cfgh.readCfg(purekey+"_MSG")+"."
            ret+=" Min: "+cfgh.readCfg(purekey+"_MINVOTE")+"%."
            ret+=" Time: "+cfgh.readCfg(purekey+"_VOTETIME")+"s"
            
            self.reactRaw(ret, chatlineObj.port)
            
            vc = threading.Thread(target=self.__voteEnd,args=(purekey,chatlineObj,onSuccess,delayAfterVote))
            vc.daemon = True
            vc.start()
        
        vote = None
        if (""+chatlineObj.msg).lower().endswith("yes"):
            vote = Vote(key,chatlineObj.steamPlayer+"_"+chatlineObj.ingamePlayer,now,agree=True)
        elif (""+chatlineObj.msg).lower().endswith("no"):
            vote = Vote(key,chatlineObj.steamPlayer+"_"+chatlineObj.ingamePlayer,now,agree=False)
        elif firstvote:
            vote = Vote(key,chatlineObj.steamPlayer+"_"+chatlineObj.ingamePlayer,now,agree=True)
        else:
            return
        
        if vote:
            votes.update({chatlineObj.steamPlayer+"_"+chatlineObj.ingamePlayer:vote})
        self.votes.update({key:votes})
        
        minvote = int(cfgh.readCfg(purekey+"_MINVOTE"))
        vAgree = self._voteP(votes)
        ret = ""
        ret+="ServerChat "+cfgh.readCfg(purekey+"_MSG")
        ret+=" "+str(vAgree)+"/"+cfgh.readCfg(purekey+"_MINVOTE")+"%"
        self.reactRaw(ret, chatlineObj.port)
    
        
    def _voteP(self,votes):
        '''
        Returns 0-100 as a percentage value.
        100 means 100% of the voters agree
        '''
        vYes=0
        vNo=0
        for key,value in votes.items():
            if value.agree:
                vYes+=1
            else:
                vNo+=1
        if vYes == 0 and vNo == 0:
            return 0
        ppV = 100/(vYes+vNo)
        return int(ppV*vYes)
    
    def getPlayerID(self,steamid64,port):
        '''
        DEPRECATED
        WARNING: This is broken. The command returns the wrong number and every ingame command
        using this value does only work from within the game even with the correct number
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
            return cfgh.readCfg("CHATBOT_CALL_MSG")+" "+cfgh.readCfg(bCfgName+"_MSG")+" - "+cfgh.readCfg(bCfgName+"_DESC")+"\n"
            
            
            
            
            
            
            
            
            
            
            
        