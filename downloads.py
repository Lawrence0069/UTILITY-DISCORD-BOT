import aiohttp, io, discord

async def download_and_upload(url, name, guild, is_emoji=True):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return "❌ Couldn't download file."
            image_bytes = await resp.read()
            try:
                if is_emoji:
                    emoji = await guild.create_custom_emoji(name=name, image=image_bytes)
                    return f"✅ Emoji added: <:{emoji.name}:{emoji.id}>"
                else:
                    sticker = await guild.create_sticker(
                        name=name,
                        description="Stolen sticker 😈",
                        emoji="😈",
                        file=discord.File(io.BytesIO(image_bytes), filename=f"{name}.png")
                    )
                    return f"✅ Sticker added: {sticker.name}"
            except discord.Forbidden:
                return "❌ Permission denied."
            except discord.HTTPException as e:
                return f"❌ Error: {e}"
