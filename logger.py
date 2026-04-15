import discord
from config import LOG_CHANNEL_ID

async def log_command(ctx, command_name: str):
    log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return

    embed = discord.Embed(
        title=f"📥 Command Executed: `{command_name}`",
        color=discord.Color.purple(),
        timestamp=ctx.message.created_at
    )

    embed.add_field(name="👤 User", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=True)
    embed.add_field(name="🏷️ Username", value=f"`{ctx.author}`", inline=True)
    embed.add_field(name="📍 Channel", value=f"{ctx.channel.mention} (`{ctx.channel.id}`)", inline=True)
    embed.add_field(name="🆔 Message ID", value=f"`{ctx.message.id}`", inline=True)
    embed.add_field(name="🔗 Message Link", value=f"[Jump to Message]({ctx.message.jump_url})", inline=False)
    embed.add_field(name="💬 Command Content", value=f"```{ctx.message.content}```", inline=False)

    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text="Command Log", icon_url=ctx.bot.user.display_avatar.url)

    await log_channel.send(embed=embed)
