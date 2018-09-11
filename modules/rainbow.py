from discord.ext import commands
from discord import utils as discord_utils
from discord import Embed
from discord import Colour, Role

import json

ddb = 'data/colourstore.json'


def add_colour_to_db(server, name):
    with open(ddb, 'r+') as f:
        data = json.load(f)
        if server not in data:
            data[server] = [name]
        else:
            data[server].append(name)
        f.seek(0)
        json.dump(data, f, indent=4, sort_keys=True)
        f.truncate()


def get_server_colours(server):
    with open(ddb, 'r') as f:
        data = json.load(f)
        return data[server]


def check_for_existing_colour(user_roles, server):
    server_colours = get_server_colours(server)

    for role in user_roles:
        if role.name in server_colours:
            return role.name
    else:
        return False


class Rainbow:

    def __init__(self, bot):
        self.bot = bot

    async def add_c(self, server, name, c):
        value = c.strip('#')
        value = value.strip('0x')
        value = int(value, 16)
        value = hex(value)
        colour = Colour(value)
        await self.bot.create_role(server, name=name, colour=colour)
        add_colour_to_db(server.id, name)

    @commands.command(pass_context=True, aliases=['add_color'], help='Creates a new colour role.')
    async def add_colour(self, ctx, name, c):
        server = ctx.message.channel.server
        self.add_c(server, name, c)

    @commands.command(pass_context=True, aliases=['color_user'], help='Sets user colour.')
    async def colourme(self, ctx, colour):
        server = ctx.message.channel.server
        user = ctx.message.author

        user_has_colour = check_for_existing_colour(user.roles, server.id)

        if any(r.name == colour for r in user.roles):
            await self.bot.say("You already have this colour!")
        elif user_has_colour:
            old_colour = discord_utils.get(server.roles, name=user_has_colour)
            await self.bot.remove_roles(user, old_colour)

            new_colour = discord_utils.get(server.roles, name=colour)
            await self.bot.add_roles(user, new_colour)

        else:
            role_object = discord_utils.get(server.roles, name=colour)
            await self.bot.add_roles(user, role_object)

    @commands.command(pass_context=True, hidden=True)
    async def init_default_colours(self, ctx):
        server = ctx.message.channel.server
        defs = {
            "default": Colour.default(),
            "dark blue": Colour.dark_blue(),
            "dark gold": Colour.dark_gold(),
            "dark green": Colour.dark_green(),
            "dark grey": Colour.dark_grey(),
            "dark magenta": Colour.dark_magenta(),
            "dark orange": Colour.dark_orange(),
            "dark purple": Colour.dark_purple(),
            "dark red": Colour.dark_red(),
            "dark teal": Colour.dark_teal(),
            "darker grey": Colour.darker_grey(),
            "blue": Colour.blue(),
            "gold": Colour.gold(),
            "green": Colour.green(),
            "magenta": Colour.magenta(),
            "red": Colour.red(),
            "teal": Colour.teal(),
            "orange": Colour.orange(),
            "purple": Colour.purple(),
            "light grey": Colour.light_grey(),
            "lighter grey": Colour.lighter_grey()
        }
        for key, value in defs.items():
            await self.bot.create_role(server, name=key, colour=value, mentionable=False)
            add_colour_to_db(server.id, key)


def setup(bot):
    bot.add_cog(Rainbow(bot))
