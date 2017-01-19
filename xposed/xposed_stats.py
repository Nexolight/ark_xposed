import os
import sys
import json
from flask import Blueprint, request, Response
from xposed import cfgh
from xposed.xposed_auth import requires_auth,requires_role
from sharedsrc.playerdb_helper import PlayerJSONEncoder, PlayerJSONDecoder, Player

xposed_stats_bp = Blueprint("xposed_stats", __name__)

@xposed_stats_bp.route("/serverstats", methods=['GET', 'POST'])
@requires_auth()
@requires_role(["admin"])
def getStats():
    scope=request.args.get("scope")
    spath = os.path.dirname(sys.argv[0])
    players=""
    try:
        with open(os.path.join(spath,cfgh.readCfg("STATS_PLAYERDB")), "r") as file:
            players=file.read()
    except Exception as e:
        return Response("Server fail: "+str(e),500)
    if scope == "all":
        return players
        