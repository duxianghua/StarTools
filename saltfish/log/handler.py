import logging

def file_handler(filename):
    FileHandler = logging.FileHandler(filename=filename)
    FileHandler.format('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    FileHandler.setLevel(level=logging.DEBUG)
    return FileHandler

def console_handler():
    formatter = logging.Formatter(
        '[%(levelname)-8s] %(message)s', datefmt='%H:%M:%S'
    )
    StreamHandler = logging.StreamHandler()
    StreamHandler.setFormatter(formatter)
    StreamHandler.setLevel(logging.DEBUG)
    return StreamHandler