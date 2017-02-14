import logging
import os
import time
import threading
import multiprocessing

class FileWatch(object):
    '''
    A class which should help to keep a file in cache
    while automatically updating the cache in case the file
    changes.
    '''
    def __init__(self):
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self.l.info("FileWatch initialized");
        self.observers = {}
        self.worker = None
    
    def registerObserver(self, filepath, interval, callback, unique=True, gone=None):
        '''
        Do a callback when the given file changes.
        :param filepath:
        :param interval:
        :param callback:
        :param unique: default=True, Only adds the observer when the file is not watched yet.
        :param gone: default=None, Call this function when the file is no longer available once to give it a chance for re-register.
        '''
        if unique and self.observers.get(filepath):
            return
        self.l.info("Add new observer")
        self.observers.update({
                filepath:{
                    "observer":callback,
                    "ondestroy":gone,
                    "interval":interval,
                    "modified":os.path.getmtime(filepath),
                    "lastcheck":time.time()
                }
            })
        
    def unregisterObservers(self, file):
        '''
        Stop doing callbacks when this file changes
        :param callback:
        '''
        self.l.info("Remove observer")
        self.observers.pop(file)
        
    def startWatching(self):
        if self.worker and not self.worker.isStopped():
            self.l.error("File observer is already running")
            return
        self.l.info("Start file observer")
        self.worker = FWWorker(self.observers)
        self.worker.daemon = True;
        self.worker.start()
        
    def stopWatching(self):
        self.l.info("Stopping file observer")
        self.worker.stopIt()
        while not self.worker.isStopped():
            time.sleep(1);
        self.l.info("Stopped file observer")
        
class FWWorker(threading.Thread):
    '''
    Do the work within a thread to
    not block anything else.
    '''
    def __init__(self, observers):
        super(FWWorker, self).__init__()
        self.l = logging.getLogger(__name__+"."+self.__class__.__name__)
        self._stopit = threading.Event()
        self.l.info("Initialized FileWatch worker")
        self.observers = observers
        self.activeTasks = []
        self.queue = []
        self.lock = threading.Lock()
        
    def run(self):
        while not self.isStopped():
            now = time.time()
            for key, obj in self.observers.items():
                if now - obj.get("lastcheck") > obj.get("interval"):
                    obj["lastcheck"]=time.time();
                    self.checkFile(key)
            for aT in self.activeTasks:
                if not aT.isAlive():
                    self.activeTasks.remove(aT)
            if len(self.queue) > 0 and len(self.activeTasks) < multiprocessing.cpu_count():
                job = self.queue.pop(0)
                self.activeTasks.append(job)
                job.daemon = True
                job.start()
            else:
                time.sleep(0.05)
    
    
    def checkFile(self, filepath):
        '''
        Check the modification time of the file
        and call the corresponding callback when it was modified..
        :param filepath:
        '''
        fPI = threading.Thread(target=self.__checkFile, args=(filepath,))
        self.queue.append(fPI)
        
    def __checkFile(self, filepath):
        '''
        see checkFile
        :param filepath:
        '''
        if not os.path.exists(filepath):
            self.l.info("File "+filepath+" doesn't exist anymore - removing observers")
            self.lock.acquire(True)
            detached=self.observers.pop(filepath)
            self.lock.release()
            if detached.get("ondestroy"):
                self.l.info("calling gone callback")
                detached.get("ondestroy")()
            return
        mt = os.path.getmtime(filepath)
        if self.observers.get(filepath).get("modified") != mt:
            self.l.info("File "+filepath+" changed - calling observer")
            self.lock.acquire(True)
            self.observers.get(filepath)["modified"] = mt
            self.observers.get(filepath).get("observer")()
            self.lock.release()
        
        
    def stopIt(self):
        '''
        Stop the thread and all it's childs. May take a few seconds
        '''
        self._stopit.set()

    def isStopped(self):
        '''
        True when the thread is terminated
        '''
        return self._stopit.isSet()
