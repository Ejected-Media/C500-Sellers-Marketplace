import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp # Async HTTP client required for talking to Go

# --- Configuration & Aesthetics ---
# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
# Test Guild ID for instant command syncing during dev
TEST_GUILD_ID = discord.Object(id=int(os.getenv('TEST_GUILD_ID')))
# The internal URL of the Go Core API service
GO_API_URL = os.getenv('GO_API_URL')

# The Cozy Pastel Palette (Hex codes converted to integers for Discord Embeds)
COLOR_SAKURA = 0xFFD1DC
COLOR_DREAMY = 0xAEEEEE
COLOR_MINT = 0x98FF98
COLOR_LAVENDER = 0xE6E6FA

# Placeholder Icon for MVP
GUILD_ICON_BUILDER = "🛠️"

# --- Bot Setup ---
class C500Bot(commands.Bot):
    def __init__(self):
        # Requesting necessary intents so the bot can see members and content
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands to the test server immediately on startup
        self.tree.copy_global_to(guild=TEST_GUILD_ID)
        await self.tree.sync(guild=TEST_GUILD_ID)
        print(f"☁️ Commands synced to test guild ID: {TEST_GUILD_ID.id}")

bot = C500Bot()

# --- UI Views (Buttons) ---

class BuyView(discord.ui.View):
    """The persistent view attached to product embeds containing the Buy button."""
    def __init__(self, item_id):
        super().__init__(timeout=None) # View persists indefinitely so button always works
        self.item_id = item_id

    @discord.ui.button(label="Buy Now with C500", style=discord.ButtonStyle.green, emoji="🛒")
    async def buy_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Acknowledge the click instantly so it doesn't time out.
        await interaction.response.defer(ephemeral=True, thinking=True)

        print(f"🤖 User {interaction.user.id} clicked buy on item {self.item_id}")

        # TODO:
        # 1. Prepare payload: {"buyer_discord_id": ..., "item_id": self.item_id}
        # 2. Use aiohttp session to POST to f"{GO_API_URL}/create-checkout"
        # 3. Parse response for 'checkout_url'
        # 4. Create a new View with a Link Button pointing to the checkout URL.
        # 5. Send an ephemeral followup DM with a cozy message and the link button.
        await interaction.followup.send("TODO: Implement Buy Button logic connecting to Go backend.", ephemeral=True)


# --- UI Modals (Forms) ---

class DropModal(discord.ui.Modal, title='Create New C500 Drop 🛍️'):
    """The pop-up form builders see when creating a listing."""
    # Define text inputs
    item_title = discord.ui.TextInput(
        label='Item Title', placeholder='e.g., Snow White TKL', max_length=100
    )
    price = discord.ui.TextInput(
        label='Price ($)', placeholder='450.00', max_length=10
    )
    description = discord.ui.TextInput(
        label='Description', style=discord.TextStyle.long, max_length=1000
    )
    image_url = discord.ui.TextInput(
        label='Image URL (Direct Link)', placeholder='https://...'
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Runs when builder clicks Submit on the modal.
        await interaction.response.defer(thinking=True)

        # TODO:
        # 1. Prepare payload with all form inputs and builder ID.
        # 2. Use aiohttp to POST to f"{GO_API_URL}/create-item"
        # 3. Parse response to get real 'item_id' and 'formatted_price'.
        # 4. Construct the Pastel Embed using input data and colors.
        # 5. Instantiate BuyView(item_id=real_item_id).
        # 6. Send the embed and view to the channel.
        await interaction.followup.send("TODO: Implement Drop creation logic connecting to Go backend.", ephemeral=True)


# --- Slash Commands ---

@bot.tree.command(name="c500-drop", description="[Builder] Create a new listing.")
async def c500_drop(interaction: discord.Interaction):
    # TODO: Send the DropModal to the user.
    # await interaction.response.send_modal(DropModal())
    pass

@bot.tree.command(name="c500-setup", description="[Builder] Setup your payment account.")
async def c500_setup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    # TODO:
    # 1. POST to f"{GO_API_URL}/create-onboarding-link" with builder ID.
    # 2. Get 'onboarding_url' from response.
    # 3. Create a Link Button View.
    # 4. Send ephemeral DM with the secure link.
    await interaction.followup.send("TODO: Implement Setup logic.", ephemeral=True)

@bot.tree.command(name="c500-dashboard", description="[Builder] View your shop stats.")
async def c500_dashboard(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    # TODO:
    # 1. POST to f"{GO_API_URL}/get-dashboard" with builder ID.
    # 2. Parse JSON response for stats.
    # 3. Build a pastel embed displaying counts and escrow balance.
    # 4. Send ephemeral response.
    await interaction.followup.send("TODO: Implement Dashboard logic.", ephemeral=True)

@bot.tree.command(name="c500-live", description="[Builder] Trigger verification for an order.")
@app_commands.describe(context="e.g., 'order:12345' or 'chat'")
async def c500_live(interaction: discord.Interaction, context: str):
    await interaction.response.defer(ephemeral=True, thinking=True)
    # TODO:
    # 1. POST to f"{GO_API_URL}/go-live-trigger" with context string.
    # 2. Handle success/error responses from Go.
    # 3. Send ephemeral confirmation message.
    await interaction.followup.send(f"TODO: Implement Go Live logic for context: {context}", ephemeral=True)


# --- Main Execution ---
@bot.event
async def on_ready():
    print(f'✅ C500 Python Bot Skeleton is online as {bot.user} (ID: {bot.user.id})')

# Only run the bot if the token is present
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: DISCORD_BOT_TOKEN not found in .env")
      
