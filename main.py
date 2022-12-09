from typing import Optional

import discord
import commands as cf
from discord.ext import commands
from threading import Thread
import time
import json
import os


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)


paycheck: dict = json.load(open("paycheck.json", 'r'))
accounts: dict = json.load(open("account.json", 'r'))

# save
def save():
    json.dump(accounts, open('account.json', 'w'))
    json.dump(paycheck, open('paycheck.json', 'w'))

# make it where it adds money or remove money every 2 minutes using ayncio
def add_money(id_):
    if paycheck.get(id_) is None: return

    if accounts.get(id_) is not None:
        accounts[id_] = accounts[id_] + paycheck[id_]
    else:
        accounts[id_] = paycheck[id_]

    if accounts[id_] < -20:
        accounts[id_] = -20

    save()


def add_money_s():
    while True:
        time.sleep(600)
        for id_ in paycheck.keys():
            add_money(id_)


def add_paycheck(id_, amount):
    if paycheck.get(id_) is not None:
        paycheck[id_] = paycheck[id_] + amount
    else:
        paycheck[id_] = amount

    if paycheck[id_] < -5:
        paycheck[id_] = -5

    save()

def sort():
    global paycheck, accounts
    paycheck = dict(sorted(paycheck.items(), key=lambda x: x[1]))
    accounts = dict(sorted(accounts.items(), key=lambda x: x[1]))

async def see_money(msg: discord.Message, _):
    users = msg.channel.guild.members
    # output Paycheck and account

    text = ""
    await msg.channel.send('Paycheck:')
    text += ""
    for user in users:
        for id_, pay in paycheck.items():
            if user.id == int(id_):
                text += f'{user.name}: {pay}\n'
    await msg.channel.send(f'```{text or " "}```')
    await msg.channel.send(f'Accounts:')
    text = ""
    for user in users:
        for id_, m in accounts.items():
            if user.id == int(id_):
                text += f'{user.name}: {m}\n'
    await msg.channel.send(f'```{text or " "}```')


async def richest(msg, _):
    def to_user(users, i) -> Optional[discord.User]:
        for u in users:
            if u.id == int(i):
                return u
        return None

    id_ = max(accounts, key=accounts.get)
    money = accounts[id_]
    user = to_user(msg.channel.guild.members, id_)
    await msg.channel.send(f'{user.name} is the richest with {money} frog coin')


cmds = {
    'update': cf.update,
    'clear': cf.clear,
    'help': cf.help,
    'idea': cf.gidea,
    'money': see_money,
    'richest': richest,

    '_allusr': cf.dev_allusr
}


@client.event
async def on_ready():
    print(f'{client.user} is ready')

    thread = Thread(target=add_money_s)
    thread.setDaemon(True)
    thread.start()


@client.event
async def on_message(msg: discord.Message):
    print(f'{msg.author}: {msg.content}')
    if msg.author == client.user:
        return
    msg_content = msg.content.lower()

    # cycle through the cmds with keys and values
    for key, cmd in cmds.items():
        if msg_content.startswith('!' + key) or msg_content.startswith('/' + key):
            o = msg.content.replace('!' + key, '').replace('/' + key, '').strip()
            await cmd(msg, o)
            break
    else:
        if msg_content.startswith('!') or msg_content.startswith('/'):
            await msg.channel.send("""```ansi
\u001b[1;31m There is no such command
```""")

    if msg.channel.category.name == 'FanArt' and len(msg.attachments) > 0:
        # add ARROW UP and DOWN
        await msg.add_reaction('⬆')
        await msg.add_reaction('⬇')


# on reaction
@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    if reaction.message.channel.category.name != 'FanArt' or len(reaction.message.attachments) <= 0:
        return
    if user == client.user:
        return

    if reaction.emoji == '⬆':
        add_paycheck(user.id, 1)
    elif reaction.emoji == '⬇':
        add_paycheck(user.id, -1)


@client.event
async def on_reaction_remove(reaction: discord.Reaction, user: discord.User):
    if reaction.message.channel.category.name != 'FanArt' or len(reaction.message.attachments) <= 0:
        return
    if user == client.user:
        return

    if reaction.emoji == '⬆':
        add_paycheck(user.id, -1)
    elif reaction.emoji == '⬇':
        add_paycheck(user.id, 1)


client.run(os.getenv('KEY'))
