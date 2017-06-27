# -*- coding: utf-8 -*-
import logging
from handler import file_handler, console_handler



def setup_logger():
    logging.root.addHandler(console_handler)
    logging.root.addHandler(file_handler)

