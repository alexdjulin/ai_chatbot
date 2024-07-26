#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filename: helpers.py
Description: Define here all methods to be used in the main script.
Example: SST, TTS, CSV read/write, LLM completion, etc.
Author: @alexdjulin
Date: 2024-07-25
"""

from logger import get_logger
from datetime import datetime
from time import sleep
import edge_tts
import asyncio
from pydub import AudioSegment
from pydub.playback import play
from playsound import playsound
import csv
import os
from textwrap import dedent
import speech_recognition as sr
from langchain_core.runnables.base import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from terminal_colors import GREY, RESET, CLEAR

from config_loader import config
LOG = get_logger(os.path.splitext(os.path.basename(__file__))[0])


def format_string(prompt: str) -> str:
    '''
    Removes tabs, line breaks and extra spaces from strings. This is useful
    when formatting prompts to send to chatGPT or to save to a csv file

    Args:
        prompt (str): prompt to format

    Return:
        (str): formatted prompt
    '''

    # remove tabs and line breaks
    prompt = dedent(prompt).replace('\n', ' ').replace('\t', ' ')

    # remove extra spaces
    while '  ' in prompt:
        prompt = prompt.replace('  ', ' ')

    return prompt.strip()


def load_from_csv(csvfile: str) -> dict:
    '''
    Loads question and answers from csv file into a dict

    Args:
        csvfile (str): path to csv file

    Return:
        (dict): dict with question and answers

    Raises:
        Exception: if error reading csv file
    '''

    qna_dict = {}

    try:
        with open(csvfile, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # store avatar name
            qna_dict["What's your name?"] = f"My name is {config['avatar_name']}."
            for row in reader:
                question, answer = row
                qna_dict[question] = answer
            LOG.debug(f"Answers have been read from {csvfile}.")

    except Exception as e:
        LOG.error(f"Error reading from CSV file: {e}")
        print(f'{GREY}Failed to load avatar story (see log).{RESET}')

    return qna_dict


def write_to_csv(csvfile: str, *strings: list, timestamp: bool = False) -> bool:
    '''
    Adds strings to a csv file on a new row

    Args:
        csvfile (str): path to csv file
        *strings (list): strings to add as columns to csv file
        timestamp (bool): first column should be a timestamp

    Return:
        (bool): True if successful, False otherwise

    Raises:
        Exception: if error writing to csv file
    '''

    try:
        with open(csvfile, mode='a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, doublequote=True)
            # remove tabs, line breaks and extra spaces
            safe_strings = [format_string(s) for s in strings]
            if timestamp:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                safe_strings = [timestamp] + safe_strings
            csv_writer.writerow(safe_strings)

    except Exception as e:
        LOG.error(f"Error writing to CSV file: {e}")
        return False

    return True


def build_chain() -> RunnableSequence:
    '''Define the langchain chain to chat with the avatar.

    Return:
        (RunnableSequence): chain instance
    '''

    # create openai model and link it to tools
    llm_gpt4 = ChatOpenAI(model=config['openai_model'], api_key=config['openai_api_key'])

    # create prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant answering questions."),
            ("system", "Keep your answers short and straight to the point. Never use more than 2 or 3 sentences."),
            ("ai", "Hello! I am your helpful assistant. How can I help you today?"),
            ("human", "Give me a good French comedy."),
            ("ai", "Sure! How about 'Amélie'?"),
            ("human", "Do you know the height of the Eiffel Tower?"),
            ("ai", "Sure, the Eiffel Tower is 324 meters tall."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
        ]
    )

    # create string output parser
    str_output_parser = StrOutputParser()

    # create chain
    chain = prompt | llm_gpt4 | str_output_parser

    return chain


def generate_tts(text: str) -> None:
    '''
    Generates audio from text using edge_tts API and plays it

    Args:
        text (str): text to generate audio from
    '''

    voice = config['edgetts_voice']
    audio_file = config['temp_audio_file']

    async def text_to_audio() -> None:
        """ Generate speech from text and save it to a file """
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(audio_file)

    # generate audio data
    try:
        asyncio.run(text_to_audio())

    except Exception as e:
        LOG.error(f"Error generating and playing audio: {e}. Voice deactivated.")
        # print answer and exit
        print(f'{CLEAR}{text}')
        return

    # print answer
    print(f'{CLEAR}{text}')

    # play and delete audio file
    audio = AudioSegment.from_file(audio_file)
    play(audio)

    # deleve temporary audio file
    os.remove(audio_file)


def record_audio_message(exit_chat) -> str | None:
    '''Record voice and return text transcription.

    Args:
        exit_chat (dict): chat exit flag {'value': bool} passed by reference as mutable dicts so it 
        can be modified on keypress and updated here.

    Return:
        (str | None): text transcription

    Raises:
        UnknownValueError: if audio could not be transcribed
        RequestError: if error connecting to Google API
    '''

    text = ''
    language = config['chat_language']
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    try:

        with microphone as source:

            print(f"{CLEAR}{GREY}(listening){RESET}", end=' ', flush=True)
            timeout = config['speech_timeout']
            audio = recognizer.listen(source, timeout=timeout)

            print(f"{CLEAR}{GREY}(transcribing){RESET}", end=' ', flush=True)
            text = recognizer.recognize_google(audio, language=language)

            if not text:
                raise sr.UnknownValueError

            return text.capitalize()

    except sr.WaitTimeoutError:
        if config['use_keyboard']:
            print(f"{CLEAR}{GREY}Can't hear you. Please try again.{RESET}", end=' ', flush=True)
        else:
            if not exit_chat['value']:
                # start listening again
                record_audio_message(language, exit_chat)

    except sr.UnknownValueError:
        print(f"{CLEAR}{GREY}Can't understand audio. Please try again.{RESET}", end=' ', flush=True)
        sleep(2)

    except sr.RequestError:
        print(f"{CLEAR}{GREY}Error connecting to Google API. Please try again.{RESET}", end=' ', flush=True)
        sleep(2)

    return None
