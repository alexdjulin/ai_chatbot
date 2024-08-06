#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: tools.py
Description: Tool methods that the langchain agent can use to retrieve informatoin the LLM does not know about.
Author: @alexdjulin
Date: 2024-07-25
"""

from pathlib import Path
# langchain
from langchain_core.tools import tool
# logger
from logger import get_logger
LOG = get_logger(Path(__file__).stem)


@tool
def get_information_about_me(title: str, comment: str) -> None:
    """Get a list of info about me."""

    LOG.debug("Tool call: get_information_about_me")

    info = [
        "My name is Alex",
        "I am currently looking for a job as an AI software developer",
        "I like coding, trail running and snorkeling",
        "My favourite color is emerald green",
        "My favourite movie is Jurassic Park",
        "My favourite book is La Nuit Des Temps by René Barjavel",
        "I am a fan of the Harry Potter series",
        "I am a trail runner and I love running in the mountains. The longest distance I ran is 61 km.",
        "Sometimes I play blues harmonica, but I suck at it. Don't tell anyone!",
    ]

    return info


# List of tools
agent_tools = [
    get_information_about_me
]
