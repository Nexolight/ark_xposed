from sharedsrc.cmd_helper import CMD
from sharedsrc.conf_helper import ConfHelper
import logging
cfgh = ConfHelper();
cmd = CMD()
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-20s %(message)s")
l = logging.getLogger("XPosed")
