import os
import requests
import json
import logging
from enum import Enum

import discord
from discord.ext import commands, tasks

log = logging.getLogger('ext.servercount')

class ServerCountException(Exception):
    pass


class BotLists(Enum):
    TopGG = 'TopGG'
    BotsGG = 'BotsGG'
    DBL = 'DBL'
    Discords = 'Discords'
    Disforge = 'Disforge'
    DLSpace = 'DLSpace'


class BotListService:
    def __init__(self, name: BotLists, api_base, api_path, server_cnt_name=None, shard_cnt_name=None, shard_id_name=None):
        self.name: BotLists = name
        self.api_base = api_base
        self.api_path = api_path
        
        self.server_cnt_name = server_cnt_name
        self.shard_cnt_name = shard_cnt_name
        self.shard_id_name = shard_id_name


ServerList = [
    BotListService(
        name=BotLists.TopGG,
        api_base='https://top.gg/api',
        api_path='/bots/{:s}/stats',
        server_cnt_name='server_count',
        shard_cnt_name='shard_count',
        shard_id_name='shard_id'
    ),
    BotListService(
        name=BotLists.BotsGG,
        api_base='https://discord.bots.gg/api/v1',
        api_path='/bots/{:s}/stats',
        server_cnt_name='guildCount',
        shard_cnt_name='shardCount',
        shard_id_name='shardId'
    ),
    BotListService(
        name=BotLists.DBL,
        api_base='https://discordbotlist.com/api/v1',
        api_path='/bots/{:s}/stats',
        server_cnt_name='guilds',
        shard_id_name='shard_id'
    ),
    BotListService(
        name=BotLists.Discords,
        api_base='https://discords.com/bots/api',
        api_path='/bot/{:s}',
        server_cnt_name='server_count'
    ),
    BotListService(
        name=BotLists.Disforge,
        api_base='https://disforge.com/api',
        api_path='/botstats/{:s}',
        server_cnt_name='servers'
    ),
    BotListService(
        name=BotLists.DLSpace,
        api_base='https://api.discordlist.space/v2',
        api_path='/bots/{:s}',
        server_cnt_name='serverCount'
    ),
]

class ServerCount(commands.Cog):

    # redirect to modified/injected Cog scope
    cog_class: 'ServerCount'
    is_cog_scope:bool =False

    tokens: dict[str] = {} # key is BotLists enum
    token_dir:str = None
    user_agent:str = 'ext.discord.servercount'

    @staticmethod
    def init(client: discord.Bot, user_agent):
        """init internal variables used to hide PyCord complexity
           must be called *after* adding this class to extension
           but *before* the bot initializes the Cog (bot.run())
        Args:
            client (discord.Bot): discord Client/Bot
        """
        # pycord modifies the Help class scope when loading it as Cog
        # therefore, class attributes cannot directly be set/modified
        # (the id of the class changes -> class attrs are not shared)

        # the modified Cog-class can be retrieved by using the client
        # therefore it is saved into the unmodified class variables

        # the cog-modified class can be retrieved from the client
        # to hide this workaround from the user
        if 'discord.ext.servercount.servercount' not in client.extensions:
            raise ServerCountException('ServerCount Cog not added to client. Use .load_extension(\'discord.ext.servercount.servercount\')')
        cog_class: ServerCount = client.extensions['discord.ext.servercount.servercount'].ServerCount
        ServerCount.cog_class = cog_class

        ServerCount.cog_class.user_agent = user_agent


    @staticmethod
    def set_token(bot_list: BotLists, token: str):
        """add a token to the ServerCount process
           this must be called before bot is started, but after init

        Args:
            bot_list (BotLists): BotList service
            token (str): token
        """
        if ServerCount.is_cog_scope:
            tokens = ServerCount.tokens
        else:
            tokens = ServerCount.cog_class.tokens

        tokens[bot_list.value] = token
        log.info(f'starting {bot_list.value} job, {len(tokens)}/{len(ServerList)} lists have a token')


    @staticmethod
    def set_token_dir(dir: str):
        """set a directory for token files
           the filename for each token must match the BotLists enum exactly

           this must be called before bot is started, but after init

        Args:
            dir (str): path to token directory
        """
        if ServerCount.is_cog_scope:
            tokens = ServerCount.tokens
        else:
            tokens = ServerCount.cog_class.tokens

        log.info(f'token folder was set to {dir}')
        # init all server objects
        for sList in ServerList:
            key = sList.name.value
            if os.path.exists(f'{dir}/{key}.txt'):
                tokens[key] = open(f'{dir}/{key}.txt', 'r').readline()[:-1]
                
                if tokens[key]:
                    log.info(f'starting {key} job')
                else:
                    log.warning(f'found {key} config, but token is empty')
            else:
                log.debug(f'ignoring {key}, no Token')


    def __init__(self, client):
        self.client: discord.AutoShardedBot = client
        self.serverList = ServerList
        self.skip_first_iteration = True
        self.post_loop.start()



    def cog_unload(self):
        log.info('stopping all servrecount jobs')
        self.post_loop.cancel()


    async def post_count(self, service: BotListService, payload):
        """post the payload to the given service
           token MUST be set in service
        Args:
            service (BotListService): [description]
            payload ([type]): [description]
        """

        url = service.api_base + service.api_path.format(str(self.client.user.id))
        
        headers = {
            'User-Agent'   : ServerCount.user_agent,
            'Content-Type' : 'application/json',
            'Authorization': ServerCount.tokens[service.name.value]
        }

        payload = json.dumps(payload)

        r = requests.post(url, data=payload, headers=headers, timeout=5)

        if r.status_code >= 300:
            log.info(f'{service.name} Server Count Post failed with {r.status_code}')



    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""

        server_count = len(self.client.guilds)
        log.info(f'posting {server_count} servers')


        for sList in self.serverList:
            
            if sList.name.value not in ServerCount.tokens:
                continue
            
            cnt_name = sList.server_cnt_name
            shard_name = sList.shard_cnt_name
            id_name = sList.shard_id_name

            payload = {
                f'{cnt_name}': server_count
            }

            if self.client.shard_count and shard_name:
                payload[shard_name] = self.client.shard_count
            if self.client.shard_id and id_name:
                payload[id_name] = self.client.shard_id

            await self.post_count(sList, payload=payload)


    @tasks.loop(hours=1)
    async def post_loop(self):
        if self.skip_first_iteration:
            self.skip_first_iteration = False
            return
        await self.update_stats()
  

    @post_loop.before_loop
    async def start_loop(self):
        await self.client.wait_until_ready()


    @discord.Cog.listener()
    async def on_ready(self):
        log.info('ext.servercount loaded')


def setup(client):
    client.add_cog(ServerCount(client))
