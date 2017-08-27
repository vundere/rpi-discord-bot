import re
from discord.ext import commands
from utils import file_tools
from bot import is_mommy


class Memes:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Add a picture to the bot image folder.'
                                  'Either add this command as the comment to an uploaded image, '
                                  'or use this command with an url that ends in filename.extension',
                      pass_context=True, help='Add picture to meme pool', hidden=True)
    @commands.has_role('team')
    @commands.cooldown(3, 30.0, commands.BucketType.user)
    async def addmem(self, ctx):
        if not ctx.message.attachments:
            url = re.search("(?P<url>https?://[^\s]+)", ctx.message.content).group("url")
            filename = url.split('/')[-1]
        else:
            url = ctx.message.attachments[0]['url']
            filename = ctx.message.attachments[0]['filename']
        success = file_tools.save_mem(url, filename)
        if success:
            return await self.bot.say('Yoink! Image successfully purloined.')
        else:
            return await self.bot.say("Unable to download image. You're either unoriginal or can't understand what an "
                                      "image is, and I don't know which is worse.")

    @commands.command(help='Adds last posted image to meme pool.', pass_context=True,
                      description='Downloads the last image posted in the channel to the meme folder.'
                                  'Please refrain from adding heresy images to the meme folders, to avoid'
                                  'unnecessary duplicates.', hidden=True)
    @commands.has_role('team')
    @commands.cooldown(3, 30.0, commands.BucketType.user)
    async def yoink(self, ctx):
        # TODO simplify
        if not is_mommy(ctx):
            return await self.bot.say("Sorry, this command is currently not working as intended "
                                      "and unavailable until that's sorted.")

        def is_origin(context, cand):
            return context.message.channel == cand.channel
        async for message in self.bot.logs_from(ctx.message.channel, limit=200):
            url = re.search("(?P<url>https?://[^\s]+)", message.content)
            if is_origin(ctx, message):
                if url and not message.attachments:
                    url = url.group("url")
                    filename = url.split('/')[-1]
                    if file_tools.is_heresy(file_tools.discord_filename_fix(filename)):
                        return await self.bot.say('This can already be found in the available heretical material.')
                    else:
                        success = file_tools.save_mem(url, filename)
                        if success:
                            return await self.bot.say('Yoink! Image successfully purloined.')
                        else:
                            return await self.bot.say("Unable to download image. ")
                elif message.attachments:
                    url = message.attachments[0]['url']
                    filename = message.attachments[0]['filename']
                    if file_tools.is_heresy(file_tools.discord_filename_fix(filename)):
                        return await self.bot.say('This can already be found in the available heretical material.')
                    else:
                        success = file_tools.save_mem(url, filename)
                        if success:
                            return await self.bot.say('Yoink! Image successfully purloined.')
                        else:
                            return await self.bot.say("Unable to download image. ")

    @commands.command(description='Posts an image of toebeans',
                      help='Posts an image of toebeans')
    async def beans(self):
        # TODO more beans
        return await self.bot.upload('static/6YWo7Kr.jpg')

    @commands.command(description='What the fuck do you think this does?',
                      help='What the fuck do you think this does?', hidden=True)
    async def memes(self):
        img = file_tools.get_rand_mem()
        return await self.bot.upload(img)

    @commands.command(description='KEKS FOR THE KEK THRONE', help='MEMES FOR THE MEME GOD')
    async def heresy(self):
        heretical_material = file_tools.get_heresy()
        return await self.bot.say(heretical_material)

    @commands.command(description='Posts an Overwatch-related image', help='Posts an Overwatch-related image')
    async def ow(self):
        result = file_tools.get_watched()
        return await self.bot.say(result)


def setup(bot):
    bot.add_cog(Memes(bot))
