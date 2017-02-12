from sharedsrc.cmd_helper import CMD
from sharedsrc.conf_helper import ConfHelper
from sharedsrc.playerdb_helper import PlayerDBHelper
import logging
cfgh = ConfHelper()
pdbh = PlayerDBHelper(update=True, autoupdate=True, cfgh=cfgh)
cmd = CMD()
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-20s %(message)s")
l = logging.getLogger("XPosed")
