#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: config_loader.py
Description: Loads the contents of the yaml configuration file into a 'config' variable, to be imported in all other scripts.
Author: @alexdjulin
Date: 2024-07-25
"""

import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
