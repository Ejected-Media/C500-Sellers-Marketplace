import discord
from discord.ext import commands

class CogManagerControlView(discord.ui.View):
    def __init__(self, bot: commands.Bot, cog_name: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.cog_name = cog_name
        self.update_buttons()

    def update_buttons(self):
        """Dynamically enables/disables buttons based on current runtime extension state."""
        extension_path = f"cogs.{self.cog_name}"
        is_loaded = extension_path in self.bot.extensions

        # Toggle button interactivity depending on active state
        self.load_btn.disabled = is_loaded
        self.reload_btn.disabled = not is_loaded
        self.eject_btn.disabled = not is_loaded

    def build_status_embed(self) -> discord.Embed:
        """Constructs the current runtime status embed for the cog."""
        extension_path = f"cogs.{self.cog_name}"
        is_loaded = extension_path in self.bot.extensions

        embed = discord.Embed(
            title=f"Cog Manager: `{self.cog_name}`",
            description="Manage active runtime status and extension state safely.",
            color=discord.Color.from_rgb(82, 183, 136) if is_loaded else discord.Color.from_rgb(110, 110, 110)
        )
        embed.add_field(
            name="Current Status", 
            value="🟢 **Loaded & Active**" if is_loaded else "🔴 **Unloaded / Ejected**", 
            inline=False
        )
        embed.set_footer(text=f"Target Path: {extension_path}")
        return embed

    @discord.ui.button(label="Load", style=discord.ButtonStyle.success, emoji="📥", custom_id="cog_manager:load")
    async def load_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Loads the extension into active runtime memory."""
        extension_path = f"cogs.{self.cog_name}"
        try:
            if extension_path in self.bot.extensions:
                await interaction.response.send_message(f"⚠️ Cog `{self.cog_name}` is already loaded.", ephemeral=True)
                return

            await self.bot.load_extension(extension_path)
            self.update_buttons()
            
            embed = self.build_status_embed()
            embed.color = discord.Color.from_rgb(82, 183, 136) # Success green
            embed.add_field(name="System Status", value=f"📥 Cog `{self.cog_name}` has been successfully **loaded** into runtime.", inline=False)

            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"✅ Cog `{self.cog_name}` loaded successfully.", ephemeral=True)

        except commands.ExtensionNotFound:
            error_msg = f"❌ Cog path `cogs.{self.cog_name}` could not be found."
            await self._safe_send(interaction, error_msg)
        except commands.NoEntryPointError:
            error_msg = f"❌ Cog `{self.cog_name}` lacks a required `setup` function."
            await self._safe_send(interaction, error_msg)
        except Exception as e:
            error_msg = f"❌ Failed to load `{self.cog_name}`: {e}"
            await self._safe_send(interaction, error_msg)

    @discord.ui.button(label="Reload", style=discord.ButtonStyle.primary, emoji="🔄", custom_id="cog_manager:reload")
    async def reload_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Hot-reloads the extension to apply live code updates without restarting the bot."""
        extension_path = f"cogs.{self.cog_name}"
        try:
            if extension_path not in self.bot.extensions:
                await interaction.response.send_message(f"⚠️ Cog `{self.cog_name}` is not active. Use **Load** instead.", ephemeral=True)
                return

            await self.bot.reload_extension(extension_path)
            self.update_buttons()
            
            embed = self.build_status_embed()
            embed.color = discord.Color.from_rgb(74, 107, 108) # Accent blue/teal
            embed.add_field(name="System Status", value=f"🔄 Cog `{self.cog_name}` has been successfully **reloaded**.", inline=False)

            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"⚡ Cog `{self.cog_name}` hot-reloaded successfully.", ephemeral=True)

        except Exception as e:
            error_msg = f"❌ Error reloading `{self.cog_name}`: {e}"
            await self._safe_send(interaction, error_msg)

    @discord.ui.button(label="Eject", style=discord.ButtonStyle.danger, emoji="🚀", custom_id="cog_manager:eject")
    async def eject_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Safely unloads the cog and clears it from active runtime memory."""
        extension_path = f"cogs.{self.cog_name}"
        try:
            if extension_path not in self.bot.extensions:
                await interaction.response.send_message(f"⚠️ Cog `{self.cog_name}` is not currently loaded.", ephemeral=True)
                return

            await self.bot.unload_extension(extension_path)
            self.update_buttons()
            
            embed = self.build_status_embed()
            embed.color = discord.Color.from_rgb(217, 4, 41) # Alert red
            embed.add_field(name="System Status", value=f"⚠️ Cog `{self.cog_name}` has been safely **ejected** from active runtime.", inline=False)

            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send(f"🚀 Cog `{self.cog_name}` successfully ejected.", ephemeral=True)

        except commands.ExtensionNotLoaded:
            error_msg = f"⚠️ Cog `{self.cog_name}` was not active in runtime memory."
            await self._safe_send(interaction, error_msg)
        except Exception as e:
            error_msg = f"❌ Error ejecting `{self.cog_name}`: {e}"
            await self._safe_send(interaction, error_msg)

    async def _safe_send(self, interaction: discord.Interaction, message: str):
        """Helper to safely route error responses depending on interaction state."""
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
