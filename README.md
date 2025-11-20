# SillyChat: An AI app with silly personas to chat with

SillyChat is a simple and open-source AI chatting app built with Python using the Ollama API.

## What can you do with SillyChat as of now?

As of right now, you can save chat logs, load chat logs, and choose nine different personas to chat with.

## That's nice and all, but how do I work with this app?

To get this working, you need to install Ollama on your system, and the Ollama python module

```
pip install ollama
```

Whatever module errors that come up, try installing the missing modules. This isn't really the ideal way of installing all the necessary modules, but I'll get a requirements.txt file up soon.

## How can I save/load chat logs?

Chat logs are automatically saved, but if you pass the ``--no-autosave`` argument, then you'll have to save the chat logs manually. To save chat logs manually, while in the chat, type the following:
```
/save
```
To load chat logs, simply pass the ``--chat`` or ``-c`` parameter with the path to the chat logs. Be sure to load the correct persona with the chat logs. The chat log file has the persona in the name so you can easily determine what persona to use. For example:
```
python scai.py --chat example.json
```
## That's nice and all, but how do I pick a persona?

To pick a persona, simply pass the ``--persona`` or ``-p`` parameter with the path to the persona file. If no persona is specified, it will load the generic_ai persona by default. For example:
```
python scai.py --persona personas/ye
```
