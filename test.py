import discord
from discord.ext import commands

BOT_TOKEN = "MTM4NTE5NzQ3MjUyMzIyNzI0OA.G_Rj8x.SaxTe0ZdILeA8-Nq-3dYlFWkt3-OX8HXl_yYvU"

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def perm(ctx, role_id: int, server_id: int, perm_type: str):
    """Set a role's permissions in a specific server.
    Usage: .perm <role_id> <server_id> admin
    """
    guild = bot.get_guild(server_id)
    if not guild:
        await ctx.send("❌ Server not found or bot not in that server.")
        return

    role = guild.get_role(role_id)
    if not role:
        await ctx.send("❌ Role not found.")
        return

    # Apply permissions
    if perm_type.lower() == "admin":
        perms = discord.Permissions(administrator=True)
        await role.edit(permissions=perms)
        await ctx.send(f"✅ {role.name} now has Administrator permissions in {guild.name}")
    else:
        await ctx.send("❌ Unknown permission type. Currently only `admin` is supported.")

bot.run(BOT_TOKEN)
