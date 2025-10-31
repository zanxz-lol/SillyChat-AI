#!/usr/bin/python3

import argparse
from modules.chatbot import Chatbot

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SillyChat AI: Talk with your favorite characters using AI!")

    parser.add_argument("-p", "--persona", type=str, help="Persona file of the character you wanna chat with.")
    parser.add_argument("-c", "--chat", type=str, help="Previous chat logs to load.")
    parser.add_argument("--no-autosave", action="store_false", help="Disables autosaving chat logs")

    args = parser.parse_args()

    try:
        if not args.persona:
            print("Persona not specified. Defaulting to generic AI assistant..")
        persona_file = open(args.persona if args.persona else "personas/generic_ai", "r")
        bot = Chatbot("artifish/llama3.2-uncensored", persona_file.name, persona_file.read(), autosave=args.no_autosave)
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
