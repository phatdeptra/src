
import discord
import json
import random
import pyowm
import youtube_dl
import asyncio
from newsapi import NewsApiClient
from discord.ext.commands import * 

intents = discord.Intents.all()
intents.voice_states = True
intents.members = True 
intents.guilds = True

bot = Bot(command_prefix=".", case_insensitive= True, intents=intents)

owm = pyowm.OWM('63eb1b66f709c2bfe5f1770fe88fbc56')

muted_users = {}

NEWS_API_KEY = '98a1bf4eb7c543fd9d2b4adab11767b0'

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# Event
@bot.event
async def on_member_join(member):
    welcome_channel = welcome

    if welcome_channel:
        welcome_message = f"chào mừng, {member.mention}! đã đến với discord test bot."
        await welcome_channel.send(welcome_message)

@bot.event
async def on_member_remove(member):
    goodbye_channel = goobye

    if goodbye_channel:
        goodbye_message = f"cút, {member.display_name}! con mẹ mày đi."
        await goodbye_channel.send(goodbye_message)

@bot.event
async def on_ready():
    print(f'đã vào acc {bot.user.name} - {bot.user.id}')
    await bot.change_presence(activity=discord.Game(name="bú cặc chó"))
    
@bot.event
async def on_message(message):
    prefixes = load_prefixes()

    if str(message.guild.id) in prefixes:
        custom_prefix = prefixes[str(message.guild.id)]
        bot.command_prefix = custom_prefix

    await bot.process_commands(message)
    
    # Load prefixes from a JSON file
def load_prefixes():
    try:
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        prefixes = {}
    return prefixes
    
    # Load or create the experience data file
try:
    with open('exp_data.json', 'r') as f:
        exp_data = json.load(f)
except FileNotFoundError:
    exp_data = {}
    
    # Save prefixes to the JSON file
def save_prefixes(prefixes):
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)
	
# commands
@bot.command()
async def weather(ctx, *, city):
    try:
        observation = owm.weather_at_place(city)
        weather = observation.get_weather()
        
        temperature = weather.get_temperature('celsius')['temp']
        status = weather.get_status()
        
        weather_message = f"The current weather in {city} is {status.capitalize()} with a temperature of {temperature:.1f}°C."
        await ctx.send(weather_message)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def addexp(ctx, member: discord.Member, exp_amount: int):
    if exp_amount <= 0:
        await ctx.send("Invalid experience amount.")
        return
    
    user_id = str(member.id)
    
    if user_id in exp_data:
        exp_data[user_id]['exp'] += exp_amount
    else:
        exp_data[user_id] = {'exp': exp_amount}
    
    with open('exp_data.json', 'w') as f:
        json.dump(exp_data, f, indent=4)
    
    await ctx.send(f"cho {exp_amount}  {member.display_name}'s .")

@bot.command()
async def exp(ctx, member: discord.Member = None):
    member = member or ctx.author
    
    user_id = str(member.id)
    
    if user_id in exp_data:
        current_exp = exp_data[user_id]['exp']
        await ctx.send(f"{member.display_name}'s experience: {current_exp} XP")
    else:
        await ctx.send(f"{member.display_name} has no experience yet.")


@bot.command()
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"{ctx.channel.mention} ``` kênh đã được mở khóa ``` .")

@bot.command()
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"{ctx.channel.mention} kênh đã được khóa.")

@bot.command()
async def mute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if muted_role is None:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
             await channel.set_permissions(muted_role, send_messages=False)
    
    await member.add_roles(muted_role)
    muted_users[member.muted.id] = muted_role.id
    
    await ctx.send(f"{member.mention} mày đã bị khóa mõm.")

@bot.command()
async def permissions(ctx, user: discord.Member = None):
    user = user or ctx.author
    
    permissions = user.permissions_in(ctx.channel)
    
    permissions_str = '\n'.join(f'{perm[0]}: {perm[1]}' for perm in permissions)
    
    embed = discord.Embed(title=f'Permissions for {user.display_name}', description=permissions_str, color=discord.Color.blue())
    await ctx.send(embed=embed)

async def news(ctx, *, query=''):
    if not query:
        await ctx.send("hãy nhập nội dung tìm kiếm tin tức.")
        return

    try:
        news_data = newsapi.get_top_headlines(q=query, language='en', page_size=5)
        
        if news_data['totalResults'] > 0:
            for article in news_data['articles']:
                title = article['title']
                description = article['description']
                url = article['url']
                
                news_embed = discord.Embed(title=title, description=description, url=url, color=discord.Color.blue())
                await ctx.send(embed=news_embed)
        else:
            await ctx.send("No news articles found for the provided topic.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def status(ctx, *, new_status):
    await bot.change_presence(activity=discord.Game(name=new_status))
    await ctx.send(f"trạng thái bot đã thành {new_status}")

@bot.command()
async def setprefix(ctx, new_prefix):
    prefixes = load_prefixes()
    prefixes[str(ctx.guild.id)] = new_prefix
    save_prefixes(prefixes)
    await ctx.send(f'Prefix mới là: {new_prefix}')
    
@bot.command()
async def ping(ctx):
	await ctx.send("ping của bot là **{0}**".format(round(bot.latency * 1000)))
		
@bot.command()
async def kick(ctx, member: discord.Member, reason="không có lý do"):
		await ctx.send(f"{member.mention} đã bị kick |  Reason:  {reason}")
		await member.send(f"chúc mừng mày đã cút khỏi **server** |  Reason:  {reason}")
		await member.kick(reason=reason)
		
@bot.command()
async def ban(ctx, member: discord.Member, reason="không có lý do"):
	await ctx.send(f"{member.mention} đã bị ban |  Reason:  {reason}")	
	await member.send(f"óc cặc bị baned haha **server** |  Reason:  {reason}")
	await member.ban(reason=reason)
		
@bot.command()
async def unban(ctx, member: discord.Member):
	await ctx.send(f"{member.mention} đã được unban")
	await member.send(f"địt mẹ hên vậy , đã được unband **server**")
	await member.unban()
	
@bot.command()
async def addrole(ctx, user: discord.Member, role: discord.Role):
    if role not in user.roles:
        await user.add_roles(role)
        await ctx.send(f"cho {role.name} role {user.mention}.")
    else:
        await ctx.send(f"{user.mention} đã có {role.name} role.")
	
	
bot.run("")
