import os
from ai_chatbot import AiChatbot
from logger import get_logger
import argparse
from terminal_colors import CYAN, RESET

# create logger
LOG = get_logger(os.path.splitext(os.path.basename(__file__))[0])


if __name__ == '__main__':

    # create avatar instance
    avatar = AiChatbot()
    avatar.chat_with_avatar()
    
