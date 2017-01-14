import logging
from sharedsrc.conf_helper import ConfHelper
from flask import Flask
from xposed.xposed_stats import xposed_stats_bp
cfgh = ConfHelper();
xposed = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-11s %(message)s")

class XPosed(object):
    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)
        #xposed.register_blueprint(xposed_profiles)
        xposed.register_blueprint(xposed_stats_bp)
        xposed.run(port=int(cfgh.readCfg("XPOSED_PORT")), host=cfgh.readCfg("XPOSED_BIND"))

@xposed.route("/", methods=['GET', 'POST'])
def hello_world():
    return "hello world"