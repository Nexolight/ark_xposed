from xposed import cfgh,l
import sys
import os
import string
import random
class Utils:
    def __init__(self):
        pass
    
    @staticmethod
    def getSecret():
        '''
        This returns the key used to encrypt the session.
        One is generated in case there's no one already
        '''
        key=None
        try:
            if os.path.isfile(cfgh.readCfg("XPOSED_SECRET_KEY")):
                with open(cfgh.readCfg("XPOSED_SECRET_KEY"), "r") as f:
                    key=f.read()
            else:
                with open(cfgh.readCfg("XPOSED_SECRET_KEY"), "w") as f:
                    pool = string.ascii_letters + string.digits
                    key=''.join(random.choice(pool) for i in range(256))
                    f.write(key)
        except Exception as e:
            l.error("Fatal - no viable path for XPOSED_SECRET_KEY in config")
            l.error(e)
            sys.exit(1)
        return key