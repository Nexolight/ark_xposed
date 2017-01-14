import subprocess
import os
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(name)-11s %(message)s")
class CMD(object):
    def __init__(self):
        self.l = logging.getLogger(self.__class__.__name__)

    def proc(self, args, env=None, proctimeout=5, cwd=None):
        '''
        This executes an external program and returns the output as well as the errors
        decoded as utf-8 or plain (on fail). This method may time out. It returns None on any error.
        Othersie an Array like [str(output), str(errors)] is returned.
        :param args: The command line as array.
        :param env: Additional environment variables.
        :param proctimeout: The maximum execution time.
        :param cwd: Change to directory
        '''
        print("PROC")
        output=""
        errors=""
        sysenv=os.environ.copy()
        if env:
            sysenv.update(env)
        process=None
        try:
            process=subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=sysenv, cwd=cwd)#subprocess with pipes
            stdoutdata, stderrdata=process.communicate(timeout=proctimeout)#Get the data and wait for finish
            try:
                output=stdoutdata.decode("utf-8")
                errors=stderrdata.decode("utf-8")
            except UnicodeDecodeError:#In some rare cases
                self.local.l.warn("UnicodeDecodeError - cannot read output")
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
        print("PROC DONE")
        print(str([output, errors]))
        return[output, errors]