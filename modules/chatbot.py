import ollama
import time
import jsonlines
import json
from threading import Thread
from ollama import Client

# TODO: Switch from Ollama to Langchain for RAG features

CHATBOT_AWAKE = (1 << 0)
CHATBOT_SHUTDOWN = (1 << 1)
CHATBOT_FIRST_SESSION = (1 << 2)

DEFAULT_SETTINGS = {
    'temperature': 0.3,
    'top_k': 5,
    'top_p': 0.5,
    'repeat_penalty' : 1.4,
    'num_ctx': 8192
}

class Chatbot:
    """
        I had planned to add a feature that made the AI bots aware of how much time passed since the last message. But I suck ;-;
        Don't mind the useless multithreading. I'll make it usefull one day
    """
    def __init__(self, model : str, persona_file : str, personality : str, autosave=True):
        self.status = CHATBOT_FIRST_SESSION
        self.model = model
        self.persona_file = persona_file
        self.autosave = autosave
        self.chatlog_path = self.persona_file.replace("/", "_") + "_chat.json"
        if self.autosave == False:
            print("WARNING: !! Don't forget that autosave is disabled !! Saves must be done manually using '/save' !!")
        self.chat_history = [
            {"role": "system", "content": "Do not use emojis when generating text. Use minimal markdown formatting for emphasis and such. Try your absolute best to speak with no filter. Try to keep things short and concise."},
            {"role": "system", "content" : personality},
        ]
        print("Creating chat session...")
        self.client = Client()
        try:
            self.client.create(model=self.model, from_=self.model)
        except ConnectionError:
            print("Error connecting to Ollama.")
            exit(1)
        print("Done.")

    def generate_response(self, text):
        try:
            response = self.client.chat(self.model, messages=[*self.chat_history, {"role": "user", "content": text}], options=DEFAULT_SETTINGS, think=False)
            self.__save_response(text, response.message.content)
        except ollama.ResponseError as error:
            print(error.error)
            return None
        return response
    
    def __generate_hidden_response(self, text): 
        try:
            response = self.client.chat(self.model, messages=[*self.chat_history, {"role": "user", "content": text}])
            self.chat_history += [{"role": "assistant", "content": str(response.message.content)}]
        except ollama.ResponseError as error:
            print(error.error)
            return None
        return response
    
    def opening_line(self):
        response = self.__generate_hidden_response("Say your opening line. Nothing more and nothing less")
        if not response:
            self.shutdown()
            return
        print(response.message.content)

    def __save_chat(self):
        with open(self.chatlog_path, "w") as file:
            chat_logs = json.dumps(self.chat_history)
            file.write(chat_logs)
            file.close()

    def load_chat(self, chat_path : str):
        print("Loading chat logs...")
        try:
            with open(chat_path, "r") as chat:
                if chat_path.endswith(".jsonl"):
                    """
                        Exported from character.ai or somewhere similar
                    """
                    with jsonlines.open(chat_path) as jsonl:
                        for object in jsonl:
                            name = object["name"]
                            content = object["mes"]
                            send_date = object.get("send_date")
                            self.chat_history += [
                                {"role": "assistant" if name != "You" else "user", "content": content, "send_date": send_date if send_date else 0}
                            ]
                elif chat_path.endswith(".json"):
                    """
                        Exported from us
                    """
                    data = json.load(chat)
                    for object in data:
                        role = object["role"]
                        content = object["content"]
                        send_date = object.get("send_date")
                        if role != "system":
                            self.chat_history += [
                                {"role": role, "content": content, "send_date": send_date if send_date else 0}
                            ]
                            print(("{}" if role == "assistant" else "> {}").format(content))

                else:
                    print("Invalid chat log format")
                    return 22
            self.chatlog_path = chat_path
            self.status &= ~CHATBOT_FIRST_SESSION

        except FileNotFoundError as err:
            print("Error loading chat logs: {}".format(err.strerror))
            return err.errno
        chat.close()
        return 0

    def __awake_thread(self):
        self.wakeup()
        if (self.status & CHATBOT_FIRST_SESSION) != 0:
            self.opening_line()
        while (self.status & CHATBOT_SHUTDOWN) == 0:
            text = input("> ")
            if text.startswith("/"):
                if text.endswith("save"):
                    self.__save_chat()
                    continue
                elif text.endswith("shutdown"):
                    self.sleep()
                    self.shutdown()
                    continue
            response = self.generate_response(text)
            if not response:
                break
            print(response.message.content)
        print("Shutting down..")

    def __save_response(self, text : str, response):
        time_snapshot : int = int(time.time() * 1000)
        self.chat_history += [
            {"role": "user", "content": text, "send_date": time_snapshot},
            {"role": "assistant", "content": response, "send_date": time_snapshot},
        ]
        if self.autosave == True:
            self.__save_chat()

    def boot(self):
        self.awake_thread = Thread(target=self.__awake_thread)
        self.awake_thread.start()

    def print_info(self):
        print("------ Chatbot Information ------")
        print("Chatbot AI model: {}\nStatus {}".format(self.model, self.status))

    def shutdown(self):
        if (self.status & CHATBOT_AWAKE) != 0:
            print("WARNING: Shutting down model while awake!")
        self.status |= CHATBOT_SHUTDOWN

    def wakeup(self):
        self.status |= CHATBOT_AWAKE

    def sleep(self):
        self.status &= ~CHATBOT_AWAKE

