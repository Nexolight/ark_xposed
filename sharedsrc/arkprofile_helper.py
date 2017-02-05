import os
import sys
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-20s %(message)s")

class ArkProfileDecoder(object):
    '''
    A helper which can read the .arkprofile files
    '''
    HEADER=b'\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11'
    NEWLINE=b'\x00\x00\x00'
    X01='\x3D\x11\x00\x00\x00'
    FORMAT={
        b'\x41':'A',
        b'\x42':'B',
        b'\x43':'C',
        b'\x44':'D',
        b'\x45':'E',
        b'\x46':'F',
        b'\x47':'G',
        b'\x48':'H',
        b'\x49':'I',
        b'\x4a':'J',
        b'\x4b':'K',
        b'\x4c':'L',
        b'\x4d':'M',
        b'\x4e':'N',
        b'\x4f':'O',
        b'\x50':'P',
        b'\x51':'Q',
        b'\x52':'R',
        b'\x53':'S',
        b'\x54':'T',
        b'\x55':'U',
        b'\x56':'V',
        b'\x57':'W',
        b'\x58':'X',
        b'\x59':'Y',
        b'\x5A':'Z',
        b'\x61':'a',
        b'\x62':'b',
        b'\x63':'v',
        b'\x64':'d',
        b'\x65':'e',
        b'\x66':'f',
        b'\x67':'g',
        b'\x68':'h',
        b'\x69':'i',
        b'\x6a':'j',
        b'\x6b':'k',
        b'\x6c':'l',
        b'\x6d':'m',
        b'\x6e':'n',
        b'\x6f':'o',
        b'\x70':'p',
        b'\x71':'q',
        b'\x72':'r',
        b'\x73':'s',
        b'\x74':'t',
        b'\x75':'u',
        b'\x76':'v',
        b'\x77':'w',
        b'\x78':'x',
        b'\x79':'y',
        b'\x7a':'z',
        b'\x30':'0',
        b'\x31':'1',
        b'\x32':'2',
        b'\x33':'3',
        b'\x34':'4',
        b'\x35':'5',
        b'\x36':'6',
        b'\x37':'7',
        b'\x38':'8',
        b'\x39':'9',
        b'\x2f':'/',
        b'\x28':'(',
        b'\x29':')',
        b'\x2e':'.',
        b'\x01':',',
    }
    
    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)
        self.l.info("Initialized ArkProfileDecoder")
    
    def decode_file(self, arkprofile_f):
        self.l.info("Opening file "+os.path.basename(arkprofile_f))
        pos=0
        ret=""
        with open(arkprofile_f, "rb") as file:
            if(ArkProfileDecoder.HEADER != file.read(len(ArkProfileDecoder.HEADER))):
                raise Exception("Header missmatch!")
            pos+=len(ArkProfileDecoder.HEADER)
            self.l.info("Header found!")
            while True:
                #===============================================================
                # Newline
                #===============================================================
                if(ArkProfileDecoder.NEWLINE == file.read(len(ArkProfileDecoder.NEWLINE))):
                    ret += "\n"
                    pos += len(ArkProfileDecoder.NEWLINE)
                else:
                    file.seek(pos-len(ArkProfileDecoder.NEWLINE))
                
                #===============================================================
                # Everything else
                #===============================================================
                chunk = file.read(1)
                pos+=1
                if(not chunk):
                    self.l.info("Reached end of file!")
                    break
                decchar=ArkProfileDecoder.FORMAT.get(chunk)
                if(decchar):
                    ret += decchar
                    
        return ret
        
        

class ArkProfile(object):
    def __init__(self):
        pass
    
    def __str__(self):
        return "unimplemented"