#!/usr/bin/python3
# -*- coding: utf-8 -*-
import threading
import multiprocessing
import sys
import argparse
import json
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder
import re
import os
import logging
import time
import subprocess
import chardet
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-11s %(message)s")

class Main(object):
    '''
    Just the main class
    '''
    spath = os.path.dirname(sys.argv[0])
    settings={
        "intervall":60000,
        "gus":None,
        "playerdb":os.path.join(spath,"arkstats/playerdb.json"),
        "playerrecords":os.path.join(spath,"arkstats/playerrecords.info"),
        "serverrecords":os.path.join(spath,"arkstats/serverrecords.info")
    }

    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.info("Initialized ARK statistics tool")
        self.settings = Main.settings
        parser = argparse.ArgumentParser(description="Settings for ARK statistics")
        parser.add_argument(
            "-s", "--settings-file", metavar="path", nargs=1,
            help="The path to the GameUserSettings",
            dest="gus"
        )
        
        parser.add_argument(
            "-i", "--intervall", metavar="seconds", nargs="?",
            default=0,
            type=int,
            help="The internal db.",
            dest="intv"
        )
        parser.add_argument(
            "-d", "--player-db", metavar="path", nargs="?",
            default=None,
            help="The internal db.",
            dest="plrec"
        )
        parser.add_argument(
            "-p", "--player-records", metavar="path", nargs="?",
            default=None,
            help="The path to the records for players",
            dest="plrec"
        )
        parser.add_argument(
            "-a", "--arkserver-records", metavar="path", nargs="?",
            default=None,
            help="The path to the records for the ark server",
            dest="srvrec"
        )

        args = parser.parse_args()

        if args.gus and os.path.exists(args.gus[0]):
            self.settings["gus"]=args.gus[0]
        else:
            self.l.error("Please enter a valid path to GameUserSettings!")
            parser.print_help()
            sys.exit(1)
        if args.intv and args.intv > 0:
            self.settings["intervall"]=args.intv
        if args.plrec:
            self.settings["playerrecords"]=args.plrec
        if args.srvrec:
            self.settings["serverrecords"]=args.srvrec

        worker = Worker(self.settings, GUSHelper(self.settings))
        worker.start()
        try:
            while True:
                worker.fetchPlayerInfo()
                time.sleep(self.settings.get("intervall"))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.l.warn(str(e))
            pass
        finally:
            self.l.info("terminated...")
            worker.stop()
            sys.exit(0)

class GUSHelper(object):
    def __init__(self,settings):
        self.settings = settings

    def readKeyGUS(self,key):
        gus = open(self.settings.get("gus"),"rb")
        enc = chardet.detect(gus.read()).get("encoding")
        if enc == "windows-1252":
            enc = "cp1252"
        gus.close()
        gus = open(self.settings.get("gus"), encoding=enc)
        for line in gus.readlines():
            matches = re.search("^\s*?"+key+"\s*?=\s*?([^\s]+).*$",line)
            if matches:
                gus.close()
                return matches.group(1)
        gus.close()
        return None


class CMD(object):
    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)

    def proc(self, args, env=None, proctimeout=5, cwd=None):
        '''
        This executes an external program and returns the output as well as the errors
        decoded as utf-8 or plain (on fail). This method may time out. It returns None on any error.
        Othersie an Array like [str(output), str(errors)] is returned.
        :param args: The command line as array.
        :param env: Additional environment variables.
        :param proctimeout: The maximum execution time.
        :param cwd: Change to directory
        '''
        output=""
        errors=""
        sysenv=os.environ.copy()
        if env:
            sysenv.update(env)
        process=None
        try:
            process=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=sysenv, cwd=cwd)#subprocess with pipes
            stdoutdata, stderrdata=process.communicate(timeout=proctimeout)#Get the data and wait for finish
            try:
                output=stdoutdata.decode("utf-8")
                errors=stderrdata.decode("utf-8")
            except UnicodeDecodeError:#In some rare cases
                self.local.l.warn("UnicodeDecodeError - cannot read output")
                output=stdoutdata
                errors=stderrdata
        except subprocess.TimeoutExpired:#Self explaining
            emsg="TimeoutExpired - Execution required more than "+str(proctimeout)+"s."
            errors=emsg
        except MemoryError:
            emsg="MemoryError - It seems like you're out of ram - The output is to big."
            errors=emsg
        except Exception as e:
            emsg=str(e)
            errors=emsg
        finally:
            if process:
                try:
                    process.kill()
                except OSError as e:
                    pass
                if process.stdout:
                    process.stdout.close()
                if process.stderr:
                    process.stderr.close()
        return[output, errors]


class Worker(threading.Thread):
    '''
    Do the work in threads
    '''

    def __init__(self, settings, gush):
        '''
        Initializes the worker
        :param settings: from Main.settings
        :param gush: GUSHelper instance
        '''
        super(Worker, self).__init__()
        self.l = logging.getLogger(self.__class__.__name__)
        self._stopit = threading.Event()
        self.activeTasks = []
        self.queue = []
        self.l.info("Initialized ARK statistics worker")
        self.settings=settings
        self.l.info("Settings loaded:")
        for key,value in settings.items():
            self.l.info(str(key)+" --> "+str(value))
        self.cmd = CMD()
        self.l.info("Started command line helper")
        self.gush = gush
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
                "mcrcon", "-c",
                "-H", "127.0.0.1",
                "-P", "32330",
                "-p", self.gush.readKeyGUS("ServerAdminPassword"),
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
                    self.folderhealth(self.settings.get("playerdb"))
                    players=[]
                    self.lock.acquire()
                    if os.path.exists(self.settings.get("playerdb")):
                        file = open(self.settings.get("playerdb"), "r")
                        players=json.load(file, cls=PlayerJSONDecoder)
                        file.close()
                    exists=False

                    for plr in players:
                        if plr.steamid == player.steamid:
                            exists=True
                            plr.no=player.no
                            plr.name=player.name
                            td = player.lastseen - plr.lastseen
                            if td < self.settings.get("intervall") + 5000:
                                plr.timeplayed += td
                            plr.lastseen = player.lastseen
                            self.l.info("updated player "+str(plr.name))
                            break

                    if not exists:
                        players.append(player)
                        self.l.info("added new player \""+str(player.name)+"\" to db.")
                    file = open(self.settings.get("playerdb"), "w+")
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

class PlayerJSONEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Player):
            obj = {
                "no":object.no,
                "name":str(object.name),
                "steamid":object.steamid,
                "lastseen":object.lastseen,
                "timeplayed":object.timeplayed,
                "firstseen":object.firstseen
            }
            return obj
        else:
            #Use the defaults for everything else
            return JSONEncoder.default(self, object)

class PlayerJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.decodePlayer, *args, **kwargs)
    def decodePlayer(self, object):
        res = Player(
            no=object.get("no"),
            name=object.get("name"),
            steamid=object.get("steamid"),
            lastseen=object.get("lastseen"),
            timeplayed=object.get("timeplayed"),
            firstseen=object.get("firstseen"),
        )
        return res       
        
class Player(object):
    def __init__(self,
        no=0,
        name="unknown",
        steamid=0,
        lastseen=0,
        timeplayed=0,
        firstseen=0
    ):
        self.no=no
        self.name=name
        self.steamid=steamid
        self.lastseen=lastseen
        self.timeplayed=timeplayed
        self.firstseen=firstseen    

if __name__ == '__main__':
    Main()
