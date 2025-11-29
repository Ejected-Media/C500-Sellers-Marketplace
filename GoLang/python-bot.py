# Inside the Python Discord Bot
import requests

async def buy_button_callback(interaction):
    # User clicked buy. Call the Go internal API.
    response = requests.post(
        "http://c500-core-service-url/api/internal/create-checkout",
        json={"buyer_discord_id": str(interaction.user.id), "item_id": "some_item_id"}
    )
    data = response.json()
    checkout_url = data["checkout_url"]

    # Send the cozy ephemeral DM
    await interaction.response.send_message(f"Here is your secure link: {checkout_url}", ephemeral=True)
  
