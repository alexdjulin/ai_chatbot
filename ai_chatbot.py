import os
from time import sleep
import helpers
import keyboard
import threading
import re
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from terminal_colors import CYAN, RED, GREEN, GREY, RESET, CLEAR

# import config and create logger
from config_loader import config
from logger import get_logger
LOG = get_logger(os.path.splitext(os.path.basename(__file__))[0])

# load settings from config file
CHATBOT_NAME = config['chatbot_name']
USER_NAME = config['user_name']
CHAT_HISTORY_CSV = config['chat_history']
LOG_FILE = config['log_filepath']

# create log folder if needed
os.makedirs(os.path.dirname(CHAT_HISTORY_CSV), exist_ok=True)


class AiChatbot:
    '''
    This class defines an AI chatbot to converse with.
    '''

    def __init__(self) -> None:
        '''
        Create class instance
        '''

        # flags
        self.recording = False
        self.exit_chat = {'value': False}  # use a dict to pass flag by reference to helpers

        # thread object to handle chat tasks
        self.chat_thread = None

    def chat_with_avatar(self) -> None:
        '''Starting point to chat with the avatar.'''

        # define keyboard event to exit chat at any time
        keyboard.on_press_key("esc", self.on_esc_pressed)

        print(f'\n{GREY}Starting chat, please wait...{RESET}')
        helpers.write_to_csv(CHAT_HISTORY_CSV, 'NEW CHAT', timestamp=True)

        print(f'\n{CYAN}# CHAT START #{RESET}')

        # LANGCHAIN SETUP
        # create openai model and link it to tools
        llm_gpt4 = ChatOpenAI(model=config['openai_model'], api_key=config['openai_api_key'])

        # create prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", ("You are a helpful assistant answering questions."))
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

        # create message history
        messages = []

        if self.exit_chat['value']:
            # exit program before starting chat if esc was pressed during setup
            exit()

        print(f'\n{RED}{USER_NAME}:{RESET}')

        if config['use_text']:
            while not self.exit_chat['value']:
                # get user message
                new_message = input()
                if new_message.strip() == '':
                    # skip empty message or only spaces
                    continue
                if new_message in {'quit', 'exit'}:
                    # raise exit flag and exit loop on keywords
                    self.exit_chat['value'] = True
                    break
                # send message to chatGPT and get answer on separate thread
                self.chat_thread = threading.Thread(target=self.generate_model_answer, args=[new_message])
                self.chat_thread.start()

        else:
            if config['use_keyboard']:
                # define keyboard event to trigger audio inpout
                keyboard.on_press_key("space", self.on_space_pressed)

                while not self.exit_chat['value']:
                    sleep(1)  # wait 1 second before checking again

            else:
                # use direct chat input
                while not self.exit_chat['value']:
                    if self.recording is False:
                        # start a new record thread
                        self.chat_thread = threading.Thread(target=self.record_message)
                        self.chat_thread.start()
                    sleep(1)  # wait 1 second before checking again

        # stop keyboard listener
        keyboard.unhook_all()

        # wait for chat thread to finish
        if self.chat_thread and self.chat_thread.is_alive():
            self.chat_thread.join()

        print(f'\n{CYAN}# CHAT END #{RESET}')

    def on_space_pressed(self, e) -> None:
        ''' When space is pressed, start a thread to record your voice and send message to chatGPT '''
        if e.event_type == keyboard.KEY_DOWN and self.recording is False:
            self.chat_thread = threading.Thread(target=self.record_message)
            self.chat_thread.start()

    def on_esc_pressed(self, e) -> None:
        ''' When esc is pressed, raise exit_flag to terminate chat and any chat thread running '''
        if e.event_type == keyboard.KEY_DOWN and not self.exit_chat['value']:
            LOG.debug('Raising exit flag to terminate chat')
            self.exit_chat['value'] = True
            message = 'Ending chat, please wait...' if self.input == 'voice' else 'Ending chat, PRESS ENTER to close'
            print(f'{CLEAR}{GREY}{message}{RESET}', flush=True)

    def record_message(self) -> None:
        ''' Record voice and transcribe message '''

        self.recording = True

        new_message = helpers.record_voice(self.exit_chat)

        # Process new message on success or ask user to try again if no message was recorded
        if new_message:
            self.generate_model_answer(new_message)
        else:
            self.recording = False

    def generate_model_answer(self, message: str) -> None:
        '''Send new message and get answer from the LLM.

        Args:
            message (str): message to send to the LLM
        '''

        # print message in speech mode
        if not config['use_text']:
            print(f'{CLEAR}{message.capitalize()}')

        # add message to prompt and chat history
        self.messages.append(HumanMessage(content=message))
        helpers.write_to_csv(CHAT_HISTORY_CSV, USER_NAME, message, timestamp=True)

        # print avatar feedback
        print(f'\n{CLEAR}{GREEN}{CHATBOT_NAME}:{RESET}')
        print(f'{CLEAR}{GREY}(generate){RESET}', end=' ', flush=True)

        # get answer and tokens count, add it to prompt
        answer, tokens = helpers.generate_llm_answer(messages=self.messages)
        self.prompt_tokens += tokens[0]
        self.completion_tokens += tokens[1]

        # format answer
        sentences = re.split(r"(?<=[.!?])\s", answer)
        answer = ' '.join([sentence.strip().capitalize() for sentence in sentences])

        # add answer to prompt and chat history
        self.messages.append({"role": "assistant", "content": answer})
        helpers.write_to_csv(CHAT_HISTORY_CSV, CHATBOT_NAME, answer, timestamp=True)

        if self.output == 'talk':
            # generate tts
            print(f'{CLEAR}{GREY}(transcribe){RESET}', end=' ', flush=True)
            helpers.generate_tts(text=answer)

        else:
            # print answer
            print(f'{CLEAR}{answer}')

        # prompt for a new chat
        self.recording = False
        print(f'\n{RED}{USER_NAME}:{RESET}')
