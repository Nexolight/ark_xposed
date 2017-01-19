import os
import sys
import json
from flask import Blueprint, request, Response
from xposed import cfgh
from xposed.xposed_auth import requires_auth,requires_role
from sharedsrc.playerdb_helper import PlayerJSONEncoder, PlayerJSONDecoder, Player

xposed_conf_bp = Blueprint("xposed_conf", __name__)

@xposed_conf_bp.route("/serverconf", methods=['GET', 'POST'])
@requires_auth()
@requires_role(["admin"])
def getConf():
    entry=request.args.get("entry")
    ret=None
    if(entry=="allhtml"):
        ret = cfgh.readGUSCfgPlain(filterPW=True).replace("\n","<br>")
    elif(entry=="alljson"):
        ret = json.dumps(cfgh.readGUSCfgDict(filterPW=True))
    elif(entry):
        ret = cfgh.readGUSCfg(entry,filterPW=True)
    if not ret:
         return Response("404 Not found",404)
    return ret
        