import discord
from discord.ext import commands
from discord import app_commands

class TemplateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Standard Prefix Command
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Responds with Pong and latency."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! 🏓 ({latency}ms)')

    # Slash Command (Application Command)
    @app_commands.command(name="hello", description="Says hello to you!")
    async def hello(self, interaction: discord.Interaction):
        """Greets the user who invoked the command."""
        await interaction.response.send_message(f"Hello {interaction.user.mention}! GloxBot is online.")

    # Event Listener within a Cog
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        # Example: Simple auto-responder
        if "glox" in message.content.lower():
            await message.add_reaction("👋")

# Required setup function for the bot to load the cog
async def setup(bot):
    await bot.add_cog(TemplateCog(bot))
