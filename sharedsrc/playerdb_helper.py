import json
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder
from sharedsrc.file_watch import FileWatch
from sharedsrc.conf_helper import ConfHelper
import os
import sys
import logging
import re

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
        self.svgpath = os.path.join(os.path.dirname(sys.argv[0]), self.cfgh.readCfg("STATS_PLAYERPROFILES"))
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
                pdb=[]
                for player in json.loads(f.read(),cls=PlayerJSONDecoder):
                    player.savegames=self._readPlayerSavegames(player.steamid)
                    pdb.append(player)
                if len(pdb) > 0:
                    self.playerdb = pdb
                else:
                    self.l.warn("(Pass update) The file looks empty at a point where it shouldn't")
        except Exception as e:
            self.l.error("Cannot update playerdb cache: "+str(e))
            
    def _recoverDBObserver(self):
        if self.fw:
            self.dbpath = os.path.join(os.path.dirname(sys.argv[0]), self.cfgh.readCfg("STATS_PLAYERDB"))
            self.updatePlayerDB()
            
    def _readPlayerSavegames(self, steamid):
        '''
        Read the preprocessed savegames from arktools which may or may not be
        available depending on the individual setup
        
        TODO: Implement multi savegames
        :param steamid:
        '''
        try:
            profiles=[]
            for svg in os.listdir(self.svgpath):
                #===============================================================
                # Match is a placeholder for later coming multiple profiles
                # <steamid>.<playerid>.<ingame name>.json or <steamid>.json
                #===============================================================
                if re.match("^("+steamid+"\.[0-9]\..+|"+steamid+")\.json",svg): 
                    with open(os.path.join(self.svgpath,svg)) as f:
                        self.l.debug("caching "+steamid+".json for player "+steamid)
                        profiles.append(json.loads(f.read()))
            return profiles
        except FileNotFoundError as e:
            self.l.warn("(Ignore) No preprocessed savegame found for player "+steamid)
        except Exception as e:
            self.l.warn("(Ignore ) Something went wrong: "+str(e))
        return []
    
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
    
    
    #===========================================================================
    # Savegame profile access functions
    #===========================================================================
    def getSvgPlayerName(self, svg):
        self.l.debug("Seeking PlayerName")
        return self._getSvgProperty(
            props=self._getSvgPrimalPlayerData(svg),
            prop="PlayerName",
            type="StrProperty",
        )
    
    def getActiveSvg(self, player):
        '''
        Returns the currently active savegame from the given player
        :param player:
        '''
        return self.__getActiveSvg(player)
    
    def getActiveSvgByID(self, steamid):
        '''
        Returns the currently active savegame from the player
        with the given steamid
        :param steamid:
        '''
        player=self.getPlayerByID(steamid)
        return self.__getActiveSvg(player)
        
    def __getActiveSvg(self, player):
        '''
        TODO: implement multiple profiles
        :param player:
        '''
        if len(player.savegames) > 0:
            return player.savegames[0]
        return none
    
    #===========================================================================
    # Internal shorthands to access the json savegame
    #===========================================================================
    def _getSvgProfileProperties(self, svg):
        return svg.get("profile").get("properties")
    
    def _getSvgPrimalPlayerData(self, svg):
        return self._getSvgProperty(
            props=self._getSvgProfileProperties(svg),
            prop="MyData",
            type="StructProperty",
            structType="PrimalPlayerDataStruct"
        )
    
    def _getSvgProperty(self, props, prop, type, structType=None):
        for property in props:
            if property.get("type") == type and property.get("name") == prop:                
                if type == "StructProperty" and property.get("structType") == structType:
                    return property.get("value")
                else:
                    return property.get("value")

class PlayerJSONEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Player):
            obj = {
                "no":object.no,
                "name":object.name,
                "steamid":object.steamid,
                "lastseen":object.lastseen,
                "timeplayed":object.timeplayed,
                "firstseen":object.firstseen,
                "isonline":object.isonline,
                "savegames":object.savegames
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
            isonline=object.get("isonline"),
            savegames=object.get("savegames")
        )
        return res       
        
class Player(object):
    def __init__(self,
        no=None,
        name=None,
        steamid=None,
        lastseen=None,
        timeplayed=None,
        firstseen=None,
        isonline=None,
        savegames=None
    ):
        self.no=Player.ifndef(no,0)
        self.name=Player.ifndef(name,"unknown")
        self.steamid=Player.ifndef(steamid,0)
        self.lastseen=Player.ifndef(lastseen,0)
        self.timeplayed=Player.ifndef(timeplayed,0)
        self.firstseen=Player.ifndef(firstseen,0)
        self.isonline=Player.ifndef(isonline,False)
        self.savegames=Player.ifndef(savegames,[])
        
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
            
    