#!/usr/bin/python3

import sys
import argparse
from modules.chatbot import Chatbot

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Talk with your favorite characters using AI!")

    parser.add_argument("-p", "--persona", type=str, help="Persona file of the character you wanna chat with.")
    parser.add_argument("-c", "--chat", type=str, help="Previous chat logs to load.")

    args = parser.parse_args()

    try:
        if not args.persona:
            print("Persona not specified. Defaulting to generic AI assistant..")
        persona_file = open(args.persona if args.persona else "personas/generic_ai", "r")
        bot = Chatbot("artifish/llama3.2-uncensored", persona_file.name, persona_file.read())
        persona_file.close()
    except FileNotFoundError as err:
        print("Error loading persona file: {}".format(err.strerror))
        exit(1)

    if args.chat:
        rc = bot.load_chat(args.chat)
        if rc != 0:
            exit(rc)       

    bot.boot()
    try:
        bot.awake_thread.join()
    except KeyboardInterrupt:
        bot.shutdown()
        bot.awake_thread.join()
