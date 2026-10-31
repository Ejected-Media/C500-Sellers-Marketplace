import os
import pathlib
import logging
import discord
from discord.ext import commands
from discord import app_commands

logger = logging.getLogger("GloxBot.CogManager")

class CogManagerView(discord.ui.View):
    """Interactive control panel view for managing bot cogs."""
    def __init__(self, bot, cog_name: str):
        super().__init__(timeout=180)
        self.bot = bot
        self.cog_name = cog_name
        self.update_buttons()

    def update_buttons(self):
        extension_path = f"cogs.{self.cog_name}"
        is_loaded = extension_path in self.bot.extensions
        
        # Toggle state indicators on buttons
        self.load_btn.disabled = is_loaded
        self.unload_btn.disabled = not is_loaded
        self.reload_btn.disabled = not is_loaded
        self.eject_btn.disabled = not is_loaded

    @discord.ui.button(label="Load / Install", style=discord.ButtonStyle.green, emoji="📥")
    async def load_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        extension_path = f"cogs.{self.cog_name}"
        try:
            await self.bot.load_extension(extension_path)
            self.update_buttons()
            await interaction.response.edit_message(embed=self.build_status_embed(), view=self)
            await interaction.followup.send(f"✅ Successfully loaded/installed cog: `{self.cog_name}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to load `{self.cog_name}`: {e}", ephemeral=True)

    @discord.ui.button(label="Unload", style=discord.ButtonStyle.secondary, emoji="⏸️")
    async def unload_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        extension_path = f"cogs.{self.cog_name}"
        try:
            await self.bot.unload_extension(extension_path)
            self.update_buttons()
            await interaction.response.edit_message(embed=self.build_status_embed(), view=self)
            await interaction.followup.send(f"⏸️ Successfully unloaded cog: `{self.cog_name}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unload `{self.cog_name}`: {e}", ephemeral=True)

    @discord.ui.button(label="Reload", style=discord.ButtonStyle.primary, emoji="🔄")
    async def reload_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        extension_path = f"cogs.{self.cog_name}"
        try:
            await self.bot.reload_extension(extension_path)
            self.update_buttons()
            await interaction.response.edit_message(embed=self.build_status_embed(), view=self)
            await interaction.followup.send(f"🔄 Successfully reloaded cog: `{self.cog_name}`", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to reload `{self.cog_name}`: {e}", ephemeral=True)

    @discord.ui.button(label="Eject Cog", style=discord.ButtonStyle.danger, emoji="🚀")
    async def eject_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Safely unloads the cog and clears it from active runtime memory."""
        extension_path = f"cogs.{self.cog_name}"
        try:
            if extension_path in self.bot.extensions:
                await self.bot.unload_extension(extension_path)
            
            self.update_buttons()
            embed = self.build_status_embed()
            embed.color = discord.Color.from_rgb(217, 4, 41) # Alert red
            embed.add_field(name="System Status", value=f"⚠️ Cog `{self.cog_name}` has been safely **ejected** from active runtime.", inline=False)
            
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"🚀 Cog `{self.cog_name}` successfully ejected.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error ejecting `{self.cog_name}`: {e}", inline=False, ephemeral=True)

    def build_status_embed(self) -> discord.Embed:
        extension_path = f"cogs.{self.cog_name}"
        is_loaded = extension_path in self.bot.extensions
        
        embed = discord.Embed(
            title=f"⚙️ Cog Management Console: `{self.cog_name}.py`",
            color=discord.Color.from_rgb(82, 183, 136) if is_loaded else discord.Color.from_rgb(128, 128, 128)
        )
        embed.add_field(name="Runtime State", value="🟢 **ACTIVE** (Loaded)" if is_loaded else "⚪ **INACTIVE** (Unloaded/Ejected)", inline=False)
        embed.add_field(name="Target Scope", value="Zerg Temple PHX • Up To A Boil HR / Logistics", inline=False)
        embed.set_footer(text="GloxBot Core Architecture • Modular Control Deck")
        return embed


class CogManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    cog_group = app_commands.Group(name="cog", description="Manage, install, configure, and eject bot cogs")

    @cog_group.command(name="control", description="Open the interactive control interface for a specific cog")
    @app_commands.describe(cog_name="The filename of the cog without extension (e.g., throne, template)")
    @app_commands.checks.has_any_role("core-ops", "Admin", "Founder")
    async def cog_control(self, interaction: discord.Interaction, cog_name: str):
        # Validate if file exists in cogs directory
        cog_file = pathlib.Path(__file__).parent / f"{cog_name}.py"
        if not cog_file.exists():
            await interaction.response.send_message(f"❌ Error: Cog file `cogs/{cog_name}.py` does not exist on disk.", ephemeral=True)
            return

        view = CogManagerView(self.bot, cog_name)
        embed = view.build_status_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @cog_group.command(name="list", description="List all available cogs and their current load status")
    @app_commands.checks.has_any_role("core-ops", "Admin", "Founder")
    async def cog_list(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        cogs_dir = pathlib.Path(__file__).parent
        embed = discord.Embed(
            title="📋 GloxBot System Cogs Inventory",
            color=discord.Color.from_rgb(74, 107, 108) # Copper Oxidation (#4a6b6c)
        )

        cog_files = [f.stem for f in cogs_dir.glob("*.py") if f.stem != "__init__"]
        
        for cog in sorted(cog_files):
            ext_path = f"cogs.{cog}"
            is_loaded = ext_path in self.bot.extensions
            status = "🟢 Loaded" " (Active)" if is_loaded else "⚪ Unloaded"
            embed.add_field(name=f"{cog}.py", value=status, inline=True)

        embed.set_footer(text="Use /cog control <name> to install, reload, or eject individual modules.")
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CogManagerCog(bot))
