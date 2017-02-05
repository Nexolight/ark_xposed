import os
import sys
import json
from flask import Blueprint, request, Response
from xposed import cfgh
from xposed.xposed_auth import requires_openid,requires_role
from sharedsrc.playerdb_helper import PlayerJSONEncoder, PlayerJSONDecoder, Player

xposed_conf_bp = Blueprint("xposed_conf", __name__)

@xposed_conf_bp.route("/serverconf", methods=['GET', 'POST'])
@requires_openid()
@requires_role(["admin"])
def getConf():
    entry=request.args.get("entry")
    if(entry=="allhtml"):
        return cfgh.readGUSCfgPlain(filterPW=True).replace("\n","<br>")
    elif(entry=="alljson"):
        return json.dumps(cfgh.readGUSCfgDict(filterPW=True))
    elif(entry):
        ret = cfgh.readGUSCfg(entry,filterPW=True)
        if not ret:
            return Response("404 - setting: "+entry+" not found", 404)
        return ret
    else:
        return Response("400 - Unsupported param",400)
        
        