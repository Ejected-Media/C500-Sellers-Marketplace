from discord.ext import commands

@discord.ui.button(label="Eject Cog", style=discord.ButtonStyle.danger, emoji="🚀")
async def eject_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
    """Safely unloads the cog and clears it from active runtime memory with granular error handling."""
    extension_path = f"cogs.{self.cog_name}"
    
    try:
        if extension_path not in self.bot.extensions:
            raise commands.ExtensionNotLoaded(f"Extension '{extension_path}' is not currently loaded.")

        await self.bot.unload_extension(extension_path)

        self.update_buttons()
        embed = self.build_status_embed()
        embed.color = discord.Color.from_rgb(217, 4, 41)  # Alert red
        embed.add_field(name="System Status", value=f"⚠️ Cog `{self.cog_name}` has been safely **ejected** from active runtime.", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"🚀 Cog `{self.cog_name}` successfully ejected.", ephemeral=True)

    except commands.ExtensionNotLoaded as e:
        error_msg = f"⚠️ Cog `{self.cog_name}` was not active in runtime memory: {e}"
        if interaction.response.is_done():
            await interaction.followup.send(error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(error_msg, ephemeral=True)
            
    except commands.ExtensionNotFound as e:
        error_msg = f"❌ Cog path `cogs.{self.cog_name}` could not be located: {e}"
        if interaction.response.is_done():
            await interaction.followup.send(error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(error_msg, ephemeral=True)

    except Exception as e:
        error_msg = f"❌ Unexpected system error ejecting `{self.cog_name}`: {e}"
        if interaction.response.is_done():
            await interaction.followup.send(error_msg, ephemeral=True)
        else:
            await interaction.response.send_message(error_msg, ephemeral=True)
