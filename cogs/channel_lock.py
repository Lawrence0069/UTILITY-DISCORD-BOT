# cogs/channel_lock.py
from discord.ext import commands
import discord
from config import LOCK_CHANNEL_PERMS,UNLOCK_CHANNEL_PERMS,LOCK_SPECIFIC_USER,UNLOCK_SPECIFIC_USER, BOT
from logger import log_command

class ChannelLock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_perm_lock(self, ctx):
        return ctx.author.id in BOT or any(role.id in LOCK_CHANNEL_PERMS for role in ctx.author.roles)
    def has_perm_UNLOCK(self, ctx):
        return ctx.author.id in BOT or any(role.id in UNLOCK_CHANNEL_PERMS for role in ctx.author.roles)
    def has_perm_SPE(self, ctx):
        return ctx.author.id in BOT or any(role.id in LOCK_SPECIFIC_USER for role in ctx.author.roles)
    def has_perm_UNSPE(self, ctx):
        return ctx.author.id in BOT or any(role.id in UNLOCK_SPECIFIC_USER for role in ctx.author.roles)
    
    @commands.command()
    async def lock(self, ctx):
        
        if not self.has_perm_lock(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        try:
            overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(" Channel locked.")
            await log_command(ctx, "lock")
        except Exception as e:
            await ctx.send(f" Error: {e}")

    @commands.command()
    async def unlock(self, ctx):
        
        if not self.has_perm_UNLOCK(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        try:
            overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = True
            await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.send(" Channel unlocked.")
            await log_command(ctx, "unlock")
        except Exception as e:
            await ctx.send(f" Error: {e}")

    @commands.command()
    async def lockuser(self, ctx, member: discord.Member = None):
        
        if not self.has_perm_SPE(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not member:
            return await ctx.send(" Mention a user.", delete_after=5)
        if ctx.author.id not in BOT and member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot lock higher/equal role.", delete_after=5)
        try:
            overwrite = ctx.channel.overwrites_for(member)
            overwrite.send_messages = False
            await ctx.channel.set_permissions(member, overwrite=overwrite)
            await ctx.send(f" Channel locked for {member.display_name}.")
            await log_command(ctx, "lockuser")
        except Exception as e:
            await ctx.send(f" Error: {e}")

    @commands.command()
    async def unlockuser(self, ctx, member: discord.Member = None):
        if not self.has_perm_UNSPE(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not member:
            return await ctx.send(" Mention a user.", delete_after=5)
        if ctx.author.id not in BOT and member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot unlock higher/equal role.", delete_after=5)
        try:
            overwrite = ctx.channel.overwrites_for(member)
            overwrite.send_messages = True
            await ctx.channel.set_permissions(member, overwrite=overwrite)
            await ctx.send(f" Channel unlocked for {member.display_name}.")
            await log_command(ctx, "unlockuser")

        except Exception as e:
            await ctx.send(f" Error: {e}")

async def setup(bot):
    await bot.add_cog(ChannelLock(bot))