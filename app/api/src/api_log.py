import os,time,logging
from logging.handlers import TimedRotatingFileHandler
def getLogger(name,logFile,level:int=logging.DEBUG):
    _logger:logging.Logger=logging.getLogger(name,level=level)
    _handler=TimedRotatingFileHandler(logFile,when="midnight",backupCount=30,encoding="utf-8")
    _handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    _logger.addHandler(_handler)
    return _logger
    pass
