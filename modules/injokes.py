from discord.ext import commands
from utils import tools
import json


class Injokes:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Correctly places blame.', pass_context=True,
                      description='Pretty self-explanatory when you use it.')
    async def blame(self, ctx):
        user = str(ctx.message.author.id)
        if user == '153497617144217600':
            return await self.bot.say("It's your fault, dingus!")
        if user == '187724282888060930':
            return await self.bot.say("It's definitely not vun's fault.")
        else:
            return await self.bot.say("It's all Jax' fault.")

    @commands.command(help="Number of Jenson rips", description="The number of times Jenson has said 'rip' since this "
                                                                "command was implemented.",
                      aliases=["ripcounter", "rip"], pass_context=True)
    async def ripcount(self, ctx):
        if ctx.message.server.id == "321067467243782144":
            with open(self.bot.data_file, 'r') as f:
                data = json.load(f)
                count = data.get("rip", 0)
                user = tools.find_member(self.bot, "133237258668081152")
            return await self.bot.say("{0} has said 'rip' {1} times".format(user.display_name, str(count)))
        else:
            return await self.bot.say("This command is not yet set up for this server.")


def setup(bot):
    bot.add_cog(Injokes(bot))
