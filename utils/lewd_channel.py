import json

CONF_FILE = 'cfg/bot_config.json'

# TODO see about merging this file into another


def push(server, channel):
    """
    Adds the passed channel to the list of channels where lewd functions are allowed
    :param server: String, plaintext name of the server.
    :param channel: String, plaintext name of the channel.
    Params can be found in the discord context, but it's possible to use statics as well"""
    with open(CONF_FILE, 'r+') as config:
        data = json.load(config)
        if server not in data["lewd_allowed"]:
            data['lewd_allowed'][server] = [channel]
        else:
            data['lewd_allowed'][server].append(channel)
        config.seek(0)
        json.dump(data, config, indent=4, sort_keys=True)
        config.truncate()
        return data['lewd_allowed']


def pop(server, channel):
    """
        Removes the passed channel from the list of channels where lewd functions are allowed
        :param server: String, plaintext name of server.
        :param channel: String, plaintext name of the channel.
        Usually gotten from the discord context"""
    with open(CONF_FILE, 'r+') as config:
        data = json.load(config)
        data['lewd_allowed'][server].remove(channel)
        config.seek(0)
        json.dump(data, config, indent=4, sort_keys=True)
        config.truncate()
        return data['lewd_allowed']
