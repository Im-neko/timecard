import logging

def get_module_logger(modname, filename):
    logger = logging.getLogger(modname)
    handler = logging.FileHandler(filename)
    formatter = logging.Formatter('%(asctime)s:[NAME]:%(name)s:[lINE]:%(lineno)d [lEVEL]:%(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(10)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger