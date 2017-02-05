import os
import sys
import json
from flask import Blueprint, request, Response
from xposed import cfgh,l
from xposed.xposed_auth import requires_auth,requires_role
from sharedsrc.arkprofile_helper import ArkProfileDecoder

xposed_profile_bp = Blueprint("xposed_profile", __name__)

@xposed_profile_bp.route("/profile", methods=['GET', 'POST'])
@requires_auth()
@requires_role(["admin"])
def getProfile():
    steamid=request.args.get("steamid")
    if(not steamid):
        return Response("400 - Missing param",400)
    apd = ArkProfileDecoder()
    arkprofile=None
    try:
        arkprofile = apd.decode_file(
            os.path.join(cfgh.readCfg("ARKDIR"),"ShooterGame/Saved/SavedArks/"+steamid+".arkprofile"))
    except Exception as e:
        l.error(e)
        return Response("500 - Can't read arkprofile:",500)
    
    if(apd):
        return arkprofile.replace("\n","<br>")
    
    return Response("500 - Couldn't parse arkprofile:",500)
    '''
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
    '''
        
        