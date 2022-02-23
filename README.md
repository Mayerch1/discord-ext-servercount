### discord-ext-servercount

An extension to update the servercount of popular bot lists.

**There are no front-facing docs for this and it's not on PyPI.**

## Installing

Installing is done purely via git:

```py
python -m pip install -U git+https://github.com/Mayerch1/discord-ext-servercount
```

## Getting Started

To setup a basic help-page, the extension needs to be loaded as cog.
Execute the following before starting the bot.

To automatically detect slash commands, the extension should be loaded at last.
Before starting the bot, `init` should be called.

```py
import discord
from discord.ext.servercount import ServerCount

bot = discord.Bot(...)
# ...
bot.load_extension('discord.ext.servercount.servercount')

ServerCount.init(bot, user_agent='myBot (<url>)')
bot.run(TOKEN)
```

To set tokens for the bot lists, use the following functions.

```py
ServerCount.set_token(bot_list: BotLists, token: str)
# and/or
ServerCount.set_token_dir(dir: str)
```
When specifying a single token, one of the supported Services must be used
```py
class BotLists(Enum):
    TopGG
    BotsGG
    DBL
    Discords
    Disforge
    DLSpace
```

When using `set_token_dir`, the extension searches the inter directory (non-recursive) for text files.
Each token must be in a file, which matches it's name identical to one of the services in the `BotLists`-Enum.

If the same token is specified multiple times (e.g. once in `set_token` and once in `set_token_dir`), the last set operation will be rememberd.


### NOTE
For security reasons, it is recommended to **NOT** use `set_token_dir`. Store your tokens in a secure credential store instead and use `set_token` for each token.
