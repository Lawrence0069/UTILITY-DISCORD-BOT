# cogs/help.py
from discord.ext import commands
import discord
from discord.ui import View, Select
from config import HELP_PERMS, BOT
from logger import log_command


class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Vc Cmds", description="Commands related to voice channels"),
            discord.SelectOption(label="Moderation Cmds", description="Ban, kick, timeout, etc."),
            discord.SelectOption(label="Channel Locking Cmds", description="Lock/unlock channels"),
            discord.SelectOption(label="Utility Commands", description="Utility Commands"),
            discord.SelectOption(label="Back", description="Return to main help menu")
        ]
        super().__init__(placeholder="Choose a help category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]

        # Back to home menu
        if category == "Back":
            embed = discord.Embed(
                title="Welcome to Karuta CrossTrade Hub Help Center",
                description="*Your ultimate Discord Moderation & Server Management Bot.* \n\u200b ",
                color=0x8A2BE2
            )
            embed.add_field(
                name="COMMAND CATEGORIES",
                value="",
                inline=False
            )
            embed.add_field(
                name="VC Commands",
                value="`joins, moves, disconnects, mutes — all in voice channels.`",
                inline=False
            )
            embed.add_field(
                name="Moderation Commands",
                value="`Ban, kick, timeout, purge, warn — complete with logging `",
                inline=False
            )
            embed.add_field(
                name="Channel Commands",
                value="`Lock, unlock, hide, slowmode — manage channels like a pro.`",
                inline=False
            )
            embed.add_field(
                name="Utility Commands",
                value="`userinfo, avatar, reminders, emoji/sticker management & more.`\n\u200b",
                inline=False
            )
            embed.set_footer(text="🛠️ Built by Rectrict — crafted for command, built for legacy.")
            await interaction.response.edit_message(embed=embed, view=self.view)
            return

        embed = discord.Embed(title=f"<a:Arrow_White:1379495415606542497> Help: {category}", color=discord.Color.dark_purple())

        if category == "Vc Cmds":
            embed.add_field(name=".kh <user>", value="Displays whether the specified user is currently in a voice channel.", inline=False)
            embed.add_field(name=".drag <user>", value="Moves the specified user to your current voice channel.", inline=False)
            embed.add_field(name=".mu <user> <vc_id>", value="Moves the user to the specified voice channel.", inline=False)
            embed.add_field(name=".mvc <from_vc> <to_vc>", value="Moves all users from one voice channel to another.", inline=False)
            embed.add_field(name=".dcall <vc_id>", value="Disconnects all users from the specified voice channel.", inline=False)
            embed.add_field(name=".join <user>", value="Joins the same voice channel as the specified user.", inline=False)
            embed.add_field(name=".mute/unmute <vc_id>", value="Mutes all users in the specified voice channel.", inline=False)
            embed.add_field(name=".deaf/undeaf <vc_id>", value="Deafens all users in the specified voice channel.", inline=False)

        elif category == "Moderation Cmds":
            embed.add_field(name=".ban <user>", value="Bans the user from the server.", inline=False)
            embed.add_field(name=".unban <user_id>", value="Unbans a user using their User ID.", inline=False)
            embed.add_field(name=".kick <user>", value="Kicks the user from the server.", inline=False)
            embed.add_field(name=".to <user> <duration>", value="Applies a timeout to the user for the specified duration.", inline=False)
            embed.add_field(name=".rto <user>", value="Removes timeout from the user.", inline=False)
            embed.add_field(name=".nick <user> <nickname>", value="Changes the nickname of the specified user.", inline=False)
            embed.add_field(name=".role <user> <role>", value="Assigns the specified role to the user.", inline=False)

        elif category == "Channel Locking Cmds":
            embed.add_field(name=".lock", value="Locks the current channel, preventing @everyone from sending messages.", inline=False)
            embed.add_field(name=".unlock", value="Unlocks the channel for @everyone.", inline=False)
            embed.add_field(name=".lockuser <user>", value="Prevents the user from sending messages in the channel.", inline=False)
            embed.add_field(name=".unlockuser <user>", value="Restores sending permission for the user in the channel.", inline=False)

        elif category == "Utility Commands":
            embed.add_field(name=".say <msg>", value="Bot repeats the specified message.", inline=False)
            embed.add_field(name=".purge <number>", value="Deletes the specified number of recent messages.", inline=False)
            embed.add_field(name=".clear", value="Deletes all messages sent by the bot in the channel.", inline=False)
            embed.add_field(name=".stealemoji", value="Steals and adds an emoji to the server.", inline=False)
            embed.add_field(name=".stealsticker", value="Steals and adds a sticker to the server.", inline=False)
            embed.add_field(name=".ping <role> <msg>", value="Mentions the role with the given message.", inline=False)
            embed.add_field(name=".dumprole <role>", value="Lists all users with the specified role.", inline=False)
            embed.add_field(name=".av <user>", value="Displays the avatar of the specified user.", inline=False)
            embed.add_field(name=".ui <user>", value="Displays the userinfo of the specified user.", inline=False)

        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(HelpSelect())


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_perm(self, ctx):
        return ctx.author.id in BOT or any(role.id in HELP_PERMS for role in ctx.author.roles)

    @commands.command(name="h")
    async def help_command(self, ctx):
        if not self.has_perm(ctx):
            return await ctx.send(" No permission.")

        embed = discord.Embed(
            title="Welcome to The Senctum Obscura Help Center <a:HS_Flower_Welcome:1392739464106741802>",
            description="*Your ultimate Discord Moderation & Server Management Bot.* \n\u200b ",
            color=0x8A2BE2
        )
        embed.add_field(
            name="COMMAND CATEGORIES",
            value="",
            inline=False
        )
        embed.add_field(
            name="VC Commands",
            value="`joins, moves, disconnects, mutes — all in voice channels.`",
            inline=False
        )
        embed.add_field(
            name="Moderation Commands",
            value="`Ban, kick, timeout, purge, warn — complete with logging `",
            inline=False
        )
        embed.add_field(
            name="Channel Commands",
            value="`Lock, unlock, hide, slowmode — manage channels like a pro.`",
            inline=False
        )
        embed.add_field(
            name="Utility Commands",
            value="`userinfo, avatar, reminders, emoji/sticker management & more.`\n\u200b",
            inline=False
        )
        embed.set_footer(text="🛠️ Built by Rectrict — crafted for command, built for legacy.")
        await log_command(ctx, "help")
        await ctx.send(embed=embed, view=HelpView())


async def setup(bot):
    await bot.add_cog(Help(bot))
