# cogs/Utility.py
from discord.ext import commands
import discord
from datetime import timedelta
from config import AVATAR_PERMS, BOT, UI_PERMS
from logger import log_command

import re

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    def has_perm_av(self, ctx):
        return ctx.author.id in BOT or any(role.id in AVATAR_PERMS for role in ctx.author.roles)
    def has_perm_ui(self, ctx):
        return ctx.author.id in BOT or any(role.id in UI_PERMS for role in ctx.author.roles)
    
    @commands.command(aliases=['avatar', 'pfp'])
    async def av(self, ctx, member: discord.Member = None):

        if not self.has_perm_av(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        
        member = member or ctx.author  # Use mentioned member or the command invoker

        embed = discord.Embed(
            title=f"{member.name}'s Avatar",
            color=discord.Color.gold()
        )
        embed.set_image(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)
        await log_command(ctx, "av")

    @commands.command(aliases=["ui"])
    async def userinfo(self, ctx, *, arg=None):

        # Permission check
        if not self.has_perm_ui(ctx):
            return await ctx.send(" You don't have permission to use this command.", delete_after=5)

        member = None

        # Get member from message reply
        if ctx.message.reference:
            try:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                member = msg.author if isinstance(msg.author, discord.Member) else None
            except:
                pass

        # Get member from argument
        if not member and arg:
            try:
                member = await commands.MemberConverter().convert(ctx, arg)
            except:
                member = discord.utils.find(
                    lambda m: arg.lower() in m.name.lower() or arg.lower() in m.display_name.lower(),
                    ctx.guild.members
                )

        # Fallback to author
        if not member:
            member = ctx.author

        # Get roles in reverse (highest first), excluding @everyone
        roles = [role.mention for role in reversed(member.roles) if role != ctx.guild.default_role]
        roles_str = ", ".join(roles) if roles else "None"

        # Build embed
        embed = discord.Embed(
            title=f"👤 User Info: {member}",
            color=discord.Color.dark_gold(),
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Username", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
        embed.add_field(name="Status", value=str(member.status).title(), inline=True)
        embed.add_field(name="Bot?", value="✅ Yes" if member.bot else " No", inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, style='F'), inline=False)
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, style='F'), inline=False)
        embed.add_field(name="Top Roles", value=roles_str, inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)
        await log_command(ctx, "userinfo")



async def setup(bot):
    await bot.add_cog(Utility(bot))
