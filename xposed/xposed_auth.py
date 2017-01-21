from flask import request, Response

def check_auth(request):
    auth = request.authorization
    if(auth and auth.username == "admin" and auth.password == "Kaesefondue"):
        return True
    else:
        return False

def has_roles(request, roles=[]):
    #
    # nothing done yet
    #
    return True

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

def requires_role(roles):
    def wrapper(f):
        def wrapped(*args, **kwargs):
            if not has_roles(request, roles):
                return Response("Your privileges are too low for this action",403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper