### discord-ext-help

An extension to create an interaction based Help Menu.

**There are no front-facing docs for this and it's not on PyPI.**

## Installing

Installing is done purely via git:

```py
python -m pip install -U git+https://github.com/Mayerch1/discord-ext-help
```

## Getting Started

To setup a basic help-page, the extension needs to be loaded as cog.
Execute the following before starting the bot.

To automatically detect slash commands, the extension should be loaded at last.
Before starting the bot, `init_help` should be called.

```py
import discord
from discord.ext.help import Help

bot = discord.Bot(...)
# ...
bot.load_extension('discord.ext.help.help')

Help.init_help(bot, auto_detect_commands=True)
bot.run(TOKEN)
```

To offer some more options, certain attributes can be set.
These attributes unlock more help buttons.

```py
Help.set_default_footer(custom_footer)
Help.set_feedback(FEEDBACK_CHANNEL, FEEDBACK_MENTION)
Help.invite_permissions(
    discord.Permissions(attach_files=True)
)
Help.support_invite('<invite url>')
Help.set_tos_file('legal/tos.md')
Help.set_privacy_file('legal/privacy.md')
```

If an error happens then an exception of type `HelpException` is raised.

This second example shows how to create a custom help page:
This can be used with or without automatic command detection.

The extension will add pagination once more than one field is shown

```py
from discord.ext import menus

elements = [
    HelpElement(cmd_name='/help', description='show this message'),
    HelpElement(cmd_name='/fuel time', description='use this for time limited races'),
    HelpElement(cmd_name='/fuel laps', description='use this for lap limited races')
]
page = HelpPage(
    name='parameters',
    title='QuoteBot Help',
    description='Explain command parameters',
    elements=elements,
    emoji='✏️'
)
Help.add_page(page)
```
