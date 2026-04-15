# cogs/cleanup.py
from discord.ext import commands
import discord
from config import CLEAN, BOT
from logger import log_command

class Cleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_perm(self, ctx):
        return ctx.author.id in BOT or any(role.id in CLEAN for role in ctx.author.roles)

    @commands.command(name="clear")
    async def clear_bot_messages(self, ctx, limit: int = 50):
        

        if not self.has_perm(ctx):
            return await ctx.send("No permission.", delete_after=5)

        try:
            await ctx.message.delete()

            deleted = await ctx.channel.purge(
                limit=limit,
                check=lambda m: m.author == self.bot.user,
                bulk=True
            )

            await ctx.send(f"🧹 Deleted {len(deleted)} bot messages.", delete_after=5)
            await log_command(ctx, "clear")

        except discord.Forbidden:
            await ctx.send("Missing permissions to delete messages.", delete_after=5)
        except discord.HTTPException as e:
            await ctx.send(f"An HTTP error occurred: {e}", delete_after=5)
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Cleanup(bot))
