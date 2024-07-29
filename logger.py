#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: logger.py
Description: Creates a logger instance with the specified log level, format, and file to use in all other scripts.
Author: @alexdjulin
Date: 2024-07-25
"""

import os
import logging
from config_loader import get_config
config = get_config()

# define a namespace common to all logger instances
NAMESPACE = 'ai-chitchat'

# create root logger
try:
    levels = {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}
    log_level = levels[config['log_level'].upper()]
    log_format = config['log_format']
    log_file = config['log_filepath']
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(level=log_level, format=log_format, filename=log_file)

except Exception:
    # create default logger
    log_level = 20  # INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_file = 'logs/avatar.log'
    logging.basicConfig(level=log_level, format=log_format, filename=log_file)

logging.getLogger(NAMESPACE)

# empty log file if option is set
if config['empty_log']:
    with open(log_file, 'w'):
        pass


def get_logger(name: str) -> logging.Logger:
    ''' Creates child logger inside namespace '''
    return logging.getLogger(f'{NAMESPACE}.{name}')
