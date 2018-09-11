"""
Rudimentary ranking system inspired by DynoBot.
"""

from discord.ext import commands
from discord import utils as discord_utils
from discord import Embed

import json

ddb = 'data/rankstorage.json'


def add_rank(server, rank):
    with open(ddb, 'r+') as f:
        data = json.load(f)
        if server not in data:
            data[server] = {rank: 0}
        else:
            data[server][rank] = 0
        f.seek(0)
        json.dump(data, f, indent=4, sort_keys=True)
        f.truncate()


def remove_rank(server, rank):
    with open(ddb, 'r+') as f:
        data = json.load(f)
        try:
            del data[server][rank]

            f.seek(0)
            json.dump(data, f, indent=4, sort_keys=True)
            f.truncate()
        except KeyError:
            pass


def modify_count(server, rank, decrement=False):
    with open(ddb, 'r+') as f:
        data = json.load(f)
        old_count = int(data[server][rank])

        if decrement:
            new_count = old_count - 1
        else:
            new_count = old_count + 1

        data[server][rank] = new_count
        f.seek(0)
        json.dump(data, f, indent=4, sort_keys=True)
        f.truncate()

        if new_count == 0:
            # remove_rank(server, rank)
            # return False
            pass
        else:
            pass
            # return True


def get_ranks(server):
    with open(ddb, 'r') as f:
        data = json.load(f)
        return data[server]


def case_insensitive_find(server, rank):
    with open(ddb, 'r') as f:
        data = json.load(f)
        for r in data[server].keys():
            if r.lower() == rank.lower():
                return r
        return False


def truncate_name(name):
    if len(name) > 11:
        return '{}...{}'.format(name[:3], name[-3:])
    else:
        return name


class Ranks:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, help='Join or leave a rank.')
    async def rank(self, ctx, rank_name):
        server = ctx.message.channel.server
        user = ctx.message.author

        rank_exists = case_insensitive_find(server.id, rank_name)

        if rank_exists:
            rank_name = rank_exists
            role_object = discord_utils.get(server.roles, name=rank_name)

            if any(r.name == rank_name for r in user.roles):
                modify_count(server.id, rank_name, decrement=True)
                await self.bot.remove_roles(user, role_object)
                await self.bot.say("You have been removed from {}".format(rank_name))

                # if not remaining_members:
                #     await self.bot.delete_role(server, role_object)

            else:
                modify_count(server.id, rank_name)
                await self.bot.add_roles(user, role_object)
                await self.bot.say("You have been added to {}".format(rank_name))

        else:
            await self.bot.say("This rank does not exist!")

    @commands.command(pass_context=True, help='List all ranks and number of members.')
    async def ranks(self, ctx):
        surround = '```'
        base_str = ''
        data = get_ranks(ctx.message.channel.server.id)
        channel = ctx.message.channel

        col_len = 15
        # for key, value in data.items():
        #     if len(key) >= col_len:
        #         col_len = len(key) + 1
        for key, value in data.items():
            rank_name = truncate_name(key)
            base_str += '{0}{2}{1}\n'.format(
                rank_name,
                str(value).strip(),
                ' '*(col_len - len(rank_name) - len(str(value)))
            )

        final_str = base_str.rstrip()
        if final_str:
            payload = '{surround}{content}{surround}'.format(surround=surround, content=final_str)
        else:
            payload = 'Empty'

        embed = Embed(color=0xf400c5)
        embed.add_field(name='Ranks', value=payload)
        await self.bot.send_message(channel, embed=embed)

    @commands.command(pass_context=True, help='Add a new rank.')
    async def newrank(self, ctx, rank_name):
        server = ctx.message.channel.server

        rank_exists = case_insensitive_find(server.id, rank_name)
        if rank_exists:
            rank_name = rank_exists

        if not any(r.name == rank_name for r in server.roles):
            add_rank(server.id, rank_name)
            await self.bot.create_role(server, name=rank_name, mentionable=True)
            await self.bot.say("Rank {} created!".format(rank_name))
        else:
            await self.bot.say("This rank already exists!")

    @commands.command(pass_context=True, help='Deletes a rank.')
    async def delrank(self, ctx, rank_name):
        server = ctx.message.channel.server
        rank_exists = case_insensitive_find(server.id, rank_name)
        if rank_exists:
            rank_name = rank_exists

        role_object = discord_utils.get(server.roles, name=rank_name)
        remove_rank(server.id, rank_name)
        await self.bot.delete_role(server, role_object)
        await self.bot.say('Rank {} deleted!'.format(rank_name))

    @commands.command(pass_context=True, help='Assigns a number of members to a rank.')
    async def addrank(self, ctx, rank_name, *members):
        """
            The *members arg is just there to avoid errors; due to how messages work,
            we can't actually use them.
            Or, we can, but that would be far more complicated than this needs to be;
            all we need is the mentions list.
        """
        server = ctx.message.channel.server

        rank_exists = case_insensitive_find(server.id, rank_name)
        if rank_exists:
            rank_name = rank_exists

        if not any(r.name == rank_name for r in server.roles):
            add_rank(server.id, rank_name)
            await self.bot.create_role(server, name=rank_name, mentionable=True)

        for member in ctx.message.mentions:
            role_object = discord_utils.get(server.roles, name=rank_name)

            if not any(r.name == rank_name for r in member.roles):
                modify_count(server.id, rank_name)
                await self.bot.add_roles(member, role_object)

        await self.bot.say('Success!')


def setup(bot):
    bot.add_cog(Ranks(bot))
