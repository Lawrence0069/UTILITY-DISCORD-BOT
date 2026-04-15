# cogs/role.py
from discord.ext import commands
import discord
from config import ROLE_PERMS, BOT, PING_PERMS
from logger import log_command

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_perm_role(self, ctx):
        return ctx.author.id in BOT or any(role.id in ROLE_PERMS for role in ctx.author.roles)
    def has_perm_ping(self, ctx):
        return ctx.author.id in BOT or any(role.id in PING_PERMS for role in ctx.author.roles)
    
    @commands.command()
    async def ping(self, ctx, role: discord.Role = None, *, message: str = None):

        if not self.has_perm_ping(ctx):
            await ctx.message.delete()
            return await ctx.send(" No permission.", delete_after=10)
        
        # List of allowed role IDs to be pinged
        ALLOWED_ROLE_IDS = [1363833812131250306, 1363833761183039638, 1363832742214766592, 1363832694101901472, 1388540960421580912, 1388541478468456479, 1388541543752798229, 1363833248639357114, 1363832775781650532, 1363832572714553344, 1363832599910551592, 1363839248616390786, 1363832666675347629, 1363830795114119258, 1363832631178956960]

        if not role or not message:
            await ctx.message.delete()
            return await ctx.send("Usage: `.ping <role mention/id/name> <message>`", delete_after=10)

        if role.id not in ALLOWED_ROLE_IDS:
            await ctx.message.delete()
            return await ctx.send("You cannot ping this role.", delete_after=5)

        try:
            await ctx.message.delete()
            await log_command(ctx, "ping")
        except discord.Forbidden:
            pass  # Bot lacks permission to delete

        await ctx.send(f"{role.mention} {message}")



    @commands.command(name="role")
    async def toggle_role(self, ctx, member: discord.Member = None, *, role: discord.Role = None):
        if not self.has_perm_role(ctx):
            return await ctx.send(" No permission.", delete_after=5)

        if not member or not role:
            return await ctx.send(" Usage: `.role <user> <role>`", delete_after=5)

        if ctx.author.id not in BOT and role > ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot modify higher role.", delete_after=5)

        try:
            await log_command(ctx, "role")
            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f" Removed role **{role.name}** from **{member.display_name}**.")
            else:
                await member.add_roles(role)
                await ctx.send(f" Added role **{role.name}** to **{member.display_name}**.")
        except Exception as e:
            await ctx.send(f" Error: {e}")

async def setup(bot):
    await bot.add_cog(RoleManager(bot))