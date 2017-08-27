from discord.ext import commands

import asyncio


class Vote(object):
    def __init__(self, name, votemax):
        self.name = name
        self.votemax = votemax
        self.votes = 0
        self.voters = []

    def incr(self):
        if self.votes < self.votemax:
            self.votes += 1
        if self.votes == 3:
            del self


class Community:
    def __init__(self, bot):
        self.bot = bot
        self.active_votes = {}
        self.voter_timeout = {}

    async def start_manager(self):
        await asyncio.sleep(0.5)
        for vote in list(self.active_votes):
            if self.active_votes[vote] > 10:
                del self.active_votes[vote]
                self.active_votes.pop(vote, None)
                print(vote + " removed")

    @commands.command(description="Starts vote", hidden=True, pass_context=True)
    async def votestart(self, ctx):
        server = ctx.message.channel.server.name
        instigator = ctx.message.author.name
        if not (instigator in self.voter_timeout or server in self.active_votes):
            self.active_votes[server] = Vote(server, 3)
            while self.active_votes:
                await asyncio.sleep(0.5)
                await self.start_manager()
            await self.bot.say("Voting has started. (0/%s)" % self.active_votes[server].votemax)
        else:
            await self.bot.say("Please wait for the ongoing vote to finish.")

    @commands.command(description="Votes on the current vote", hidden=True, pass_context=True)
    async def vote(self, ctx):
        server = ctx.message.channel.server.name
        voter = ctx.message.author.name

        def get_vote():
            if server in self.active_votes:
                return self.active_votes[server]
            else:
                return None

        vote_object = get_vote()
        if vote_object:
            if voter not in vote_object.voters:
                vote_object.incr()
                vote_object.voters.append(voter)
                await self.bot.say("Voting (%s/%s)" % (vote_object.votes, vote_object.votemax))
            else:
                await self.bot.say("You have already voted.")
        else:
            await self.bot.say("No active vote.")

    @commands.command(hidden=True)
    async def vote_test(self, *text, time=10):
        print(time)
        print(" ".join(text))

    @commands.command(hidden=True)
    async def votes(self):
        await self.bot.say(self.active_votes)


def setup(bot):
    bot.add_cog(Community(bot))
