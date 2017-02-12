import os
import sys
import json
import re
from datetime import datetime
from flask import Blueprint, request, Response
from xposed import cfgh,cmd,l
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
        output = cmd.proc(["tail","-n",str(lines), os.path.join(spath,cfgh.readCfg("CHATLOG_DB"))])
        if output[1]:
            return Response("500 - Error during chatlog read: "+output[1],500)
        if output[0]:
            ret=[]
            for line in output[0].split("\n"):
                lifo=re.search("([0-9]+)\:(.+)\s\((.+)\)\:\s(.+)",line)
                lifo2=re.search("([0-9]+)\:(SERVER)\:\s*\'*(.+)\:(.*)",line)
                flifo=None
                if lifo and len(lifo.groups()) > 3:
                    flifo=lifo
                elif lifo2 and len(lifo2.groups()) > 3:
                    flifo=lifo2
                if flifo:
                    ret.append({
                        "time":flifo.group(1),
                        "steamname":flifo.group(2),
                        "playername":flifo.group(3),
                        "text":flifo.group(4)
                    })
            if format == "json":
                return json.dumps(ret)
            elif format == "html":
                out = ""
                for obj in ret:
                    out += str(datetime.fromtimestamp(int(obj.get("time"))/1000))+": "
                    out += obj.get("steamname")+" "
                    out += "("+obj.get("playername")+"): "
                    out += obj.get("text")+"<br>"
                return out
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
        return "ok"