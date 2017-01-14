#!/usr/bin/python3
# -*- coding: utf-8 -*-
import threading
import multiprocessing
import sys
import json
from sharedsrc.playerdb_helper import PlayerJSONEncoder, PlayerJSONDecoder, Player
from sharedsrc.cmd_helper import CMD
import re
import os
import logging
import time
import chardet
from sharedsrc.conf_helper import ConfHelper
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-11s %(message)s")

class Main(object):
    '''
    Just the main class
    '''
    spath = os.path.dirname(sys.argv[0])
    cfgh = ConfHelper()
    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.info("Initialized ARK statistics tool")

        worker = Worker(self.spath, self.cfgh)
        worker.start()
        try:
            while True:
                worker.fetchPlayerInfo()
                time.sleep(int(self.cfgh.readCfg("STATS_INTERVALL")))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.l.warn(str(e))
            pass
        finally:
            self.l.info("terminated...")
            worker.stop()
            sys.exit(0)


class Worker(threading.Thread):
    '''
    Do the work in threads
    '''

    def __init__(self, spath, cfgh):
        '''
        Initializes the worker
        :param spath: path of this script
        :param cfgh: ConfHelper instance
        '''
        super(Worker, self).__init__()
        self.l = logging.getLogger(self.__class__.__name__)
        self._stopit = threading.Event()
        self.activeTasks = []
        self.queue = []
        self.l.info("Initialized ARK statistics worker")
        self.spath=spath
        self.cmd = CMD()
        self.l.info("Started command line helper")
        self.cfgh = cfgh
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
        if not os.path.exists(os.path.dirname(abspath)):
            self.l.warn("Created folder "+os.path.dirname(abspath))
            os.mkdir(os.path.dirname(abspath))

    def fetchPlayerInfo(self):
        fPI = threading.Thread(target=self.__fetchPlayerInfo)
        self.queue.append(fPI)

    def __fetchPlayerInfo(self):
        output = self.cmd.proc(
            args=[
                os.path.join(self.spath, "thirdparty/mcrcon"), "-c",
                "-H", "127.0.0.1",
                "-P", self.cfgh.readGUSCfg("RCONPort"),
                "-p", self.cfgh.readGUSCfg("ServerAdminPassword"),
                "listplayers"
            ]
        )
        if output[1]:
            self.l.warn("Fetching players failed!")
            self.l.error(output[1])
        if output[0]:
            for line in output[0].split("\n"):
                candidate = re.search("([0-9]+)\.\s+([^\s|^,]+)[^0-9]+([0-9]+)", line)
                if candidate:
                    player = Player(
                        no=candidate.group(1),
                        name=candidate.group(2),
                        steamid=candidate.group(3),
                        timeplayed=0,
                        lastseen=int(time.time()),
                        firstseen=int(time.time())
                    )
                    self.folderhealth(os.path.join(self.spath,self.cfgh.readCfg("STATS_PLAYERDB")))
                    players=[]
                    self.lock.acquire()
                    if os.path.exists(os.path.join(self.spath,self.cfgh.readCfg("STATS_PLAYERDB"))):
                        file = open(os.path.join(self.spath,self.cfgh.readCfg("STATS_PLAYERDB")), "r")
                        players=json.load(file, cls=PlayerJSONDecoder)
                        file.close()
                    exists=False

                    for plr in players:
                        if plr.steamid == player.steamid:
                            exists=True
                            plr.no=player.no
                            plr.name=player.name
                            td = player.lastseen - plr.lastseen
                            if td < int(self.cfgh.readCfg("STATS_INTERVALL")) + 5000:
                                plr.timeplayed += td
                            plr.lastseen = player.lastseen
                            self.l.info("updated player "+str(plr.name))
                            break

                    if not exists:
                        players.append(player)
                        self.l.info("added new player \""+str(player.name)+"\" to db.")
                    file = open(os.path.join(self.spath,self.cfgh.readCfg("STATS_PLAYERDB")), "w+")
                    json.dump(players,file,cls=PlayerJSONEncoder)
                    file.close()
                    self.lock.release()



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
    Main()
