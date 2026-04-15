# cogs/emoji_sticker.py
from discord.ext import commands
import discord
import aiohttp
import io
from config import STEAL_STICKER_EMOJI, BOT
from logger import log_command 

class EmojiSticker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_perm(self, ctx):
        return ctx.author.id in BOT or any(role.id in STEAL_STICKER_EMOJI for role in ctx.author.roles)
    

    async def download_and_upload(self, url, name, guild, is_emoji=True):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    image_bytes = await resp.read()
                    try:
                        if is_emoji:
                            emoji = await guild.create_custom_emoji(name=name, image=image_bytes)
                            return f" Emoji added: <:{emoji.name}:{emoji.id}>"
                        else:
                            sticker = await guild.create_sticker(
                                name=name,
                                description="Stolen sticker 😈",
                                emoji="😈",
                                file=discord.File(fp=io.BytesIO(image_bytes), filename=f"{name}.png")
                            )
                            return f" Sticker added: {sticker.name}"
                    except discord.Forbidden:
                        return " Missing permissions to add emoji/sticker."
                    except discord.HTTPException as e:
                        return f" Failed to add: {e}"
                return " Could not download file."

    @commands.command()
    async def stealemoji(self, ctx, *args):
        await log_command(ctx, "stealemoji")
        if not self.has_perm(ctx):
            return await ctx.send(" No permission.", delete_after=5)

        emojis_to_steal = set()

        # 1. Parse emojis from command arguments
        for item in args:
            try:
                parsed = await commands.PartialEmojiConverter().convert(ctx, item)
                emojis_to_steal.add(parsed)
            except:
                continue

        # 2. Parse emojis from replied message (if any)
        if ctx.message.reference:
            try:
                ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                for word in ref_msg.content.split():
                    try:
                        parsed = await commands.PartialEmojiConverter().convert(ctx, word)
                        emojis_to_steal.add(parsed)
                    except:
                        continue
            except:
                pass

        if not emojis_to_steal:
            return await ctx.send(" No valid emojis found.", delete_after=5)

        # 3. Try to add each emoji to the guild
        success, failed = [], []
        for emoji in emojis_to_steal:
            try:
                result = await self.download_and_upload(str(emoji.url), emoji.name, ctx.guild, is_emoji=True)
                success.append(emoji.name)
            except Exception as e:
                failed.append((emoji.name, str(e)))

        # 4. Send summary
        msg = ""
        if success:
            msg += f" Added: {', '.join(success)}\n"
        if failed:
            msg += f" Failed: {', '.join(name for name, _ in failed)}"
        await ctx.send(msg or " No emojis could be added.")


    @commands.command()
    async def stealsticker(self, ctx, sticker: discord.Sticker = None):
        await log_command(ctx, "stealsticker")
        if not self.has_perm(ctx):
            return await ctx.send(" No permission.", delete_after=5)

        if ctx.message.reference and sticker is None:
            try:
                replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                if replied_msg.stickers:
                    sticker = replied_msg.stickers[0]
            except:
                pass

        if not sticker:
            return await ctx.send(" Reply to a sticker or provide one.", delete_after=5)
        if sticker.format == discord.StickerFormatType.lottie:
            return await ctx.send(" Lottie stickers are not supported.", delete_after=5)

        result = await self.download_and_upload(str(sticker.url), sticker.name, ctx.guild, is_emoji=False)
        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(EmojiSticker(bot))
