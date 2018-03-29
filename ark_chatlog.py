#!/usr/bin/python3
# -*- coding: utf-8 -*-
from sharedsrc.logger import CHATLOG_LOG
from sharedsrc.adminbot import Adminbot
import logging.config
from lib2to3.pgen2.token import AT
logging.config.dictConfig(CHATLOG_LOG)
import threading
import multiprocessing
import sys
from sharedsrc.cmd_helper import CMD
import os
import time
from sharedsrc.conf_helper import ConfHelper
from sharedsrc.playerdb_helper import Player, PlayerDBHelper 
from sharedsrc.chatline import Chatline
cfgh = ConfHelper(update=True, autoupdate=True)

class Chatlog(object):
    '''
    Just the main class
    '''
    spath = os.path.dirname(sys.argv[0])
    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.info("Initialized ARK Chatlog tool")
        worker = CLWorker(self.spath)
        worker.start()
        try:
            while True:
                worker.fetchChatlog()
                time.sleep(float(cfgh.readCfg("CHATLOG_FETCH_INTERVALL")))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.l.warn(str(e))
            pass
        finally:
            self.l.info("terminated...")
            worker.stop()
            sys.exit(0)


class CLWorker(threading.Thread):
    '''
    Do the work in threads
    '''

    def __init__(self, spath):
        '''
        Initializes the worker
        :param spath: path of this script
        '''
        super(CLWorker, self).__init__()
        self.l = logging.getLogger(self.__class__.__name__)
        self._stopit = threading.Event()
        self.activeTasks = []
        self.queue = []
        self.l.info("Initialized ARK Chatlog worker")
        self.spath=spath
        self.cmd = CMD()
        self.l.info("Started command line helper")
        self.lock = threading.Lock()
        self.adminbot = None
        self.pdbh = None
        if(int(cfgh.readCfg("CHATBOT_ENABLED")) == 1):
            self.adminbot=Adminbot(os.path.join(self.spath, "thirdparty/mcrcon"))
            self.pdbh=PlayerDBHelper()

    def run(self):
        while not self.isStopped():
            for aT in self.activeTasks:
                if aT.get("finished")==True:
                    self.activeTasks.remove(aT)
            if len(self.queue) > 0 and len(self.activeTasks) < 1: #multiprocessing.cpu_count():
                jobObj = self.queue.pop(0)
                self.activeTasks.append(jobObj)
                jobObj.get("job").daemon = True
                jobObj.get("job").start()
            else:
                time.sleep(0.1)

    def folderhealth(self, abspath):
        '''
        Create the direcotry of the path if it doesn't exist
        :param abspath:
        '''
        if not os.path.exists(os.path.dirname(abspath)):
            self.l.warn("Created folder "+os.path.dirname(abspath))
            os.mkdir(os.path.dirname(abspath))

    def fetchChatlog(self):
        for port in cfgh.readCfg("RCON_PORTS").split(" "):
            fPI = threading.Thread(target=self.__fetchChatlog,args=(port,))
            self.queue.append({"job":fPI,"finished":False})

    def __fetchChatlog(self,port):
        self.l.debug("fetch chatlog")
        try:
            output = self.cmd.proc(
                args=[
                    os.path.join(self.spath, "thirdparty/mcrcon"), "-c",
                    "-H", "127.0.0.1",
                    "-P", port,
                    "-p", cfgh.readGUSCfg("ServerAdminPassword"),
                    "GetChat"
                ]
            )
            if output[1]:
                self.l.warn("Fetching players failed!")
                self.l.error(output[1])
            if output[0]:
                filepath=os.path.join(self.spath,cfgh.readCfg("CHATLOG_DB"))
                self.lock.acquire(True)
                for line in output[0].split("\n"):
                    chatlineObj = Chatline.create(port=port, line=line)
                    if(chatlineObj):
                        chatlineObj.write(filepath)
                        self.usebot(chatlineObj)
                self.lock.release()
        finally:
            self.__subthread_suicide()
            
    def usebot(self,chatlineObj):
        if(int(cfgh.readCfg("CHATBOT_ENABLED")) == 1):
            players = self.pdbh.getPlayersByName(chatlineObj.steamPlayer)
            playerObj = None
            if(players):
                playerObj=players[0]#take the first matching
            fPI = threading.Thread(target=self.adminbot.react,args=(
                chatlineObj,
                playerObj,
                self.__subthread_suicide,))
            self.queue.append({"job":fPI,"finished":False})
        
    def __subthread_suicide(self):
        for aT in self.activeTasks:
            if aT.get("job")==threading.currentThread():
                aT.update({"finished":True})

    def stop(self):
        '''
        Stop the thread and all it's childs. May take a few seconds
        '''
        self._stopit.set()

    def isStopped(self):
        '''
        True when the thread is terminated
        '''
        return self._stopit.isSet()

if __name__ == '__main__':
    Chatlog()
