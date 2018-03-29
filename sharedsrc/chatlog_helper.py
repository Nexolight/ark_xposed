import logging
import copy
import time as _time
import json
import os
import sys
import re
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder
from sharedsrc.file_watch import FileWatch
from sharedsrc.cmd_helper import CMD
from sharedsrc.conf_helper import ConfHelper

class ChatlogHelper(object):
    '''
    This helper allows reading the chatlog from cache
    '''
    def __init__(self, update=True, autoupdate=True, cfgh=None):
        '''
        :param update: Initially read the database.
        :param autoupdate: Automatically update the cache on db changes.
        :param cfgh: a ConfHelper instance. It is created when not given.
        '''
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.spath=os.path.dirname(sys.argv[0])
        self.chatlog=[]
        self.subscribers=[]
        self.fw = None
        self.cfgh = cfgh
        if not cfgh:
            self.cfgh = ConfHelper()
        self.cmd = CMD()
        self.chatlogpath = dbpath=os.path.join(os.path.dirname(sys.argv[0]), self.cfgh.readCfg("CHATLOG_DB"))
        if autoupdate:
            self.fw = FileWatch()
            self.fw.startWatching()
        if update:
            self.updateChatlog(initial=True)
            
    def subscribe(self, callback):
        '''
        Notify callback when the chatlog gets updated
        :param callback: must take 1 argument which represents a new message (dict)
        '''
        self.subscribers.append(callback)
        
    def unsubscribe(self, callback):
        '''
        Stop notify this function
        :param callback:
        '''
        self.subscribers.pop(callback)
        
    def getChatlog(self):
        return self.chatlog
    
    def sendAll(self, name, message, steamid=None, port=None):
        '''
        TODO: pass steamname and ingame name
        
        Send a message via RCON to all players
        :param steamid: SteamID optional to indentify the player within the chatlog later.
        :param name: Name which will appear within the message
        :param message: Text.
        :param port: Text/Number If not set the message will go to all ports
        '''
        rconcmd="ServerChat "
        if steamid:
            rconcmd+=steamid+"-"
        rconcmd+=name+":"+message
        if(not port):
            for port in self.cfgh.readCfg("RCON_PORTS").split(" "):
                out=self.cmd.proc(
                    args=[
                        os.path.join(self.spath, "thirdparty/mcrcon"), "-c",
                        "-H", "127.0.0.1",
                        "-P", port,
                        "-p", self.cfgh.readGUSCfg("ServerAdminPassword"),
                        "ServerChat "+name+": "+message
                    ]
                )
        else:
            out=self.cmd.proc(
                args=[
                    os.path.join(self.spath, "thirdparty/mcrcon"), "-c",
                    "-H", "127.0.0.1",
                    "-P", str(port),
                    "-p", self.cfgh.readGUSCfg("ServerAdminPassword"),
                    "ServerChat "+name+": "+message
                ]
            )
        return out[1]; #Return errors
        
            
    def updateChatlog(self, initial=False):
        '''
        Read the chatlog and save it into memory.
        :param initial: read XPOSED_FNC_CHAT_MAX_FETCH lines initially. This won't call any subscribers.
        '''
        self.l.info("Caching chatlog")
        
        #ALLOW UPDATE THE CACHE LINE BY LINE
        
        lines=int(self.cfgh.readCfg("XPOSED_FNC_CHAT_MAX_COMPARE"))
        if initial:
            lines=int(self.cfgh.readCfg("XPOSED_FNC_CHAT_MAX_FETCH"))
        if self.fw:
            self.fw.registerObserver(filepath=self.chatlogpath, interval=1, callback=self.updateChatlog, unique=True, gone=self._recoverChatlogObserver)
        try:
            output = self.cmd.proc(["tail","-n",str(lines), os.path.join(self.spath,self.cfgh.readCfg("CHATLOG_DB"))])
            if output[1]:
                self.l.error("Error during chatlog read: "+output[1])
            if output[0]:
                for line in output[0].split("\n"):      
                    lifo=re.search("([0-9]+)\:([0-9]+)\:(.+)\s\((.+)\)\:\s(.+)",line)
                    lifo2=re.search("([0-9]+)\:([0-9]+)\:(SERVER)\:\s*\'*(.+)\:(.*)",line)
                    flifo=None
                    if lifo and len(lifo.groups()) > 4:
                        flifo=lifo
                    elif lifo2 and len(lifo2.groups()) > 4:
                        flifo=lifo2
                    if flifo:
                        message=Message(
                            server=int(flifo.group(1)),
                            time=int(flifo.group(2)),
                            steamname=flifo.group(3),
                            playername=flifo.group(4),
                            text=flifo.group(5)
                        )
                        if initial:
                            self.chatlog.append(message)
                            continue
                        if message not in self.chatlog:
                            self.chatlog.append(message)
                            for sub in self.subscribers:
                                if callable(sub):
                                    sub(message)
                                else:
                                    self.unsubscribe(sub)
                            if len(self.chatlog) > int(self.cfgh.readCfg("XPOSED_FNC_CHAT_MAX_FETCH")):
                                self.chatlog.pop(0)
        except Exception as e:
            self.l.error("Cannot update chatlog cache: "+str(e))

    def _recoverChatlogObserver(self):
        if self.fw:
            self.dbpath = os.path.join(sys.argv[0], self.cfgh.readCfg("CHATLOG_DB"))
            self.updateChatlog()
            
class MessageJSONEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Message):
            obj = {
                "server":object.server,
                "steamname":object.steamname,
                "playername":object.playername,
                "time":object.time,
                "text":object.text
            }
            return obj
        else:
            #Use the defaults for everything else
            return JSONEncoder.default(self, object)

class MessageJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.decodeMessage, *args, **kwargs)
    def decodeMessage(self, object):
        res = Message(
            server=object.get("server"),
            steamname=object.get("steamname"),
            playername=object.get("playername"),
            time=object.get("time"),
            text=object.get("text")
        )
        return res       
        
class Message(object):
    def __init__(self,
        server=None,
        steamname=None,
        playername=None,
        time=None,
        text=None
    ):
        self.server=Message.ifndef(server,0)
        self.steamname=Message.ifndef(steamname,"Unknown")
        self.playername=Message.ifndef(playername,"Unknown")
        self.time=Message.ifndef(time,_time.time())
        self.text=Message.ifndef(text,"Lorem Ipsum")
        
    @staticmethod
    def ifndef(val, default):
        '''
        Worarkound some updates
        :param val:
        :param default:
        '''
        if val == None:
            return default
        return val