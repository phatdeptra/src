import discord
import json
import random
import pyowm
import aiohttp
import sqlite3
import requests
import youtube_dl
import subprocess 
import sqlite3
import sys
import asyncio
from newsapi import NewsApiClient
from discord.ext import commands, tasks
from discord.ext.commands import BucketType, cooldown
intents = discord.Intents.all()
intents.voice_states = True
intents.members = True 
intents.guilds = True
intents.emojis = True

bot = commands.Bot(command_prefix=".", case_insensitive= True, intents=intents)
session = aiohttp.ClientSession()

is_restarting = False

owm = pyowm.OWM('63eb1b66f709c2bfe5f1770fe88fbc56')

muted_users = {}

NEWS_API_KEY = '98a1bf4eb7c543fd9d2b4adab11767b0'

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def buy_fishing_rod(user_data):
    if 'fishing_rod' not in user_data:
        user_data['fishing_rod'] = False

    if user_data['fishing_rod']:
        return "Bạn đã có một cây cần câu."
    else:
        user_data['balance'] -= 100
        user_data['fishing_rod'] = True
        return "Bạn đã mua một cây cần câu thành công."

def fish(user_data):
    if 'fishing_rod' not in user_data or not user_data['fishing_rod']:
        return "Bạn chưa có cây cần câu."

    if 'fish_caught' not in user_data:
        user_data['fish_caught'] = []

    caught_fish = random.choice(['Cá vàng', 'Cá bớp', 'Cá chép', 'Cá trê'])
    user_data['fish_caught'].append(caught_fish)
    return f"Bạn đã câu được {caught_fish}."

def sell_fish(user_data):
    if 'fish_caught' not in user_data or not user_data['fish_caught']:
        return "Bạn chưa câu được cá nào."

    total_earnings = 0
    for fish in user_data['fish_caught']:
        if fish == 'Cá vàng':
            total_earnings += 50
        elif fish == 'Cá bớp':
            total_earnings += 30
        elif fish == 'Cá chép':
            total_earnings += 20
        elif fish == 'Cá trê':
            total_earnings += 10

    user_data['balance'] += total_earnings
    user_data['fish_caught'] = []
    return f"Bạn đã bán cá thành công và nhận được {total_earnings} tiền."

# Load dữ liệu từ file user_data.json
def load_user_data():
    try:
        with open('user_data.json', 'r') as file:
            user_data = json.load(file)
    except FileNotFoundError:
        user_data = {}
    return user_data

def save_user_data(user_data):
    with open('user_data.json', 'w') as file:
        json.dump(user_data, file)

# Dữ liệu lưu trữ thông tin người dùng
user_data = load_user_data()

try:
    with open('user_data.json', 'r') as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}
      
# Event
@bot.event
async def on_disconnect():
    await session.close()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id not in user_levels:
        user_levels[message.author.id] = {
            'exp': 0,
            'level': 1
        }

    user_levels[message.author.id]['exp'] += 1

    # Kiểm tra nếu người dùng đã đạt đủ kinh nghiệm để tăng cấp
    if user_levels[message.author.id]['exp'] >= 10:
        user_levels[message.author.id]['exp'] = 0
        user_levels[message.author.id]['level'] += 1
        await message.channel.send(f'{message.author.mention} đã tăng cấp lên level {user_levels[message.author.id]["level"]}!')

    await bot.process_commands(message)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == 1119285963298967635:
        response = f"You said: {message.content}"
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!send_to_discord'):
        await send_to_discord(message.content[17:])
        await message.channel.send("Sent message to Discord channel.")

    await bot.process_commands(message)

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
    await bot.change_presence(activity=discord.Game(name="discord 😛😛 "))
    refresh.start()
      
@tasks.loop(seconds=30)
async def refresh():
    print('làm mới')
       
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
    
    # Save prefixes to the JSON file
def save_prefixes(prefixes):
    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)
	
# commands
@bot.command()
async def muacancau(ctx):
    user_data = load_user_data()
    response = buy_fishing_rod(user_data)
    save_user_data(user_data)
    await ctx.send(response)

@bot.command()
async def cauca(ctx):
    user_data = load_user_data()
    response = fish(user_data)
    save_user_data(user_data)
    await ctx.send(response)

@bot.command()
async def banca(ctx):
    user_data = load_user_data()
    response = sell_fish(user_data)
    save_user_data(user_data)
    await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def taoemoji(ctx, emoji_name, image_url):
    # Tải ảnh từ URL
    async with bot.session.get(image_url) as resp:
        image_data = await resp.read()

    # Tạo emoji trên máy chủ
    emoji = await ctx.guild.create_custom_emoji(name=emoji_name, image=image_data)

    # Gửi thông báo về việc tạo emoji thành công
    await ctx.send(f'Emoji {emoji.name} đã được tạo thành công!')

@bot.command()
@commands.is_owner()
async def xoalenh(ctx, command_name):
    bot.remove_command(command_name)
    await ctx.send(f"Lệnh {command_name} đã được xóa khỏi bot.")
    
@bot.command()
async def gai(ctx):
    gai_list = [
        {
            'name': '',
            'description': 'Cô gái dễ thương',
            'image': 'https://i.imgur.com/Q840mL6.jpg'
        },
        {
            'name': '',
            'description': 'Cô gái xinh đẹp',
            'image': 'https://i.imgur.com/6OCGTmf.jpg'
        },
        {
            'name': '',
            'description': ' Cô gái xinh đẹp',
            'image': 'https://i.imgur.com/34nFb62.jpg'
        },
        # Thêm các cô gái khác vào đây
    ]

    # Chọn ngẫu nhiên một cô gái từ danh sách
    chosen_gai = random.choice(gai_list)

    # Tạo embed message để hiển thị thông tin và ảnh của cô gái
    embed = discord.Embed(title=chosen_gai['name'], description=chosen_gai['description'], color=discord.Color.purple())
    embed.set_image(url=chosen_gai['image'])

    # Gửi embed message vào kênh chat
    await ctx.send(embed=embed)

@bot.command()
async def trai(ctx):
    # Danh sách các thông tin và ảnh của các chàng trai
    trai_list = [
        {
            'name': 'trai 1',
            'description': 'Chàng trai đẹp trai và thông minh',
            'image': 'https://i.imgur.com/6OH8D9w.jpg'
        },
        {
            'name': 'trai 2',
            'description': 'anh chàng tập gym body 6 múi',
            'image': 'https://i.imgur.com/nRdKrWe.jpg'
        },
        # Thêm các chàng trai khác vào đây
    ]

    # Chọn ngẫu nhiên một chàng trai từ danh sách
    chosen_trai = random.choice(trai_list)

    # Tạo embed message để hiển thị thông tin và ảnh của chàng trai
    embed = discord.Embed(title=chosen_trai['name'], description=chosen_trai['description'], color=discord.Color.blue())
    embed.set_image(url=chosen_trai['image'])

    # Gửi embed message vào kênh chat
    await ctx.send(embed=embed)

@bot.command()
async def update(ctx):
    # Kiểm tra quyền hạn của người gửi lệnh
    if ctx.author.id != 975838777471795202:
        return await ctx.send('Bạn không có quyền thực hiện lệnh này.')

    await ctx.send('Bắt đầu cập nhật...')

    try:
        # Chạy lệnh git pull để cập nhật mã nguồn
        subprocess.run(['git', 'pull'])
        await ctx.send('Cập nhật thành công. Bot sẽ khởi động lại.')

        # Khởi động lại bot
        await bot.close()
        await bot.login("OTc1ODUyNTYxODk2NzMwNzE0.GN_fC0.QL0taNfglD3Dy6QJP-rp3vqzuPg3Pjy8C3Tfn8")
        await bot.connect()

    except Exception as e:
        await ctx.send(f'Có lỗi xảy ra trong quá trình cập nhật: {e}')

@bot.command()
async def level(ctx):
    if ctx.author.id not in user_levels:
        await ctx.send('Bạn chưa có dữ liệu level.')
    else:
        level = user_levels[ctx.author.id]['level']
        exp = user_levels[ctx.author.id]['exp']
        await ctx.send(f'Bạn đang ở level {level} với {exp} kinh nghiệm.')

@bot.command()
@commands.is_owner()
async def lammoi(ctx):
    if not refresh.is_running():
        refresh.start()
        await ctx.send('Bot đã được cài đặt tự động làm mới.')
    else:
        await ctx.send('Bot đã được cài đặt tự động làm mới từ trước.')

@bot.command()
@commands.is_owner()
async def tatlammoi(ctx):
    if refresh.is_running():
        refresh.stop()
        await ctx.send('Bot đã được dừng tự động làm mới.')
    else:
        await ctx.send('Bot không được cài đặt tự động làm mới.')

@bot.command()
async def pray(ctx):
    await ctx.send('Chúc bạn có một ngày tốt lành và may mắn!')
    with open("/storage/emulated/0/Download/n.jpeg", "rb") as f:
        image = discord.File(f)
        await ctx.send(file=image)

@bot.command()
@commands.has_permissions(administrator=True)
async def setmoney(ctx, member: discord.Member, amount: int):
    if ctx.author.id not in user_data:
        user_data[ctx.author.id] = {
            'balance': 0
        }

    user_data[member.id] = {
        'balance': amount
    }

    save_user_data(user_data)

    await ctx.send(f'Số dư của {member.mention} đã được cập nhật thành {amount}!')
    
@bot.command()
@commands.is_owner()
async def tatbot(ctx):
    global is_restarting
    if is_restarting:
        await ctx.send("bot đã tắt")
        return
    
    is_restarting = True
    await ctx.send("Bot tắt...")
    
    await bot.change_presence(status=discord.Status.dnd)
    
    await bot.close()
    
    subprocess.Popen([sys.executable, __file__])
    await asyncio.sleep(1)
    sys.exit()
    
@bot.command()
@commands.is_owner()
async def baotri(ctx, status: str):
    global is_maintenance_mode
    if status.lower() == "on":
        is_maintenance_mode = True
        await bot.change_presence(status=discord.Status.dnd)
        await ctx.send("``` Bot đã bật chế độ bảo trì ```")
    elif status.lower() == "off":
        is_maintenance_mode = False
        await bot.change_presence(status=discord.Status.online)
        await ctx.send("``` Bot đã tắt chế độ bảo trì ```")
    else:
        await ctx.send("``` Nhập sai rồi. Vui lòng nhập 'on' hoặc 'off' ```")

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=100):
    await ctx.channel.purge(limit=amount + 5)

@bot.command()
@commands.cooldown(1, 5, BucketType.user)
async def tt(ctx, amount: int):
    user_id = str(ctx.author.id)
    
    if user_id in user_data:
        balance = user_data[user_id]['balance']
        if amount > balance or amount <= 0:
            await ctx.send("đặt cược sai yêu cầu đặt lại.")
            return
        
        outcome = random.choice(['win', 'lose'])
        
        if outcome == 'win':
            user_data[user_id]['balance'] += amount
            await ctx.send(f"bạn đã thắng {amount} coins, số tiền mới của bạn là: {user_data[user_id]['balance']} coins")
        else:
            user_data[user_id]['balance'] -= amount
            await ctx.send(f"bạn đã thua {amount} coins, số tiền mới của bạn là: {user_data[user_id]['balance']} coins")
        
        with open('user_data.json', 'w') as f:
            json.dump(user_data, f, indent=4)
    else:
        await ctx.send("bạn cần .choi để nhận có tiền chơi")
        
@tt.error
async def tt_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Lệnh này đang trong thời gian chờ. Vui lòng thử lại sau {error.retry_after:.2f} giây.")

@bot.command()
async def choi(ctx):
    user_id = str(ctx.author.id)
    
    if user_id not in user_data:
        user_data[user_id] = {'balance': 1000}
        with open('user_data.json', 'w') as f:
            json.dump(user_data, f, indent=4)
        await ctx.send("chúc mừng bạn đã nhận được 1000 coin!")
    else:
        await ctx.send("bạn đã nhận thưởng rồi")

@bot.command()
@commands.cooldown(1, 5, BucketType.user)
async def bal(ctx):
    user_data = load_user_data()
    balance = user_data.get('balance', 0)
    await ctx.send(f"Số dư của bạn là {balance} tiền 💶")
@bal.error
async def bal_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Lệnh này đang trong thời gian chờ. Vui lòng thử lại sau ``` {error.retry_after:.2f} ``` giây 🕠 ")

@bot.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"{ctx.channel.mention} ``` kênh đã được mở khóa ``` .")

@bot.command()
@commands.has_permissions(administrator=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"{ctx.channel.mention} kênh đã được khóa.")

@bot.command()
@commands.has_permissions(administrator=True)
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
@commands.has_permissions(administrator=True)
async def status(ctx, *, new_status):
    await bot.change_presence(activity=discord.Game(name=new_status))
    await ctx.send(f"trạng thái bot đã thành {new_status}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix):
    prefixes = load_prefixes()
    prefixes[str(ctx.guild.id)] = new_prefix
    save_prefixes(prefixes)
    await ctx.send(f'Prefix mới là: {new_prefix}')
    
@bot.command()
async def ping(ctx):
	await ctx.send("ping của bot là **{0}**".format(round(bot.latency * 1000)))
		
@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, reason="không có lý do"):
		await ctx.send(f"{member.mention} đã bị kick |  Reason:  {reason}")
		await member.send(f"chúc mừng mày đã cút khỏi **server** |  Reason:  {reason}")
		await member.kick(reason=reason)
		
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, reason="không có lý do"):
	await ctx.send(f"{member.mention} đã bị ban |  Reason:  {reason}")	
	await member.send(f"óc cặc bị baned haha **server** |  Reason:  {reason}")
	await member.ban(reason=reason)
		
@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, member: discord.Member):
	await ctx.send(f"{member.mention} đã được unban")
	await member.send(f"địt mẹ hên vậy , đã được unband **server**")
	await member.unban()

@bot.command()
@commands.has_permissions(administrator=True)
async def addrole(ctx, user: discord.Member, role: discord.Role):
    if role not in user.roles:
        await user.add_roles(role)
        await ctx.send(f"cho {role.name} role {user.mention}.")
    else:
        await ctx.send(f"{user.mention} đã có {role.name} role.")
        
@bot.command()
async def xemip(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    response = requests.get(f"https://ipapi.co/{member.name}/json/")
    data = response.json()
    ip = data.get('ip')

    if ip:
        await ctx.send(f"Địa chỉ IP của {member.name} là: {ip}")
    else:
        await ctx.send("Không thể lấy địa chỉ IP của người dùng.")
        
	
bot.run("OTc1ODUyNTYxODk2NzMwNzE0.GN_fC0.QL0taNfglD3Dy6QJP-rp3vqzuPg3Pjy8C3Tfn8")
