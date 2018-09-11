from discord.ext import commands
from utils.db_handler import ConnectionInstance
from datetime import datetime as dt
from collections import namedtuple


DATABASE = 'data/activity_log.db'
MOD_ROLE = 'modmin'


def is_mod(ctx):
    return any(r.name == MOD_ROLE for r in ctx.message.author.roles)


def sanitise(query):
    query = query.replace('-', '_')
    query = query.replace(' ', '_')
    query = query.replace("'", "")
    query = query.replace(',', '')
    return "'{}'".format(query)


def compdate(old, new):
    a = dt.strptime(old, '%Y - %m - %d')
    b = dt.strptime(new, '%Y - %m - %d')
    if a > b:
        return old, False
    else:
        return new, True


def check_for_table(scope):
    with ConnectionInstance(DATABASE) as db:
        db.modify("CREATE TABLE IF NOT EXISTS %s "
                  "(user_id text PRIMARY KEY, name_at_time text, last_active text, in_channel text)" %
                  sanitise(scope.id))
        db.modify("CREATE TABLE IF NOT EXISTS servers (server_id text PRIMARY KEY, server_name text )")
        db.modify("REPLACE INTO servers (server_id, server_name) VALUES (?, ?)", [scope.id, scope.name])


def update_entry(message):
    if message.channel:
        channel = message.channel
        in_chan = channel.name
        server = channel.server

        author_id = str(message.author.id)
        author_name = message.author.name
        timestamp = message.timestamp.strftime('%Y - %m - %d')
        check_for_table(server)

        with ConnectionInstance(DATABASE) as db:
            res = db.query("SELECT last_active, in_channel FROM %s WHERE user_id=?" % sanitise(server.id), [author_id],
                           one=True)
            if res:
                timestamp, update = compdate(res['last_active'], timestamp)
                if not update:
                    in_chan = res['in_channel']

            db.modify("REPLACE INTO %s (user_id, name_at_time, last_active, in_channel) VALUES(?, ?, ?, ?)" %
                      sanitise(server.id),
                      [author_id, author_name, timestamp, in_chan])


def get_inactive(ctx):
    now = dt.now().strftime('%Y - %m - %d')
    server = ctx.message.server
    inactive = []
    User = namedtuple('User', ['user_id', 'user_name'])
    with ConnectionInstance(DATABASE) as db:
        for member in server.members:
            r = db.query("SELECT last_active FROM %s WHERE user_id=?" % sanitise(server.id), [member.id], one=True)
            if r:
                current = dt.strptime(now, '%Y - %m - %d')
                last = dt.strptime(r['last_active'], '%Y - %m - %d')
                diff = current - last
                diff = diff.days

                if diff > 60:
                    inactive.append(User(member.id, member.name))

    return inactive


class Activity:

    def __init__(self, bot):
        self.bot = bot

    def is_mommy(self, ctx):
        return str(ctx.message.author.id) == self.bot.mommy

    @commands.command(pass_context=True, hidden=True)
    async def catchup(self, ctx, limit=100):
        if not self.is_mommy(ctx):
            return None

        server = ctx.message.channel.server

        def is_origin(context, cand):
            return context.message.channel.server == cand.channel.server

        for channel in server.channels:
            async for message in self.bot.logs_from(channel, limit=limit):
                if is_origin(ctx, message):
                    update_entry(message)
        return await self.bot.say('Caught up on the last {} messages!'.format(limit))

    @commands.command(pass_context=True, help="Tells you when a user last posted. Works with both tag and plaintext.")
    async def seen(self, ctx, user):
        mentions = ctx.message.mentions
        server = ctx.message.server.id
        if len(mentions) == 1:
            mentioned = mentions[0]
            with ConnectionInstance(DATABASE) as db:
                record = db.query("SELECT last_active, in_channel FROM %s WHERE user_id=?" % sanitise(server),
                                  [mentioned.id], one=True)
                if record:
                    reply = '{} was last seen at {} posting in {}'.format(
                        mentioned.name, record['last_active'], record['in_channel']
                    )
                    return await self.bot.say(reply)
        elif len(mentions) > 1:
            # TODO allow for multiple users
            pass
        else:
            with ConnectionInstance(DATABASE) as db:
                record = db.query("SELECT last_active, in_channel FROM %s WHERE name_at_time=? COLLATE nocase"
                                  % sanitise(server),
                                  [user], one=True)

                if record:
                    reply = '{} was last seen at {} posting in {}'.format(
                        user, record['last_active'], record['in_channel']
                    )
                    return await self.bot.say(reply)

    @commands.command(pass_context=True, hidden=True)
    @commands.check(is_mod)
    async def deauth(self, ctx):
        server = ctx.message.server

        inactive = get_inactive(ctx)

        deauthed = []

        for member in server.members:
            if any(i['user_id'] == member.id for i in inactive):
                for role in member.roles:
                    if role.name == 'verified':
                        await self.bot.remove_roles(member, role)
                        deauthed.append(member.name)
        return await self.bot.send_message(ctx.message.author, '```{}```'.format(m+'\n' for m in deauthed))

    @commands.command(pass_context=True, hidden=True)
    async def prune(self, ctx):
        inactive_members = get_inactive(ctx)
        if inactive_members:
            surround = "```"
            res = ''
            for member in inactive_members:
                res += '{}\n'.format(member.user_name)
            res = res.rstrip('\n')
            msg = '{0}{1}{0}'.format(surround, res)
        else:
            msg = 'No inactive members found.'

        if any(r.name == MOD_ROLE for r in ctx.message.author.roles):
            return await self.bot.send_message(ctx.message.author, msg)

    @commands.command(pass_context=True, hidden=True)
    async def maintenance(self, ctx):
        server = ctx.message.channel.server

        with ConnectionInstance(DATABASE) as db:
            res = db.query('SELECT user_id FROM %s' % sanitise(server.id))

        if res and self.is_mommy(ctx):
            current = [r['user_id'] for r in res]

            for member in server.members:
                if member.id not in current:
                    db.modify('DELETE FROM %s WHERE user_id=?' % sanitise(server.id), [member.id])


def setup(bot):
    bot.add_cog(Activity(bot))


