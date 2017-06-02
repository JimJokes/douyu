import logging
import os, shutil
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self, name='root', level=logging.INFO, log='log/now.log'):
        self.file()
        self.log = log
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        trf = TimedRotating(self.log, when='M', interval=1, backupCount=5)
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

