from xposed import l,cfgh
from flask import Flask, Response
from xposed.xposed_utils import Utils
from flask_session import Session
from flask_openid import OpenID
from flask_cors import CORS, cross_origin
xposed = Flask(__name__)
cors = CORS(xposed,resources={r"/*": {"origins": cfgh.readCfg("XPOSED_CORS_ORIGINS")}})
xposed.config.update({
    "OPENID_FS_STORE_PATH":cfgh.readCfg("XPOSED_DATA"),
    "SESSION_TYPE":"filesystem",
    "SECRET_KEY":Utils.getSecret(),
})
oid = OpenID(xposed,safe_roots=["/postlogin","/login","/chat","/serverconf","/serverstats"])
#xposed.secret_key = 'super secret key'
#xposed.config['SESSION_TYPE'] = 'filesystem'
Session(xposed)
from xposed.xposed_stats import xposed_stats_bp
from xposed.xposed_conf import xposed_conf_bp
from xposed.xposed_profile import xposed_profile_bp
from xposed.xposed_chat import xposed_chat_bp


class XPosed(object):
    def __init__(self):
        l.info("Xposed WEB API Initializing!")
        #xposed.register_blueprint(xposed_profiles)
        xposed.register_blueprint(xposed_stats_bp)
        xposed.register_blueprint(xposed_conf_bp)
        xposed.register_blueprint(xposed_profile_bp)
        xposed.register_blueprint(xposed_chat_bp)
        xposed.run(port=int(cfgh.readCfg("XPOSED_PORT")), host=cfgh.readCfg("XPOSED_BIND"), threaded=True)

@xposed.route("/", methods=['GET', 'POST'])
def hello_world():
    '''
    Yea sry I don't have time left that's fine for my purpose
    '''
    apihelp="""
<html>
    <head>
        <style>
            body{
                background-color:#000;
                color:#E0E0E0;
                padding: 2em;
                font-family:"Trebuchet MS", Helvetica, sans-serif
            }
            .entry{
                background-color:#202020;
            }
            .entry span.head{
                border-bottom: 0.2em solid #000;
                padding: 0.5em;
                display: inline-block;
                background-color: #404040;
                width: calc(100% - 1em);
                cursor:pointer;
            }
            .entry div.content{
                max-height: 0em;
                overflow:hidden;
                font-size: 0.8em;
                transition: max-height 200ms;
            }
            .entry div.content.selected{
                max-height: 100em;
            }
            .entry div.content span{
                padding: 0.5em 0.5em 0.5em 2em;
                display: inline-block;
            }
        </style>
    </head>
    <script type="text/javascript">
        var spoiler = function(elem){
            elem.nextElementSibling.classList.toggle("selected");
        };
    </script>
    <body>
        <h3>API Manual - ARK Xposed</h3>
        <div class="entry">
            <span class="head" onclick="spoiler(this)">
                /serverstats
            </span>
            <div class="content">
                <span>
                    <p>Returns overall play times on this server</p>
                    <br>
                    <p>scope=(all|steamid|steamname)</p>
                    <br>
                    <p>steamid id=str</p>
                    <p>steamname name=str</p>
                </span>
            </div>
        </div>
        <div class="entry">
            <span class="head" onclick="spoiler(this)">
                /serverconf
            </span>
            <div class="content">
                <span>
                    <p>Returns GameUserConfig.ini settings</p>
                    <br>
                    <p>entry=(allhtml|alljson|"GUSSetting")</p>
                </span>
            </div>
        </div>
        <div class="entry">
            <span class="head" onclick="spoiler(this)">
                /chat
            </span>
            <div class="content">
                <span>
                    <p>Use the ingame chat</p>
                    <br>
                    <p>command=(read|send)</p>
                    <br>
                    <p>read [format=(html|json)] [lines=num] <i>limited</i></p>
                    <p>send message=str [port=<rcon>]</p>
                </span>
            </div>
        </div>
    </body>
</html>
"""

    return apihelp