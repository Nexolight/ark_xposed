
import json
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder

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