import discord
from discord.ext import commands

class CogManagerControlView(discord.ui.View):
    def __init__(self, bot: commands.Bot, cog_name: str):
        # timeout=None is required for persistent views
        super().__init__(timeout=None)
        self.bot = bot
        self.cog_name = cog_name
        
        # Dynamically add buttons with custom_ids containing the cog name
        self.add_item(DynamicCogButton(cog_name, "Load", discord.ButtonStyle.success, "📥", "load"))
        self.add_item(DynamicCogButton(cog_name, "Reload", discord.ButtonStyle.primary, "🔄", "reload"))
        self.add_item(DynamicCogButton(cog_name, "Eject", discord.ButtonStyle.danger, "🚀", "eject"))
        self.update_button_states()

    def update_button_states(self):
        extension_path = f"cogs.{self.cog_name}"
        is_loaded = extension_path in self.bot.extensions
        
        for item in self.children:
            if isinstance(item, DynamicCogButton):
                if item.action == "load":
                    item.disabled = is_loaded
                else:
                    item.disabled = not is_loaded

    def build_status_embed(self) -> discord.Embed:
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

class DynamicCogButton(discord.ui.Button):
    def __init__(self, cog_name: str, label: str, style: discord.ButtonStyle, emoji: str, action: str):
        self.cog_name = cog_name
        self.action = action
        # Unique persistent custom_id containing both the cog name and action
        super().__init__(
            label=label,
            style=style,
            emoji=emoji,
            custom_id=f"cog_mgr:{cog_name}:{action}"
        )

    async def callback(self, interaction: discord.Interaction):
        bot: commands.Bot = interaction.client
        extension_path = f"cogs.{self.cog_name}"
        view: CogManagerControlView = self.view

        try:
            if self.action == "load":
                if extension_path in bot.extensions:
                    await interaction.response.send_message(f"⚠️ Cog `{self.cog_name}` is already loaded.", ephemeral=True)
                    return
                await bot.load_extension(extension_path)
                status_text = f"📥 Cog `{self.cog_name}` has been successfully **loaded** into runtime."
                toast_text = f"✅ Cog `{self.cog_name}` loaded successfully."
                embed_color = discord.Color.from_rgb(82, 183, 136)

            elif self.action == "reload":
                if extension_path not in bot.extensions:
                    await interaction.response.send_message(f"⚠️ Cog `{self.cog_name}` is not active.", ephemeral=True)
                    return
                await bot.reload_extension(extension_path)
                status_text = f"🔄 Cog `{self.cog_name}` has been successfully **reloaded**."
                toast_text = f"⚡ Cog `{self.cog_name}` hot-reloaded successfully."
                embed_color = discord.Color.from_rgb(74, 107, 108)

            elif self.action == "eject":
                if extension_path not in bot.extensions:
                    await interaction.response.send_message(f"⚠️ Cog `{self.cog_name}` is not currently loaded.", ephemeral=True)
                    return
                await bot.unload_extension(extension_path)
                status_text = f"⚠️ Cog `{self.cog_name}` has been safely **ejected** from active runtime."
                toast_text = f"🚀 Cog `{self.cog_name}` successfully ejected."
                embed_color = discord.Color.from_rgb(217, 4, 41)

            view.update_button_states()
            embed = view.build_status_embed()
            embed.color = embed_color
            embed.add_field(name="System Status", value=status_text, inline=False)

            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send(toast_text, ephemeral=True)

        except Exception as e:
            error_msg = f"❌ Error executing `{self.action}` on `{self.cog_name}`: {e}"
            if interaction.response.is_done():
                await interaction.followup.send(error_msg, ephemeral=True)
            else:
                await interaction.response.send_message(error_msg, ephemeral=True)
