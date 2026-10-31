@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    
    # Register the persistent view with the bot runtime
    # Note: If you manage multiple specific cogs, you'll register an instance for each active control panel 
    # or pass a wildcard/dispatcher handler depending on your architecture.
    bot.add_view(CogManagerControlView(bot, "throne"))
    bot.add_view(CogManagerControlView(bot, "zoho_books"))
    
    print("Persistent views registered successfully.")
