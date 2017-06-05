import logging
import os, shutil
import time
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self, name='root', level=logging.INFO, log='log/now.log'):
        self.file()
        self.log = log
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        trf = TimedRotating(self.log, when='MIDNIGHT', interval=1, backupCount=5)
        formatter = logging.Formatter(fmt='%(levelname)s %(asctime)s %(name)s[line:%(lineno)s] %(message)s\n',
                                      datefmt='%y-%m-%d %H:%M:%S')
        trf.setFormatter(formatter)
        self.logger.addHandler(trf)

    def file(self):
        log_file = os.path.abspath('log')
        if not os.path.exists(log_file):
            os.mkdir(log_file)


class TimedRotating(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super(TimedRotating, self).__init__(*args, **kwargs)

    def rotate(self, source, dest):
        if not callable(self.rotator):
            if os.path.exists(source):
                shutil.copy2(source, dest)
                with open(source, 'w') as f:
                    f.truncate()
        else:
            self.rotator(source, dest)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))
        if not os.path.exists(dfn):
            # os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
