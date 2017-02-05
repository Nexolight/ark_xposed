import os
import sys
import json
from flask import Blueprint, request, Response
from xposed import cfgh
from xposed.xposed_auth import requires_openid,requires_role
from sharedsrc.playerdb_helper import PlayerJSONEncoder, PlayerJSONDecoder, Player

xposed_stats_bp = Blueprint("xposed_stats", __name__)

@xposed_stats_bp.route("/serverstats", methods=['GET', 'POST'])
@requires_openid()
@requires_role(["admin"])
def getStats():
    scope=request.args.get("scope")
    if(not scope):
        return Response("400 - Missing param",400)
    spath = os.path.dirname(sys.argv[0])
    players=""
    try:
        with open(os.path.join(spath,cfgh.readCfg("STATS_PLAYERDB")), "r") as file:
            players=file.read()
    except Exception as e:
        return Response("500 - Can't read db: "+str(e),500)
    if(scope and scope == "all"):
        return players
    elif(scope and scope == "steamid"):
        steamid=request.args.get("id")
        if(not steamid):
            return Response("400 - Missing param",400)
        for player in json.loads(players,cls=PlayerJSONDecoder):
            if(str(player.steamid) == steamid):
                return json.dumps(player, cls=PlayerJSONEncoder)
        return Response("404 - steamid: "+steamid+" not found",404)
    elif(scope and scope == "steamname"):
        steamname=request.args.get("name")
        if(not steamname):
            return Response("400 - Missing param",400)
        for player in json.loads(players,cls=PlayerJSONDecoder):
            if(str(player.name).lower() == steamname.lower()):
                return json.dumps(player, cls=PlayerJSONEncoder)
        return Response("404 - steamid: "+steamname+" not found",404)
    else:
        return Response("400 - Unsupported param",400)