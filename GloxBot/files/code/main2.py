import pathlib
import discord
from discord.ext import commands
from cogs.cog_manager import CogManagerControlView # Adjust import path as needed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    
    # Automatically scan the cogs directory and register persistent views
    cogs_dir = pathlib.Path("./cogs")
    registered_count = 0
    
    for file in cogs_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue # Skip private files like __init__.py
            
        cog_name = file.stem # Extracts filename without .py extension
        
        # Register the persistent view instance with the bot runtime
        bot.add_view(CogManagerControlView(bot, cog_name))
        registered_count += 1

    print(f"Successfully registered persistent views for {registered_count} cogs.")
