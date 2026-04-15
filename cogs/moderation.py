# cogs/moderation.py

import re
from discord.ext import commands
import discord
from datetime import timedelta
from config import BAN_PERMS,UNBAN_PERMS,KICK_PERMS,TIMEOUT_PERMS,PURGE_PERMS,BOT,NICK_PERMS,DUMPROLE_PERMS,SAY_PERMS,SM_PERMS
from logger import log_command

import re

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    def has_perm_sm(self, ctx):
        return ctx.author.id in BOT or any(role.id in SM_PERMS for role in ctx.author.roles)
    def has_perm_dc(self, ctx):
        return ctx.author.id in BOT or any(role.id in SAY_PERMS for role in ctx.author.roles)
    def has_perm_dump(self, ctx):
        return ctx.author.id in BOT or any(role.id in DUMPROLE_PERMS for role in ctx.author.roles)
    def has_perm_nick(self, ctx):
        return ctx.author.id in BOT or any(role.id in NICK_PERMS for role in ctx.author.roles)
    def has_perm_ban(self, ctx):
        return ctx.author.id in BOT or any(role.id in BAN_PERMS for role in ctx.author.roles)
    def has_perm_unban(self, ctx):
        return ctx.author.id in BOT or any(role.id in UNBAN_PERMS for role in ctx.author.roles)
    def has_perm_kick(self, ctx):
        return ctx.author.id in BOT or any(role.id in KICK_PERMS for role in ctx.author.roles)
    def has_perm_timeout(self, ctx):
        return ctx.author.id in BOT or any(role.id in TIMEOUT_PERMS for role in ctx.author.roles)
    def has_perm_purge(self, ctx):
        return ctx.author.id in BOT or any(role.id in PURGE_PERMS for role in ctx.author.roles)
    def has_perm_say(self, ctx):
        return ctx.author.id in BOT or any(role.id in SAY_PERMS for role in ctx.author.roles)    

    @commands.command()
    async def say(self, ctx, *, message: str = None):
        if not self.has_perm_say(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not message:
            return await ctx.send("Usage: `.say <message>`", delete_after=5)

        try:
            await ctx.message.delete()

        except discord.Forbidden:
            pass  # Bot doesn't have permission to delete messages

        await ctx.send(message)
        await log_command(ctx, "say")

    @commands.command()
    async def dumprole(self, ctx, *, role_arg=None):
        if not self.has_perm_dump(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not role_arg:
            return await ctx.send("Usage: `.dumprole <role name/id/mention>`", delete_after=5)

        # Try to find the role from mention, ID, or name
        role = None
        if ctx.message.role_mentions:
            role = ctx.message.role_mentions[0]
        else:
            try:
                role_id = int(role_arg.strip("<@&>"))
                role = ctx.guild.get_role(role_id)
            except:
                role = discord.utils.find(lambda r: r.name.lower() == role_arg.lower(), ctx.guild.roles)

        if not role:
            return await ctx.send("Role not found.", delete_after=5)

        members = [member.mention for member in role.members]
        if not members:
            return await ctx.send("No members found with that role.", delete_after=5)

        # Create embed
        embed = discord.Embed(
            title=f"{role.name}",
            description="\n".join(members),
            color=role.color or discord.Color.blue()
        )
        # Avoid hitting embed size limit (max 4096 characters)
        if len(embed.description) > 4000:
            parts = [members[i:i+50] for i in range(0, len(members), 50)]
            await ctx.send(f"Members with role {role.name} ({len(members)}):")
            for chunk in parts:
                await ctx.send(", ".join(chunk))
        else:
            await ctx.send(embed=embed)
        await log_command(ctx, "dumprole")


    @commands.command()
    async def ban(self, ctx, member: discord.Member = None, *, reason=None):
        if not self.has_perm_ban(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not member:
            return await ctx.send(" Mention a user to ban.", delete_after=5)
        if ctx.author.id not in BOT and member.top_role > ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot ban higher role.", delete_after=5)
        try:
            await member.ban(reason=reason)
            await ctx.send(f" {member.display_name} banned.")
            await log_command(ctx, "ban")
        except Exception as e:
            await ctx.send(f" Error: {e}")

    @commands.command(aliases=["nick"])
    async def nickname(self, ctx, member: discord.Member = None, *, new_nick: str = None):
        
        if not self.has_perm_nick(ctx):  # You should define this permission check
            return await ctx.send("No permission.", delete_after=5)

        if not member or not new_nick:
            return await ctx.send("Usage: `.nick <tag/userid/username> <newnickname>`", delete_after=8)

        if ctx.author.id not in BOT and member.top_role > ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("Cannot change nickname of a higher role member.", delete_after=6)

        try:
            await member.edit(nick=new_nick, reason=f"Changed by {ctx.author}")
            await ctx.send(f" Nickname changed for {member.mention} to **{new_nick}**.")
            await log_command(ctx, "nickname")
        except Exception as e:
            await ctx.send(f"Error: {e}")


    @commands.command()
    async def unban(self, ctx, user_id: int = None):
        if not self.has_perm_unban(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not user_id:
            return await ctx.send(" Usage: `.unban <user_id>`", delete_after=5)
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f" Unbanned {user.mention} (`{user.id}`).")
            await log_command(ctx, "unban")
        except discord.NotFound:
            await ctx.send(" That user is not banned or ID is invalid.", delete_after=5)
        except Exception as e:
            await ctx.send(f" Error: {e}")

    @commands.command()
    async def kick(self, ctx, member: discord.Member = None, *, reason=None):
        if not self.has_perm_kick(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not member:
            return await ctx.send(" Mention a user to kick.", delete_after=5)
        if ctx.author.id not in BOT and member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot kick higher/equal role.", delete_after=5)
        try:
            await member.kick(reason=reason)
            await ctx.send(f" Kicked {member.display_name}.")
            await log_command(ctx, "kick")
        except Exception as e:
            await ctx.send(f" Error: {e}")

    def parse_duration(self, duration_str):
        match = re.match(r"^(\d+)([smhd])$", duration_str)
        if not match:
            return None
        value, unit = match.groups()
        value = int(value)
        return {
            's': timedelta(seconds=value),
            'm': timedelta(minutes=value),
            'h': timedelta(hours=value),
            'd': timedelta(days=value)
        }.get(unit)


    @commands.command(name="to")
    async def timeout(self, ctx, member: discord.Member = None, duration: str = None):
        if not self.has_perm_timeout(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not member or not duration:
            return await ctx.send(" Usage: `.to <user> <duration>` (e.g., 10s, 5m, 2h)", delete_after=5)
        if ctx.author.id not in BOT and member.top_role > ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot timeout higher role.", delete_after=5)

        delta = self.parse_duration(duration)
        if not delta:
            return await ctx.send(" Invalid duration. Use formats like `10s`, `5m`, `2h`, `1d`.", delete_after=5)
        try:
            await member.timeout(delta)
            await ctx.send(f"⏱️ {member.display_name} has been timed out for {duration}.")
            await log_command(ctx, "timeout")
        except Exception as e:
            await ctx.send(f" Error: {e}")

    @commands.command(name="rto")
    async def untimeout(self, ctx, member: discord.Member = None):
        if not self.has_perm_timeout(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not member:
            return await ctx.send(" Usage: .rto <user>")
        if ctx.author.id not in BOT and member.top_role > ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot remove timeout from higher role.", delete_after=5)
        try:
            await member.timeout(None)
            await ctx.send(f"🔓 {member.display_name} is no longer timed out.")
            await log_command(ctx, "rto")
        except Exception as e:
            await ctx.send(f" Error")

    @commands.command()
    async def purge(self, ctx, amount: int = None):
        if not self.has_perm_purge(ctx):
            return await ctx.send(" No permission.", delete_after=5)
        if not amount or amount <= 0:
            return await ctx.send(" Usage: `.purge <number of messages>`", delete_after=5)
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f" Deleted {len(deleted) - 1} messages.", delete_after=5)
            await log_command(ctx, "purge")
        except Exception as e:
            await ctx.send(f" Error: {e}")

    @commands.command(aliases=["sm"])
    async def slowmode(self, ctx, time: str = None, channel: discord.TextChannel = None):

        if not self.has_perm_sm(ctx):
            return await ctx.send(" You don’t have permission to manage channels.", delete_after=5)

        if not time:
            return await ctx.send(" Please specify a duration (e.g. `10s`, `2m`, `1h`, or `off`).", delete_after=5)

        # Convert time string to seconds
        time = time.lower().strip()
        if time in ["off", "none", "0"]:
            seconds = 0
        else:
            match = re.fullmatch(r"(\d+)([smh])", time)
            if not match:
                return await ctx.send(" Invalid time format. Use `10s`, `5m`, `1h`, or `off`.", delete_after=5)
            value, unit = match.groups()
            value = int(value)
            seconds = {"s": 1, "m": 60, "h": 3600}[unit] * value

        if not (0 <= seconds <= 21600):
            return await ctx.send(" Slowmode must be between 0s and 6h (21600 seconds).", delete_after=5)

        channel = channel or ctx.channel

        try:
            await channel.edit(slowmode_delay=seconds)
            await log_command(ctx, "slowmode")
            if seconds == 0:
                await ctx.send(f"⏱️ Slowmode **disabled** in {channel.mention}.")
            else:
                await ctx.send(f"⏱️ Set slowmode to **{seconds} seconds** in {channel.mention}.")
        except discord.Forbidden:
            await ctx.send(" I don’t have permission to edit that channel.", delete_after=5)
        except Exception as e:
            await ctx.send(f" Failed to set slowmode: {e}")


async def setup(bot):
    await bot.add_cog(Moderation(bot))