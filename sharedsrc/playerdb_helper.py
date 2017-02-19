import json
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder
from sharedsrc.file_watch import FileWatch
from sharedsrc.conf_helper import ConfHelper
import os
import sys
import logging

class PlayerDBHelper(object):
    '''
    A little helper which allows reading the DB from cache
    '''
    def __init__(self, update=True, autoupdate=True, cfgh=None):
        '''
        :param update: Initially read the database.
        :param autoupdate: Automatically update the cache on db changes.
        :param cfgh: a ConfHelper instance. It is created when not given.
        '''
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.l.propagate=True
        self.playerdb=[]
        self.fw = None
        self.cfgh = cfgh
        if not cfgh:
            self.cfgh = ConfHelper()
        self.dbpath = dbpath=os.path.join(os.path.dirname(sys.argv[0]), self.cfgh.readCfg("STATS_PLAYERDB"))
        if autoupdate:
            self.fw = FileWatch()
            self.fw.startWatching()
        if update:
            self.updatePlayerDB()
    
    def updatePlayerDB(self):
        '''
        Read the db and save it into memory.
        '''
        self.l.info("Caching playerdb")
        if self.fw:
            self.fw.registerObserver(filepath=self.dbpath, interval=1, callback=self.updatePlayerDB, unique=True, gone=self._recoverDBObserver)
        try:
            with open(self.dbpath, "r") as f:
                self.playerdb = json.loads(f.read(),cls=PlayerJSONDecoder)
        except Exception as e:
            self.l.error("Cannot update playerdb cache: "+str(e))
            
    def _recoverDBObserver(self):
        if self.fw:
            self.dbpath = os.path.join(os.path.dirname(sys.argv[0]), self.cfgh.readCfg("STATS_PLAYERDB"))
            self.updatePlayerDB()
    
    def getPlayerDB(self):
        '''
        Returns the an array with all Player objects.
        '''
        return self.playerdb;
    
    def getPlayerByID(self, id):
        '''
        Returns the Player object which matches the given steam id.
        :param id:
        '''
        for player in self.playerdb:
            if player.steamid == id:
                return player
    
    def getPlayersByName(self, name):
        '''
        Returns the player objects which have the given name
        :param name:
        '''
        players=[]
        for player in self.playerdb:
            if player.name == name:
                players.append(player)
        if(len(players)==0):
            return None
        return players
        
    
class PlayerJSONEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Player):
            obj = {
                "no":object.no,
                "name":str(object.name),
                "steamid":object.steamid,
                "lastseen":object.lastseen,
                "timeplayed":object.timeplayed,
                "firstseen":object.firstseen,
                "isonline":object.isonline
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
            isonline=object.get("isonline")
        )
        return res       
        
class Player(object):
    def __init__(self,
        no=0,
        name="unknown",
        steamid=0,
        lastseen=0,
        timeplayed=0,
        firstseen=0,
        isonline=False
    ):
        self.no=no
        self.name=name
        self.steamid=steamid
        self.lastseen=lastseen
        self.timeplayed=timeplayed
        self.firstseen=firstseen
        self.isonline=isonline