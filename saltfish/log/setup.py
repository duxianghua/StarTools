# -*- coding: utf-8 -*-
import logging
from handler import file_handler, console_handler



def setup_logger():
    log = logging.getLogger(__name__)
    log.addHandler(console_handler)

