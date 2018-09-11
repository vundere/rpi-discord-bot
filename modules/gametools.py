from discord.ext import commands

from datetime import datetime as dt


day_table = {
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday',
    7: 'Sunday'
}


class Gametools:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def xur(self):
        now = dt.now()
        day = dt.isoweekday(now)
        hour = now.hour
        minute = now.minute
        if day not in [6, 7, 1]:
            if day == 5:
                if hour < 18:
                    tstr = '{} hour(s) and {} minutes'.format((18 - hour), (60 - minute))
                    await self.bot.say('Xûr will arrive in {}'.format(tstr))
                else:
                    await self.bot.say('Xûr is already here!')
                pass
            elif day == 2:
                pass
        pass


def setup(bot):
    bot.add_cog(Gametools(bot))
