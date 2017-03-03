#!/usr/bin/python3
# -*- coding: utf-8 -*-
from sharedsrc.logger import STATISTICS_LOG
import logging.config
logging.config.dictConfig(STATISTICS_LOG)
import threading
import multiprocessing
import sys
import json
from sharedsrc.playerdb_helper import PlayerJSONEncoder, PlayerJSONDecoder, Player
from sharedsrc.cmd_helper import CMD
import re
import os
import time
import chardet
from sharedsrc.conf_helper import ConfHelper
cfgh = ConfHelper(update=True, autoupdate=True)

class Statistics(object):
    '''
    Just the main class
    '''
    spath = os.path.dirname(sys.argv[0])
    
    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.info("Initialized ARK statistics tool")
        worker = StWorker(self.spath)
        worker.start()
        try:
            while True:
                worker.fetchPlayerInfo()
                time.sleep(int(cfgh.readCfg("STATS_INTERVALL")))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.l.warn(str(e))
            pass
        finally:
            self.l.info("terminated...")
            worker.stop()
            sys.exit(0)


class StWorker(threading.Thread):
    '''
    Do the work in threads
    '''

    def __init__(self, spath):
        '''
        Initializes the worker
        :param spath: path of this script
        '''
        super(StWorker, self).__init__()
        self.l = logging.getLogger(self.__class__.__name__)
        self._stopit = threading.Event()
        self.activeTasks = []
        self.queue = []
        self.l.info("Initialized ARK statistics worker")
        self.spath=spath
        self.cmd = CMD()
        self.l.info("Started command line helper")
        self.lock = threading.Lock()

    def run(self):
        while not self.isStopped():
            for aT in self.activeTasks:
                if not aT.isAlive():
                    self.activeTasks.remove(aT)
            if len(self.queue) > 0 and len(self.activeTasks) < multiprocessing.cpu_count():
                job = self.queue.pop(0)
                self.activeTasks.append(job)
                job.daemon = True
                job.start()
            else:
                time.sleep(0.1)

    def folderhealth(self, abspath):
        '''
        Create the direcotry of the path if it doesn't exist
        :param abspath:
        '''
        if not os.path.exists(abspath):
            self.l.warn("Created folder "+abspath)
            os.mkdir(abspath)

    def fetchPlayerInfo(self):
        fPI = threading.Thread(target=self.__fetchPlayerInfo)
        self.queue.append(fPI)

    def __fetchPlayerInfo(self):
        output = self.cmd.proc(
            args=[
                os.path.join(self.spath, "thirdparty/mcrcon"), "-c",
                "-H", "127.0.0.1",
                "-P", cfgh.readGUSCfg("RCONPort"),
                "-p", cfgh.readGUSCfg("ServerAdminPassword"),
                "listplayers"
            ]
        )
        if output[1]:
            self.l.warn("Fetching players failed!")
            self.l.error(output[1])
        if output[0]:
            #===================================================================
            # Load all existing players
            #===================================================================
            self.folderhealth(os.path.join(self.spath,cfgh.readCfg("STATS_PLAYERDB")))
            players=[]
            self.lock.acquire()#Load all player objects
            if os.path.exists(os.path.join(self.spath,cfgh.readCfg("STATS_PLAYERDB"))):
                file = open(os.path.join(self.spath,cfgh.readCfg("STATS_PLAYERDB")), "r")
                players=json.load(file, cls=PlayerJSONDecoder)
                file.close()
            self.lock.release()
            changedp=[]#Add all changed players
            
            #Iterate over all online players
            for line in output[0].split("\n"):
                candidate = re.search("([0-9]+)\.\s+([^\s|^,]+)[^0-9]+([0-9]+)", line)
                if candidate:#This was given by the command and represents "one" player
                    now = int(time.time())
                    player = Player(
                        no=candidate.group(1),
                        name=candidate.group(2),
                        steamid=candidate.group(3),
                        timeplayed=0,
                        lastseen=now,
                        firstseen=now,
                        isonline=True,
                    )
                    exists=False#We wan't to add them later when they don't exist
                    #Iterate over all stored players
                    for plr in players:
                        if plr.steamid == player.steamid:#We just do updates
                            exists=True
                            plr.no=player.no#might change
                            plr.name=player.name#might change
                            #===================================================
                            # Update the lastseen field
                            #===================================================
                            td = player.lastseen - plr.lastseen
                            if td < int(cfgh.readCfg("STATS_INTERVALL")) + 5000:
                                plr.timeplayed += td
                            plr.lastseen = player.lastseen
                            changedp.append(plr)
                            self.l.info("updated player "+str(plr.name))
                            break;
                            
                    if not exists:#New player just add him/her
                        players.append(player)
                        changedp.append(player)
                        self.l.info("added new player \""+str(player.name)+"\" to db.")
                        
            for plr in players:
                if plr not in changedp:#This player logged out.
                    if plr.isonline:
                        plr.isonline=False
                        self.l.info("Player: "+plr.name+" is now offile")
                        self.processPlayerProfile(plr.steamid)
                elif not plr.isonline:#This player just logged in.
                    plr.isonline=True
                    self.l.info("Player: "+plr.name+" is now online")
                    self.processPlayerProfile(plr.steamid)
            if len(changedp) > 0:#only on changes
                self.lock.acquire()
                file = open(os.path.join(self.spath,cfgh.readCfg("STATS_PLAYERDB")), "w+")
                json.dump(players,file,cls=PlayerJSONEncoder)
                file.close()
                self.lock.release()

    def processPlayerProfile(self,steamid):
        fPI = threading.Thread(target=self.__processPlayerProfile,args=(steamid,))
        self.queue.append(fPI)

    def __processPlayerProfile(self,steamid):
        self.l.info("Extracting profile info from: "+steamid+".arkprofile")
        extractor=os.path.join(self.spath,"thirdparty/ark-tools-jar-with-dependencies.jar")
        outfolder=os.path.join(self.spath,cfgh.readCfg("STATS_PLAYERPROFILES"))
        self.l.debug(outfolder)
        savegame=os.path.join(cfgh.readCfg("ARKDIR"),"ShooterGame/Saved/SavedArks/"+steamid+".arkprofile")
        self.lock.acquire()
        self.folderhealth(outfolder)
        self.lock.release()
        args=[
            "java", "-jar", extractor,
            "p2j",
            savegame,
            os.path.join(outfolder,steamid+".json")
        ]
        self.cmd.proc(args)
        #self.l.debug(out)

    def fetchServerInfo(self):
        fSI = threading.Thread(target=self.__fetchServerInfo, args=(updateStats))
        self.queue.append(fPI)

    def __fetchServerInfo(self):
        pass

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
    Statistics()
