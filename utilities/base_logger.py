import logging
from datetime import datetime

# DEBUG: Detailed information, typically of interest only when diagnosing problems.

# INFO: Confirmation that things are working as expected.

# WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.

# ERROR: Due to a more serious problem, the software has not been able to perform some function.

# CRITICAL: A serious error, indicating that the program itself may be unable to continue running.


def create_logger(name): 	
    
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(lineno)d:%(funcName)s:%(message)s')
    logger.level = logging.DEBUG
    
    file_handler = logging.FileHandler ( 'logging/ThesisProject_' + datetime.today().strftime('%Y-%m-%d') + '.log')
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger
