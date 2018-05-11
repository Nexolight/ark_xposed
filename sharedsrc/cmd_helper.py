import subprocess
import os
import logging
import psutil
import signal
class CMD(object):
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)

    def getServerProcess(self,port):
        '''
        Returns the process of the ShooterGameServer
        which listens on the given port
        '''
        for proc in psutil.process_iter():
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if pinfo.get("name") != "ShooterGameServer":
                    continue
    
            for connection in proc.connections():
                    if connection.status == psutil.CONN_LISTEN and connection.laddr.port == int(port):
                            return proc

    def killserver(self, port):
        '''
        Kills the server instance
        that listens on the given port.
        '''
        proc = self.getServerProcess(port)
        if not proc:
            self.l.warn("Could not find the server process for port "+str(port))
            return
        proc.send_signal(signal.SIGTERM)

    def proc(self, args, env=None, proctimeout=5, cwd=None, encoding=None):
        '''
        This executes an external program and returns the output as well as the errors
        decoded as utf-8 or plain (on fail). This method may time out. It returns None on any error.
        Othersie an Array like [str(output), str(errors)] is returned.
        :param args: The command line as array.
        :param env: Additional environment variables.
        :param proctimeout: The maximum execution time.
        :param cwd: Change to directory
        :param encoding: Switch the used encofing (default utf-8)
        '''
        output=""
        errors=""
        if not encoding:
            encoding="utf-8"
        sysenv=os.environ.copy()
        if env:
            sysenv.update(env)
        process=None
        try:
            process=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=sysenv, cwd=cwd)#subprocess with pipes
            stdoutdata, stderrdata=process.communicate(timeout=proctimeout)#Get the data and wait for finish
            try:
                output=stdoutdata.decode(encoding)
                errors=stderrdata.decode(encoding)
            except UnicodeDecodeError:#In some rare cases
                self.l.warn("UnicodeDecodeError - cannot read output")
                output=stdoutdata
                errors=stderrdata
        except subprocess.TimeoutExpired:#Self explaining
            emsg="TimeoutExpired - Execution required more than "+str(proctimeout)+"s."
            errors=emsg
        except MemoryError:
            emsg="MemoryError - It seems like you're out of ram - The output is to big."
            errors=emsg
        except Exception as e:
            emsg=str(e)
            errors=emsg
        finally:
            if process:
                try:
                    process.kill()
                except OSError as e:
                    pass
                if process.stdout:
                    process.stdout.close()
                if process.stderr:
                    process.stderr.close()
        return[output, errors]