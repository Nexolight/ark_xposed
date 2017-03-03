import logging
import copy
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
    
    
    def sendAll(self, name, message, steamid=None):
        '''
        Send a message via RCON to all players
        :param steamid: SteamID optional to indentify the player within the chatlog later.
        :param name: Name which will appear within the message
        :param message: Text.
        '''
        rconcmd="ServerChat "
        if steamid:
            rconcmd+=steamid+"-"
        rconcmd+=name+":"+message
        out=self.cmd.proc(
            args=[
                os.path.join(spath, "thirdparty/mcrcon"), "-c",
                "-H", "127.0.0.1",
                "-P", self.cfgh.readGUSCfg("RCONPort"),
                "-p", self.cfgh.readGUSCfg("ServerAdminPassword"),
                "ServerChat -"+name+": "+message
            ]
        )
        return out[1];
        
            
    def updateChatlog(self, initial=False):
        '''
        Read the chatlog and save it into memory.
        :param initial: read XPOSED_FNC_CHAT_MAX_FETCH lines initially. This won't call any subscribers.
        '''
        self.l.info("Caching chatlog")
        
        #ALLOW UPDATE THE CACHE LINE BY LINE
        
        lines=int(cfgh.readCfg("XPOSED_FNC_CHAT_MAX_COMPARE"))
        if initial:
            lines=int(cfgh.readCfg("XPOSED_FNC_CHAT_MAX_FETCH"))
        if self.fw:
            self.fw.registerObserver(filepath=self.chatlogpath, interval=1, callback=self.updateChatlog, unique=True, gone=self._recoverChatlogObserver)
        try:
            output = cmd.proc(["tail","-n",str(lines), os.path.join(spath,cfgh.readCfg("CHATLOG_DB"))])
            if output[1]:
                self.l.e("Error during chatlog read: "+output[1])
            if output[0]:
                for line in output[0].split("\n"):
                    lifo=re.search("([0-9]+)\:(.+)\s\((.+)\)\:\s(.+)",line)
                    lifo2=re.search("([0-9]+)\:(SERVER)\:\s*\'*(.+)\:(.*)",line)
                    flifo=None
                    if lifo and len(lifo.groups()) > 3:
                        flifo=lifo
                    elif lifo2 and len(lifo2.groups()) > 3:
                        flifo=lifo2
                    if flifo:
                        message={
                            "time":flifo.group(1),
                            "steamname":flifo.group(2),
                            "playername":flifo.group(3),
                            "text":flifo.group(4)
                        }
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
                            if len(self.chatlog) > int(cfgh.readCfg("XPOSED_FNC_CHAT_MAX_FETCH")):
                                self.chatlog.pop(0)
        except Exception as e:
            self.l.error("Cannot update chatlog cache: "+str(e))

    def _recoverChatlogObserver(self):
        if self.fw:
            self.dbpath = os.path.join(sys.argv[0], self.cfgh.readCfg("CHATLOG_DB"))
            self.updateChatlog()