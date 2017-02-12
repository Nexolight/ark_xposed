from flask import request, Response, session, redirect, g
import re
import json
import sys
import copy
from xposed import cfgh,l,pdbh
from xposed.xposed_main import oid, xposed

def check_auth(request):
    auth = request.authorization
    if(auth and auth.username == "admin" and auth.password == "Kaesefondue"):
        return True
    else:
        return False
    
@xposed.before_request
def before_request():
    g.steamid=None
    g.reqPage=None
    if session.get("openid"):
        openid = session["openid"]
        g.steamid=openid.get("identity").split("/")[-1]

@xposed.route('/login')
@oid.loginhandler
def login():
    if request.args.get("status")=="failed":
        return Response("Auth failed",401)
    if g.steamid is not None:
        l.info("Welcome back : "+g.steamid)
        return redirect(oid.get_next_url())
    if request.args.get("command")=="login":
        return oid.try_login("http://steamcommunity.com/openid", ask_for=['email', 'nickname'])

@oid.after_login
def after_login(resp):
    obj={
        "next":request.args.get("next"),
        "openid_complete":request.args.get("openid_complete"),
        "janrain_nonce":request.args.get("janrain_nonce"),
        "openid":{
            "ns":request.args.get("openid.ns"),
            "mode":request.args.get("openid.mode"),
            "op_endpoint":request.args.get("openid.op_endpoint"),
            "claimed_id":request.args.get("openid.claimed_id"),
            "identity":request.args.get("openid.identity"),
            "return_to":request.args.get("openid.return_to"),
            "response_nonce":request.args.get("openid.response_nonce"),
            "assoc_handle":request.args.get("openid.assoc_handle"),
            "signed":request.args.get("openid.signed"),
            "sig":request.args.get("openid.sig")
        }
    }
    session["openid"]=obj.get("openid")
    if str(obj.get("openid_complete")) == "yes":
        g.steamid=obj.get("openid").get("identity").split("/")[-1]
        l.info("Access granted for: "+g.steamid)
        return redirect(session.get("reqPostAuthPage"))
    return redirect("/login?status=failed")

def has_roles(request, roles=[]):
    if(len(roles)==0):
        return True
    accept=True
    if "player" in roles:
        if not pdbh.getPlayerByID(g.steamid):
            l.info("Player permission denied for this request!")
            accept=False
        else:
            l.info("Player permission granted for this request!")
    if "admin" in roles:
        if not cfgh.readCfg("XPOSED_ADMINS") or not g.steamid in cfgh.readCfg("XPOSED_ADMINS"):
            l.info("Admin permission denied for this request!")
            accept=False
        else:
            l.info("Admin permission granted for this request!")
    return accept

def has_params(request, params=[]):
    for p in params:
        if not request.args.get(p):
            return False
    return True
    
def requires_auth():
    def wrapper(f):
        def wrapped(*args, **kwargs):
            if not check_auth(request):
                return Response(
                    "Could not verify your access level for that URL.\nYou have to login with proper credentials",
                    401,
                    {"WWW-Authenticate": "Basic realm=\"Login Required\""})
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def requires_openid():
    def wrapper(f):
        def wrapped(*args, **kwargs):
            if not g.steamid:
                session["reqPostAuthPage"]=request.url
                return redirect("/login?command=login")
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def requires_role(roles):
    def wrapper(f):
        def wrapped(*args, **kwargs):
            if not has_roles(request, roles):
                return Response("Your privileges are too low for this action",403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper