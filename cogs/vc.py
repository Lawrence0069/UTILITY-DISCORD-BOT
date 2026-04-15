# cogs/vc.py
from discord.ext import commands
import discord
from config import KH_PERMS,DRAG_PERMS,MU_PERMS,MVC_PERMS, DUO_ALLOWED_ROLE_IDS, DUO_VC_IDS, BOT, DC_PERMS , MUTEALL_PERMS, DEFEN_PERMS, DC_PERMS_SINGLE
from logger import log_command

class VCCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    def get_voice_channel(self, ctx, arg):
        # VC by ID
        if arg.isdigit():
            return discord.utils.get(ctx.guild.voice_channels, id=int(arg))
        # VC by name
        return discord.utils.find(lambda c: c.name.lower() == arg.lower(), ctx.guild.voice_channels)
    def get_voice_channel(self, ctx, arg):
        if not arg:
            return None
        if arg.isdigit():
            return discord.utils.get(ctx.guild.voice_channels, id=int(arg))
        return discord.utils.find(lambda c: c.name.lower() == arg.lower(), ctx.guild.voice_channels)
    def has_perm_dc(self, ctx):
        return ctx.author.id in BOT or any(role.id in DC_PERMS_SINGLE for role in ctx.author.roles)
    def has_perm_muteall(self, ctx):
        return ctx.author.id in BOT or any(role.id in MUTEALL_PERMS for role in ctx.author.roles)
    def has_perm_dcall(self, ctx):
        return ctx.author.id in BOT or any(role.id in DC_PERMS for role in ctx.author.roles)
    def has_perm_defen(self, ctx):
        return ctx.author.id in BOT or any(role.id in DEFEN_PERMS for role in ctx.author.roles)
    def has_perm_kh(self, ctx):
        return ctx.author.id in BOT or any(role.id in KH_PERMS for role in ctx.author.roles)
    def has_perm_drag(self, ctx):
        return ctx.author.id in BOT or any(role.id in DRAG_PERMS for role in ctx.author.roles)
    def has_perm_mu(self, ctx):
        return ctx.author.id in BOT or any(role.id in MU_PERMS for role in ctx.author.roles)
    def has_perm_mvc(self, ctx):
        return ctx.author.id in BOT or any(role.id in MVC_PERMS for role in ctx.author.roles)

    @commands.command()
    async def kh(self, ctx, target: discord.Member = None):
        if not self.has_perm_kh(ctx):
            return await ctx.send(" No permission.", delete_after=5)

        if not target:
            return await ctx.send(" Mention a user.", delete_after=5)

        if target.voice and target.voice.channel:
            await ctx.send(f" {target.display_name} is in <#{target.voice.channel.id}>", delete_after=15)
        else:
            await ctx.send(f" {target.display_name} is not in any voice channel.", delete_after=15)

    @commands.command()
    async def drag(self, ctx, target: discord.Member = None):
        if not self.has_perm_drag(ctx):
            return await ctx.send(" No permission.", delete_after=5)

        current_vc_id = ctx.author.voice.channel.id
        in_duo = current_vc_id in DUO_VC_IDS

        # If current VC is a duo VC, check role restriction
        if in_duo and not any(role.id in DUO_ALLOWED_ROLE_IDS for role in ctx.author.roles):
            return await ctx.send(" You are not allowed to use this command in a duo VC.", delete_after=5)

        if not ctx.author.voice:
            return await ctx.send(" You must be in a VC.", delete_after=5)

        if target is None and ctx.message.reference:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            target = replied_msg.author

        if not target:
            return await ctx.send(" Mention or reply to a user.", delete_after=5)

        if not target.voice:
            return await ctx.send(f" {target.display_name} is not in a VC.", delete_after=5)

        if ctx.author.id not in BOT and target.top_role > ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot move higher role.")

        try:
            await target.move_to(ctx.author.voice.channel)
            await ctx.send(f" Moved {target.display_name} to your VC.")
            await log_command(ctx, "drag")
        except discord.Forbidden:
            await ctx.send(" Missing permissions.", delete_after=5)
        except Exception as e:
            await ctx.send(f" Error: {e}")



    @commands.command()
    async def join(self, ctx, *, arg=None):

        member = None

        # Check for reply-based target
        if ctx.message.reference:
            try:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                member = msg.author if isinstance(msg.author, discord.Member) else None
            except:
                pass

        # If not reply, resolve from input (mention, ID, username)
        if not member and arg:
            try:
                member = await commands.MemberConverter().convert(ctx, arg)
            except:
                member = discord.utils.find(
                    lambda m: arg.lower() in m.name.lower() or arg.lower() in m.display_name.lower(),
                    ctx.guild.members
                )

        if not member:
            return await ctx.send(" Could not find the user.", delete_after=5)

        # Ensure target is in a VC
        if not member.voice or not member.voice.channel:
            return await ctx.send(" Target user is not in a voice channel.", delete_after=5)

        vc = member.voice.channel

        # Blocked VC check
        if vc.id in DUO_VC_IDS:
            return await ctx.send(" That voice channel is restricted.", delete_after=5)

        # Check visibility of VC for author
        if not vc.permissions_for(ctx.author).view_channel:
            return await ctx.send(" You don’t have access to that voice channel.", delete_after=5)

        # Ensure author is in a VC before moving
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(" You must be in a voice channel for me to move you.", delete_after=5)

        try:
            await ctx.author.move_to(vc)
            await ctx.send(f" Moved you to **{vc.name}** with {member.display_name}.")
            await log_command(ctx, "join")
        except Exception as e:
            await ctx.send(f" Failed to move: {e}")


    @commands.command()
    async def mu(self, ctx, target: discord.Member = None, new_vc_id: int = None):
        if not self.has_perm_mu(ctx):
            return await ctx.send(" No permission.", delete_after=5)

        if not target or not new_vc_id:
            return await ctx.send(" Usage: .mu <user> <vc_id>")

        if not target.voice:
            return await ctx.send(f" {target.display_name} is not in a VC.", delete_after=5)

        new_vc = ctx.guild.get_channel(new_vc_id)
        if not isinstance(new_vc, discord.VoiceChannel):
            return await ctx.send(" Invalid VC ID.")

        in_duo = new_vc.id in DUO_VC_IDS
        if in_duo and not any(role.id in DUO_ALLOWED_ROLE_IDS for role in ctx.author.roles):
            return await ctx.send(" You are not allowed to use this command in a duo VC.", delete_after=5)

        if ctx.author.id not in BOT and target.top_role > ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(" Cannot move higher role.")

        try:
            await target.move_to(new_vc)
            await ctx.send(f" Moved {target.display_name} to <#{new_vc.id}>.")
            await log_command(ctx, "mu")
        except discord.Forbidden:
            await ctx.send(" Missing permissions.", delete_after=5)
        except Exception as e:
            await ctx.send(f" Error: {e}")

    @commands.command()
    async def mvc(self, ctx, from_vc_id: int = None, to_vc_id: int = None):
        if not self.has_perm_mvc(ctx):
            return await ctx.send(" No permission.", delete_after=5)

        if not from_vc_id or not to_vc_id:
            return await ctx.send(" Usage: .mvc <from_vc_id> <to_vc_id>", delete_after=5)

        from_vc = ctx.guild.get_channel(from_vc_id)
        to_vc = ctx.guild.get_channel(to_vc_id)

        if not isinstance(from_vc, discord.VoiceChannel) or not isinstance(to_vc, discord.VoiceChannel):
            return await ctx.send(" Invalid voice channel IDs.")

        in_duo = from_vc.id in DUO_VC_IDS or to_vc.id in DUO_VC_IDS
        if in_duo and not any(role.id in DUO_ALLOWED_ROLE_IDS for role in ctx.author.roles):
            return await ctx.send(" You are not allowed to use this command for duo VCs.", delete_after=5)

        if not from_vc.members:
            return await ctx.send(" No members to move.", delete_after=5)

        moved, failed = 0, []
        for member in from_vc.members:
            try:
                await member.move_to(to_vc)
                moved += 1
            except:
                failed.append(member.display_name)

        msg = f" Moved {moved} members."
        if failed:
            msg += f" Failed: {', '.join(failed)}"
        await ctx.send(msg)
        await log_command(ctx, "mvc")

    @commands.command(aliases=["dcall"])
    async def disconnect_all(self, ctx, *, arg=None):

        if not self.has_perm_dcall(ctx):
            return await ctx.send(" You don’t have permission to move members.", delete_after=5)

        if not arg:
            return await ctx.send(" Please provide a voice channel name or ID.", delete_after=5)

        vc = self.get_voice_channel(ctx, arg)
        if not vc:
            return await ctx.send(" Voice channel not found.", delete_after=5)

        count = 0
        for member in vc.members:
            if member.bot:
                continue
            if ctx.author.id not in BOT and member.top_role >= ctx.author.top_role:
                continue
            try:
                await member.move_to(None)
                count += 1
            except:
                pass

        await ctx.send(f" Disconnected {count} members from **{vc.name}**.")
        await log_command(ctx, "disconnect_all")

    @commands.command(aliases=["mute"])
    async def server_mute_all(self, ctx, *, arg=None):

        if not self.has_perm_muteall(ctx):
            return await ctx.send(" You don’t have permission to mute members.", delete_after=5)

        if not arg:
            return await ctx.send("Please provide a voice channel name or ID.", delete_after=5)

        vc = self.get_voice_channel(ctx, arg)
        if not vc:
            return await ctx.send(" Voice channel not found.", delete_after=5)

        count = 0
        for member in vc.members:
            if member.bot:
                continue
            if ctx.author.id not in BOT and member.top_role >= ctx.author.top_role:
                continue
            if member.voice and not member.voice.mute:
                try:
                    await member.edit(mute=True)
                    count += 1
                except:
                    pass

        await ctx.send(f" Muted {count} members in **{vc.name}**.")
        await log_command(ctx, "server_mute_all")

    @commands.command(aliases=["unmute"])
    async def server_unmute_all(self, ctx, *, arg=None):

        if not self.has_perm_muteall(ctx):
            return await ctx.send(" You don’t have permission to unmute members.", delete_after=5)

        if not arg:
            return await ctx.send("Please provide a voice channel name or ID.", delete_after=5)

        vc = self.get_voice_channel(ctx, arg)
        if not vc:
            return await ctx.send(" Voice channel not found.", delete_after=5)

        count = 0
        for member in vc.members:
            if member.bot:
                continue
            if ctx.author.id not in BOT and member.top_role >= ctx.author.top_role:
                continue
            if member.voice and member.voice.mute:
                try:
                    await member.edit(mute=False)
                    count += 1
                except:
                    pass

        await ctx.send(f" Unmuted {count} members in **{vc.name}**.")
        await log_command(ctx, "server_unmute_all")


    @commands.command(aliases=["deaf"])
    async def server_deafen_all(self, ctx, *, arg=None):

        if not self.has_perm_defen(ctx):
            return await ctx.send(" You don’t have permission to deafen members.", delete_after=5)

        if not arg:
            return await ctx.send("Please provide a voice channel name or ID.", delete_after=5)

        vc = self.get_voice_channel(ctx, arg)
        if not vc:
            return await ctx.send("Voice channel not found.", delete_after=5)

        count = 0
        for member in vc.members:
            if member.bot:
                continue
            if ctx.author.id not in BOT and member.top_role >= ctx.author.top_role:
                continue
            if member.voice and not member.voice.deaf:
                try:
                    await member.edit(deafen=True)
                    count += 1
                except:
                    pass

        await ctx.send(f" Deafened {count} members in **{vc.name}**.")
        await log_command(ctx, "server_deafen_all")


    @commands.command(aliases=["undeaf"])
    async def server_undeafen_all(self, ctx, *, arg=None):

        if not self.has_perm_defen(ctx):
            return await ctx.send(" You don’t have permission to undeafen members.", delete_after=5)

        if not arg:
            return await ctx.send("Please provide a voice channel name or ID.", delete_after=5)

        vc = self.get_voice_channel(ctx, arg)
        if not vc:
            return await ctx.send(" Voice channel not found.", delete_after=5)

        count = 0
        for member in vc.members:
            if member.bot:
                continue
            if ctx.author.id not in BOT and member.top_role >= ctx.author.top_role:
                continue
            if member.voice and member.voice.deaf:
                try:
                    await member.edit(deafen=False)
                    count += 1
                except:
                    pass

        await ctx.send(f" Undeafened {count} members in **{vc.name}**.")
        await log_command(ctx, "server_undeafen_all")


async def setup(bot):
    await bot.add_cog(VCCommands(bot))