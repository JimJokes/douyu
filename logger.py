import logging
import os
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self, name, level=logging.INFO, log='log/now.log'):
        self.file()
        self.log = log
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        trf = TimedRotatingFileHandler(self.log, when='D', interval=1, backupCount=5)
        formatter = logging.Formatter(fmt='%(levelname)s %(asctime)s %(name)s[line:%(lineno)s] %(message)s\n',
                                      datefmt='%y-%m-%d %H:%M:%S')
        trf.setFormatter(formatter)
        self.logger.addHandler(trf)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def exception(self, msg):
        self.logger.exception(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def file(self):
        log_file = os.path.abspath('log')
        if not os.path.exists(log_file):
            os.mkdir(log_file)
