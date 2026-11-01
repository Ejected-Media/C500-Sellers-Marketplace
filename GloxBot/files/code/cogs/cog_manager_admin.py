import pathlib
import discord
from discord import app_commands
from discord.ext import commands

class CogManagerAdmin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Autocomplete callback function
    async def cog_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Scans the cogs directory and returns matching choices based on user input."""
        cogs_dir = pathlib.Path("./cogs")
        choices = []
        
        if cogs_dir.exists():
            for file in cogs_dir.glob("*.py"):
                if file.name.startswith("_"):
                    continue # Skip helper files like __init__.py
                
                cog_name = file.stem
                
                # Filter choices based on what the user is currently typing (case-insensitive)
                if current.lower() in cog_name.lower():
                    choices.append(app_commands.Choice(name=cog_name, value=cog_name))
        
        # Discord allows a maximum of 25 autocomplete choices per response
        return choices[:25]

    @app_commands.command(name="managecog", description="Open the control panel for any project cog.")
    @app_commands.describe(cog_name="Select or type the name of the cog to manage")
    @app_commands.autocomplete(cog_name=cog_autocomplete)
    @app_commands.checks.has_permissions(administrator=True)
    async def manage_cog(self, interaction: discord.Interaction, cog_name: str):
        # Import your persistent view here
        from cogs.cog_manager import CogManagerControlView
        
        view = CogManagerControlView(self.bot, cog_name)
        embed = view.build_status_embed()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CogManagerAdmin(bot))
