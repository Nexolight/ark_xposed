from sharedsrc.conf_helper import ConfHelper
cfgh = ConfHelper();
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-11s %(message)s")
l = logging.getLogger("XPosed")