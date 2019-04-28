# -*- coding: utf-8 -*-
import logging
import os


def get_logger(name):
    debug_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    logger = logging.getLogger(name)
    logger.setLevel(debug_level)
    return logger
