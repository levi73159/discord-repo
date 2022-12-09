import discord


async def update(msg: discord.Message, _):
    with open('games.txt', 'r') as f:
        data = f.read()
    await msg.channel.send(f"```{data}```")
    await msg.delete()


def check_role(user, roles):
    for role in user.roles:
        if role.name.lower() in roles:
            return True
    return False

async def clear(msg: discord.Message, _):
    # check if the user is admin
    if not check_role(msg.author, ['admin']):
        return

    # clear all the messages in the channel
    await msg.channel.purge()


async def gidea(msg: discord.Message, o):
    with open('ideas.txt', 'a') as f:
        f.write(f'[{msg.author.name}]: {o}\n')
    await msg.reply('Idea sent to levi him self')


async def help(msg: discord.Message, _):
    await msg.channel.send("""
Every command must start with a / or !
```update: shows you the current projects and it views and downloads
idea: give an idea to the myth the legend levi to make a game
_allusr(LSMembers only): shows you all the users name, roles, and id
help: THIS IS HELPING YOU```""")

async def dev_allusr(msg: discord.Message, _):
    if not check_role(msg.author, ['admin', 'LeviStudiosMember']):
        return

    users = msg.channel.guild.members
    users_format = map(lambda x: f'{x.name}, {list(map(lambda y: y.name ,x.roles[1:]))}, {x.id}', users)
    for i, user in enumerate(users_format):
        await msg.channel.send(f"{i}: {user}")


