# TelegramBot

In this repository you will find Telegram Bot scripted using `python-telegram-bot` library.

## Repository Structure
Each Bot code is stored in a different subfolder.

In each subfolder must be created also a `config.yml` with `API` key where bot API key must be stored.
In this yaml file can be stored other useful informations.


## Main classes
The only objects in common with each bot will be classes `Bot` and `BotRunner` stored `Bot.py`

### Bot
This is the mother class that will be used to create other Bot classes as children.
Nothing important expect for 3 abstractmethod that must be included in each Bot class:
- `_set_handlers`:
    A method where dictionary `self._handlers` must be initialized. See `Bot` class for details.
- `_start`:
    The command that is launched when bot is started
- `_help`:
    An help function to help the user


### BotRunner
This class takes care of run Bot class.


```
### Exaple
from TelegramBot.Bot import BotRunner

# initialize bot
bot = WhateverBot()

# run it
bot_runner = BotRunner(bot)
bot_runner.run()

```


## Repo Structure
Each Bot code is stored in a different subfolder.
In each subfolder must be created also a `config.yml` containing `API` key where Bot API will be stored.
In this yaml file can be stored 
