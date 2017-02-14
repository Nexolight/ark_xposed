from sharedsrc.logger import XPOSED_LOG
import logging.config
logging.config.dictConfig(XPOSED_LOG)
#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)-8s %(name)-45s %(message)s")
l = logging.getLogger(__name__)
from sharedsrc.cmd_helper import CMD
from sharedsrc.conf_helper import ConfHelper
from sharedsrc.playerdb_helper import PlayerDBHelper
cfgh = ConfHelper()
pdbh = PlayerDBHelper(update=True, autoupdate=True, cfgh=cfgh)