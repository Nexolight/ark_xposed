import os
import sys
import json
import re
from datetime import datetime
from flask import Blueprint, request, Response
from xposed import cfgh,l

from sharedsrc.cmd_helper import CMD
from sharedsrc.chatlog_helper import ChatlogHelper
from xposed.xposed_auth import requires_openid,requires_role
xposed_chat_bp = Blueprint("xposed_chat", __name__)

@xposed_chat_bp.route("/chat", methods=['GET', 'POST'])
@requires_openid()
@requires_role(["player"])
def chat():
    command=request.args.get("command")
    if(not command):
        return Response("400 - Missing param",400)   
    format="json"
    fmt=request.args.get("format")
    if fmt and fmt == "json":
        format="json"
    elif fmt and fmt == "html":
        format="html"
    spath = os.path.dirname(sys.argv[0])
    if command=="read":
        lines=request.args.get("lines")
        if not lines or int(lines) > int(cfgh.readCfg("XPOSED_FNC_CHAT_MAX_FETCH")):
            lines=int(cfgh.readCfg("XPOSED_FNC_CHAT_MAX_FETCH"))
            
        if format == "json":
            return Response(response=json.dumps(ret),status=200,mimetype="application/json")
        elif format == "html":
            out = ""
            for obj in ret:
                out += str(datetime.fromtimestamp(int(obj.get("time"))/1000))+": "
                out += obj.get("steamname")+" "
                out += "("+obj.get("playername")+"): "
                out += obj.get("text")+"<br>"
            return Response(response=out,status=200,mimetype="text/html")
    if command=="send":
        usr=request.args.get("username")
        msg=request.args.get("message")
        if not usr or not msg:
            return Response("400 - Missing param",400)
        out=cmd.proc(
            args=[
                os.path.join(spath, "thirdparty/mcrcon"), "-c",
                "-H", "127.0.0.1",
                "-P", cfgh.readGUSCfg("RCONPort"),
                "-p", cfgh.readGUSCfg("ServerAdminPassword"),
                "ServerChat "+usr+": "+msg
            ]
        )
        if out[1]:
            return Response("500 - Couldn't send message: "+output[1],500)
        return Response(response="ok",status=200,mimetype="text/html")