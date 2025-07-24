import discord
from discord.ext import commands, tasks
import json
from coingecko import get_price_and_ath
import asyncio

TOKEN = 'DISCORD_BOT_TOKEN'  # not webhook, this is the bot token
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# Load alerts
def load_alerts():
    try:
        with open("alerts.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_alerts(data):
    with open("alerts.json", "w") as f:
        json.dump(data, f)

# Load ATH records
def load_ath_data():
    try:
        with open("ath_store.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_ath_data(data):
    with open("ath_store.json", "w") as f:
        json.dump(data, f)

# 🔹 Command: /price bitcoin
@bot.command()
async def price(ctx, token: str):
    try:
        current, ath = get_price_and_ath(token)
        await ctx.send(f"💰 **{token.upper()}**\nCurrent: ${current:,.2f}\nATH: ${ath:,.2f}")
    except:
        await ctx.send("❌ Could not fetch data. Check token name.")

# 🔹 Command: /alert add bitcoin
@bot.command()
async def alert(ctx, action: str, token: str):
    user = str(ctx.author.id)
    alerts = load_alerts()

    if action == 'add':
        alerts.setdefault(user, [])
        if token not in alerts[user]:
            alerts[user].append(token)
            save_alerts(alerts)
            await ctx.send(f"🔔 Alert set for {token.upper()} ATH.")
        else:
            await ctx.send("🔔 Already tracking that token.")

    elif action == 'remove':
        if user in alerts and token in alerts[user]:
            alerts[user].remove(token)
            save_alerts(alerts)
            await ctx.send(f"🚫 Alert removed for {token.upper()}.")
        else:
            await ctx.send("❌ No such alert exists.")

# 🔄 Background task: check ATHs
@tasks.loop(minutes=5)
async def check_ath_loop():
    alerts = load_alerts()
    ath_data = load_ath_data()

    for user_id, tokens in alerts.items():
        for token in tokens:
            try:
                current, ath = get_price_and_ath(token)
                last_known = ath_data.get(token, ath)
                if current > last_known:
                    user = await bot.fetch_user(int(user_id))
                    await user.send(f"🚀 **{token.upper()} just hit a new ATH!**\nNew ATH: ${current:,.2f}")
                    ath_data[token] = current
            except:
                continue
    save_ath_data(ath_data)

@bot.event
async def on_ready():
    print(f"🤖 Bot connected as {bot.user}")
    check_ath_loop.start()

bot.run(TOKEN)
