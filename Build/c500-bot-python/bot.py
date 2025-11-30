import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp # Async HTTP client

# --- Configuration ---
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TEST_GUILD_ID = discord.Object(id=int(os.getenv('TEST_GUILD_ID')))
# URL of the Go Core API service (e.g., http://localhost:8080/api/internal)
GO_API_URL = os.getenv('GO_API_URL')

# Cozy Pastel Palette (Integer values for Discord Embeds)
COLOR_SAKURA = 0xFFD1DC
COLOR_DREAMY = 0xAEEEEE
COLOR_MINT = 0x98FF98
COLOR_LAVENDER = 0xE6E6FA

# --- Bot Setup ---
class C500Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True # Required for some command types
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync commands to test server for instant availability during dev
        self.tree.copy_global_to(guild=TEST_GUILD_ID)
        await self.tree.sync(guild=TEST_GUILD_ID)
        print(f"☁️ Commands synced to test guild ID: {TEST_GUILD_ID.id}")

bot = C500Bot()

# --- UI Views (Buttons) ---

class BuyView(discord.ui.View):
    def __init__(self, item_id):
        super().__init__(timeout=None) # View persists indefinitely
        self.item_id = item_id

    @discord.ui.button(label="Buy Now with C500", style=discord.ButtonStyle.green, emoji="🛒")
    async def buy_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        # Call Go API to create checkout session
        async with aiohttp.ClientSession() as session:
            payload = {"buyer_discord_id": str(interaction.user.id), "item_id": self.item_id}
            async with session.post(f"{GO_API_URL}/create-checkout", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    checkout_url = data.get('checkout_url')
                    
                    # Respond with cozy DM containing the link
                    embed = discord.Embed(title="Great choice! 🌸", description="We have reserved the item for you for 10 minutes.\n\nClick below to pay securely via Stripe.", color=COLOR_DREAMY)
                    link_view = discord.ui.View()
                    link_view.add_item(discord.ui.Button(label="Secure Checkout (Stripe)", style=discord.ButtonStyle.link, url=checkout_url))
                    await interaction.followup.send(embed=embed, view=link_view, ephemeral=True)
                else:
                    await interaction.followup.send("😓 Oh no! Something went wrong connecting to the C500 vault.", ephemeral=True)

# --- UI Modals (Forms) ---

class DropModal(discord.ui.Modal, title='Create New C500 Drop 🛍️'):
    item_title = discord.ui.TextInput(label='Item Title', placeholder='e.g., Snow White TKL', max_length=100)
    price = discord.ui.TextInput(label='Price ($)', placeholder='450.00', max_length=10)
    description = discord.ui.TextInput(label='Description', style=discord.TextStyle.long, max_length=1000)
    image_url = discord.ui.TextInput(label='Image URL', placeholder='https://...')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        
        # Call Go API to create item in DB
        async with aiohttp.ClientSession() as session:
            payload = {
                "builder_discord_id": str(interaction.user.id),
                "title": self.item_title.value,
                "description": self.description.value,
                "image_url": self.image_url.value,
                "price_string": self.price.value,
                "guild_tag": "builder" # Default for MVP
            }
            async with session.post(f"{GO_API_URL}/create-item", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    real_item_id = data.get('item_id')
                    formatted_price = data.get('formatted_price')

                    # Create and send the Embed
                    embed = discord.Embed(title=self.item_title.value, description=self.description.value, color=COLOR_SAKURA)
                    embed.set_image(url=self.image_url.value)
                    embed.add_field(name="Price", value=formatted_price, inline=True)
                    embed.add_field(name="Builder", value=interaction.user.mention, inline=True)
                    embed.set_footer(text="Powered by the C500 Collective | Verified Build")
                    
                    # Attach the Buy Button with the real item ID
                    view = BuyView(item_id=real_item_id)
                    await interaction.followup.send(embed=embed, view=view)
                else:
                    await interaction.followup.send("🔥 Error creating drop. Please check your inputs.", ephemeral=True)

# --- Slash Commands ---

@bot.tree.command(name="c500-drop", description="[Builder] Create a new listing.")
async def c500_drop(interaction: discord.Interaction):
    await interaction.response.send_modal(DropModal())

@bot.tree.command(name="c500-setup", description="[Builder] Setup your payment account.")
async def c500_setup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    # Call Go API for onboarding link
    async with aiohttp.ClientSession() as session:
        payload = {"builder_discord_id": str(interaction.user.id)}
        async with session.post(f"{GO_API_URL}/create-onboarding-link", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                url = data.get('onboarding_url')
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="Setup Payments (Stripe)", style=discord.ButtonStyle.link, url=url))
                await interaction.followup.send("🌸 **Let's get you paid!** Click below to set up your Stripe account. Do not share this link.", view=view, ephemeral=True)
            else:
                await interaction.followup.send("Error generating setup link.", ephemeral=True)

@bot.tree.command(name="c500-dashboard", description="[Builder] View your shop stats.")
async def c500_dashboard(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    # Call Go API for stats
    async with aiohttp.ClientSession() as session:
        payload = {"builder_discord_id": str(interaction.user.id)}
        async with session.post(f"{GO_API_URL}/get-dashboard", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                embed = discord.Embed(title="☁️ Your C500 Dashboard", color=COLOR_LAVENDER)
                embed.add_field(name="Active Listings", value=str(data['active_listings_count']), inline=True)
                embed.add_field(name="Pending Orders", value=str(data['pending_orders_count']), inline=True)
                embed.add_field(name="Escrow Balance (Est.)", value=data['total_escrowed_string'], inline=False)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("Error fetching dashboard.", ephemeral=True)

@bot.tree.command(name="c500-live", description="[Builder] Trigger verification for an order.")
@app_commands.describe(context="e.g., 'order:12345' or 'chat'")
async def c500_live(interaction: discord.Interaction, context: str):
    await interaction.response.defer(ephemeral=True, thinking=True)
    # Call Go API to trigger live event
    async with aiohttp.ClientSession() as session:
        payload = {"builder_discord_id": str(interaction.user.id), "live_context": context}
        async with session.post(f"{GO_API_URL}/go-live-trigger", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                await interaction.followup.send(f"✅ {data.get('message')}", ephemeral=True)
            elif resp.status == 409:
                await interaction.followup.send("⚠️ You are not currently live on Twitch.", ephemeral=True)
            else:
                await interaction.followup.send("Error triggering live event.", ephemeral=True)

# --- Main ---
@bot.event
async def on_ready():
    print(f'✅ C500 Python Bot is online as {bot.user}')

bot.run(TOKEN)
              
