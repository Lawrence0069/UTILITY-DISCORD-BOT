import discord
from discord.ext import commands
import os
import os

# Set working directory to where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("Now working in:", os.getcwd())

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"🔹 Loaded {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

import asyncio
async def main():
    await load_cogs()
    await bot.start("MTQxNjAzMjEzVEFzMzc5ODI2NQ.GVBWZA7.cI0LcEX9Wlxgqc5EA-1-pG37bjexjJSS2VVDvY8")

asyncio.run(main())
