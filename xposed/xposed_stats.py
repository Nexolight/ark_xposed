import os
import sys
import json
from flask import Blueprint, request, Response
from xposed import pdbh
from xposed.xposed_auth import requires_openid,requires_role
from sharedsrc.playerdb_helper import PlayerJSONEncoder, PlayerJSONDecoder

xposed_stats_bp = Blueprint("xposed_stats", __name__)

@xposed_stats_bp.route("/serverstats", methods=['GET', 'POST'])
def getStats():
    scope=request.args.get("scope")
    if(not scope):
        return Response("400 - Missing param",400)
    if(scope and scope == "all"):
        return Response(response=json.dumps(pdbh.getPlayerDB(), cls=PlayerJSONEncoder),status=200,mimetype="application/json")
    elif(scope and scope == "steamid"):
        steamid=request.args.get("id")
        if(not steamid):
            return Response("400 - Missing param",400)
        player=pdbh.getPlayerByID(steamid)
        if player:
            return Response(response=json.dumps(player, cls=PlayerJSONEncoder),status=200,mimetype="application/json")
        return Response("404 - steamid: "+steamid+" not found",404)
    elif(scope and scope == "steamname"):
        steamname=request.args.get("name")
        if(not steamname):
            return Response("400 - Missing param",400)
        player = pdbh.getPlayersByName(steamname);
        if(player):
            return Response(response=json.dumps(player[0], cls=PlayerJSONEncoder),status=200,mimetype="application/json")
        return Response("404 - steamid: "+steamname+" not found",404)
    else:
        return Response("400 - Unsupported param",400)