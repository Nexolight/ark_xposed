from flask import Flask
from xposed.xposed_stats import xposed_stats_bp
from xposed.xposed_conf import xposed_conf_bp
from xposed import cfgh,l
xposed = Flask(__name__)

class XPosed(object):
    def __init__(self):
        #xposed.register_blueprint(xposed_profiles)
        xposed.register_blueprint(xposed_stats_bp)
        xposed.register_blueprint(xposed_conf_bp)
        xposed.run(port=int(cfgh.readCfg("XPOSED_PORT")), host=cfgh.readCfg("XPOSED_BIND"))

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
                    <p>scope ( all | steamid &lt id &gt | steamname &lt name &gt)</p>
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
                    <p>entry ( allhtml | alljson | &lt setting &gt )</p>
                </span>
            </div>
        </div>
    </body>
</html>
"""

    return apihelp