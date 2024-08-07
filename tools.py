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
def get_information_about_your_interlocutor(title: str, comment: str) -> None:
    """Get a list of info about your interlocutor."""

    LOG.debug("Tool call: get_information_about_your_interlocutor")

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

@tool
def get_information_about_yourself(title: str, comment: str) -> None:
    """Get a list of info about yourself."""

    LOG.debug("Tool call: get_information_about_yourself")

    info = [
        "Your name is Babette, you are a helpful advisor with a great sense of humor",
        "You are a NASA rocket scientist and a professional chef",
        "You have your own Youtube channel called 'Chez Babette' where you teach how to make the best Cheese Fondue",
        "My favourite color is yellow",
        "You are a casual surfer and your favourite movie is Point Break. Patrick Swayze is your hero!",
        "Your favourite book is The Little Prince by Antoine de Saint-Exupéry",
        "You are a big fan of Charlie Chaplin's movies, you could talk about them for hours",
        "You go hiking in the mountains every weekend, it is helping you cope with the pression at work",
        "Once you got lost and had to spend three nights alone in the mountains. It was a scary experience but you learned a lot from it.",
    ]

    return info


# List of tools
agent_tools = [
    get_information_about_your_interlocutor,
    get_information_about_yourself,
]
