This is the final piece of the technical puzzle for the MVP.
This Python script is the "Front of House." It has very little business logic of its own. Its entire job is to look pretty in Discord, listen for user clicks, and then run back to the Go "kitchen" (API) to get things done.
Developer Prerequisites
 * Python 3.9+ installed.
 * Install necessary libraries:
   pip install discord.py python-dotenv aiohttp

 * CRITICAL: The Go Core API (main.go from two steps ago) must be running on localhost:8080 for this bot to work. The bot needs someone to talk to.
The .env File (Python Version)
Save this in the same folder as your python script.
# Get this from the Discord Developer Portal
DISCORD_BOT_TOKEN=MTE0NzE4NT...

# The ID of your private testing server (for instant command syncing during dev)
TEST_GUILD_ID=1234567890

# The internal URL of the Go backend API
GO_API_URL=http://localhost:8080/api/internal

The bot.py File
import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp # Async HTTP client for talking to Go API

# --- Configuration & Aesthetics ---
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TEST_GUILD_ID = discord.Object(id=int(os.getenv('TEST_GUILD_ID')))
GO_API_URL = os.getenv('GO_API_URL')

# The Cozy Pastel Palette (Hex codes converted to integers for Discord)
COLOR_SAKURA = 0xFFD1DC
COLOR_DREAMY = 0xAEEEEE
COLOR_MINT = 0x98FF98
COLOR_LAVENDER = 0xE6E6FA

# Placeholder Icons for MVP (In real version, these come from DB)
GUILD_ICON_BUILDER = "🛠️"

# --- Bot Setup ---
class C500Bot(commands.Bot):
    def __init__(self):
        # Requesting necessary intents so the bot can see members and messages
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands to the test server immediately for development
        self.tree.copy_global_to(guild=TEST_GUILD_ID)
        await self.tree.sync(guild=TEST_GUILD_ID)
        print(f"☁️ Commands synced to test guild: {TEST_GUILD_ID.id}")

bot = C500Bot()

# --- UI Component: The "Buy Now" Button ---
class BuyView(discord.ui.View):
    def __init__(self, item_id, price_str):
        super().__init__(timeout=None) # View persists indefinitely
        self.item_id = item_id
        self.price_str = price_str

    @discord.ui.button(label="Buy Now with C500", style=discord.ButtonStyle.green, emoji="🛒", custom_id="buy_btn_1")
    async def buy_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Acknowledge the click instantly so it doesn't time out.
        # Ephemeral = only the clicker sees the response.
        await interaction.response.defer(ephemeral=True, thinking=True)

        buyer_id = str(interaction.user.id)
        print(f"🤖 User {buyer_id} clicked buy on item {self.item_id}")

        # 2. THE BRIDGE: Call the Go Backend API
        # We use aiohttp to make an async post request without blocking the bot.
        async with aiohttp.ClientSession() as session:
            payload = {
                "buyer_discord_id": buyer_id,
                "item_id": self.item_id
            }
            try:
                async with session.post(f"{GO_API_URL}/create-checkout", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        checkout_url = data.get('checkout_url')

                        # 3A. Success Response (Cozy DM)
                        embed = discord.Embed(
                            title="Great choice! 🌸",
                            description=f"We have reserved the **Item #{self.item_id}** for you for 10 minutes.\n\nClick below to pay securely via Stripe.",
                            color=COLOR_DREAMY
                        )
                        # Create a link button for the Stripe URL
                        link_view = discord.ui.View()
                        link_view.add_item(discord.ui.Button(label="Secure Checkout (Stripe)", style=discord.ButtonStyle.link, url=checkout_url))

                        # Send followup message containing the link
                        await interaction.followup.send(embed=embed, view=link_view, ephemeral=True)

                    else:
                        # Handle API errors gracefully
                        error_text = await resp.text()
                        print(f"Go API Error: {error_text}")
                        await interaction.followup.send("😓 Oh no! Something went wrong connecting to the C500 vault. Please try again in a moment.", ephemeral=True)

            except Exception as e:
                print(f"Connection Error: {e}")
                await interaction.followup.send("🔥 Critical error connecting to backend service.", ephemeral=True)


# --- UI Component: The Drop Creation Modal (For Builders) ---
class DropModal(discord.ui.Modal, title='Create New C500 Drop 🛍️'):
    # Define the text inputs the builder sees
    item_title = discord.ui.TextInput(
        label='Item Title',
        placeholder='e.g., Snow White TKL - Lubed Gateron Inks',
        max_length=100,
    )
    price = discord.ui.TextInput(
        label='Price ($)',
        placeholder='450.00',
        max_length=10,
    )
    description = discord.ui.TextInput(
        label='Description & Specs',
        style=discord.TextStyle.long,
        placeholder='List switches, keycaps, mods, and build stream status here...',
        max_length=1000,
    )
    image_url = discord.ui.TextInput(
        label='Image URL (Direct Link)',
        placeholder='https://i.imgur.com/your-keyboard.jpg',
    )
    # In the full version, Guild Tag would be a Select Menu outside the modal,
    # but for MVP we assume Builder Guild.

    async def on_submit(self, interaction: discord.Interaction):
        # This runs when the builder clicks "Submit" on the modal.

        # 1. Generate a fake Item ID for the MVP.
        # In real life, Go backend would generate this and save to DB first.
        fake_item_id = f"item_{interaction.id}"

        # 2. Construct the Cozy Pastel Embed
        embed = discord.Embed(
            title=self.item_title.value,
            description=self.description.value,
            color=COLOR_SAKURA # The signature C500 pink border
        )
        embed.set_image(url=self.image_url.value)
        embed.add_field(name="Price", value=f"${self.price.value}", inline=True)
        # Hardcoding Builder Guild icon for MVP demonstration
        embed.add_field(name="Builder", value=f"{interaction.user.mention} {GUILD_ICON_BUILDER}", inline=True)
        embed.set_footer(text="Powered by the C500 Collective | Verified Build")

        # 3. Attach the "Buy Now" button view
        view = BuyView(item_id=fake_item_id, price_str=self.price.value)

        # 4. Post the drop to the channel
        await interaction.response.send_message(embed=embed, view=view)


# --- Slash Commands ---

@bot.tree.command(name="c500-drop", description="[Builder Only] Create a new item listing.")
@app_commands.checks.has_permissions(administrator=True) # Simple permission check for MVP
async def c500_drop(interaction: discord.Interaction):
    # Trigger the modal popup
    await interaction.response.send_modal(DropModal())

# Error handling if a non-admin tries to use the drop command
@c500_drop.error
async def c500_drop_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("🚫 Sorry, only Certified Builders can create drops!", ephemeral=True, color=COLOR_LAVENDER)

# --- Main Execution ---
@bot.event
async def on_ready():
    print(f'✅ C500 Bot is online and cozy as {bot.user} (ID: {bot.user.id})')
    print('---')

bot.run(TOKEN)

How to Test the Whole System (The "Hello World" Moment)
 * Start the Backend: Open a terminal, navigate to your Go folder, and run go run main.go. Ensure it says it's listening on port 8080.
 * Start the Bot: Open a second terminal, navigate to this Python folder, and run python bot.py. Ensure it says "Commands synced."
 * Discord Action: Go to your test Discord server.
 * Type Command: Type /c500-drop. The modal window should pop up.
 * Fill & Submit: Fill in fake details and a real image URL. Click submit.
   * Result: The bot should post the beautiful pastel embed with the green button.
 * Click Buy: Click the "Buy Now with C500" button.
   * Result: You should see a loading state briefly, and then receive an ephemeral DM with a link.
 * Check Logs: Look at your Go terminal. You should see the log message: 🤖 Python Service requesting checkout for Item...
If you see that log message, congratulations. You have officially built a working, federated marketplace prototype connecting Python, Go, Discord, and Stripe.
