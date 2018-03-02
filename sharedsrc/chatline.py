import time
import re
class Chatline(object):
    '''
    Just the main class
    '''
    
    def __init__(self,msg=None,port=None,time=time.time()*1000,ingamePlayer=None,steamPlayer=None):
        self.msg = msg
        self.port = port
        self.time = time
        self.ingamePlayer = ingamePlayer
        self.steamPlayer = steamPlayer
    
    @staticmethod
    def create(time=time.time()*1000, port=None, line=None):
        '''
        Returns a Chatline instance
        The line is supposed to be raw from the rcon response
        '''
        print(line)
        if re.match("^.+\:.+$",line) and not re.match("^AdminCmd\:.*",line) and not re.match("^SERVER\:.*",line):
            segments=line.split(":")
            pSegMatch = re.search('(\S+).*?\((.+)\)',line)
            chatlineObj = Chatline()
            chatlineObj.msg = "".join(segments[1:])
            chatlineObj.port = port
            chatlineObj.time = time
            if(pSegMatch):
                chatlineObj.steamPlayer = pSegMatch.group(1)
                chatlineObj.ingamePlayer = pSegMatch.group(2)
            return chatlineObj
        
    def write(self,filepath):
        with open(filepath, "a+") as f:
            f.write(self.port+":"+str(int(self.time))+":"+self.steamPlayer+" ("+self.ingamePlayer+"):"+self.msg+"\n")
        
            