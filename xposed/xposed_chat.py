import os
import sys
import json
from datetime import datetime
from flask import Blueprint, request, Response, g
from xposed import cfgh,l,pdbh

from sharedsrc.cmd_helper import CMD
from sharedsrc.chatlog_helper import ChatlogHelper, Message, MessageJSONEncoder
from xposed.xposed_auth import requires_openid,requires_role
clgh = ChatlogHelper()


xposed_chat_bp = Blueprint("xposed_chat", __name__)
#@requires_openid()
@xposed_chat_bp.route("/chat", methods=['GET', 'POST'])
#@requires_role(["player"])
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
            ret = Response(
                    response=json.dumps(clgh.getChatlog(), cls=MessageJSONEncoder),
                    status=200,
                    mimetype="application/json"
                )
            return ret
        elif format == "html":
            out = ""
            for message in clgh.getChatlog():
                out += str(datetime.fromtimestamp(int(message.time/1000)))+":    "
                out += message.steamname+"    "
                out += "("+message.playername+"):    "
                out += message.text+"<br>"
            return Response(response=out,status=200,mimetype="text/html")
    if command=="send":
        usr=request.args.get("username")
        msg=request.args.get("message")
        if not usr or not msg:
            return Response("400 - Missing param",400)
        playerprofile=pdbh.getActiveSvgByID(steamid="76561197987278684")
        print(pdbh.getSvgPlayerName(playerprofile))
        #l.debug(pdbh.getPlayerName(playerprofile))
        #getStrPropValue
        error="test"
        #error=clgh.sendAll(
        #    name=pdb.getActiveProfileByID(steamid=g.steamid).get("properties").get(""), 
        #    message=msg, 
        #    steamid=g.steamid)
        if error:
            return Response("500 - Couldn't send message: "+error,500)
        return Response(response="ok",status=200,mimetype="text/html")