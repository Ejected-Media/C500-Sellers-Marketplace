import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

# 1. Load Environment Variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEV_GUILD_ID = os.getenv('DEV_GUILD_ID')

# 2. Setup Logging
# This creates a file 'glox.log' and also prints to console.
# Useful for debugging why a cog didn't load.
log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger('GloxBot')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('glox.log', encoding='utf-8', mode='w')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# 3. Bot Class Definition
class GloxBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('!'),
            intents=discord.Intents.default(), # Customize intents as needed in Dev Portal
            help_command=commands.DefaultHelpCommand(),
            # If you have a DEV_GUILD_ID, this syncs commands instantly on boot
            tree_cls=discord.app_commands.CommandTree if not DEV_GUILD_ID else type(
                'DevCommandTree', (discord.app_commands.CommandTree,), 
                {'sync': lambda self, guild=discord.Object(id=int(DEV_GUILD_ID)): super().sync(guild=guild)}
            )
        )
        # Store startup time for uptime command
        self.uptime = None 
        # Flag to ensure setup runs only once
        self.synced_commands = False

    async def setup_hook(self):
        """
        This is the modern way to load extensions (cogs) and perform async setup
        before the bot connects to Discord.
        """
        logger.info("--- Loading Cogs ---")
        
        # Iterate through all files in the 'cogs' folder
        cogs_path = Path(__file__).parent / 'cogs'
        for filename in os.listdir(cogs_path):
            if filename.endswith('.py') and filename != '__init__.py':
                extension_name = f'cogs.{filename[:-3]}'
                try:
                    await self.load_extension(extension_name)
                    logger.info(f"✅ Loaded Extension: {extension_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load extension {extension_name}. Error: {e}")
        
        logger.info("--- Cog Loading Complete ---\n")

    async def on_ready(self):
        """
        Called when the bot has successfully connected and is ready.
        """
        if not self.synced_commands:
            try:
                if DEV_GUILD_ID:
                    logger.info(f"Syncing commands to Dev Guild ID: {DEV_GUILD_ID}")
                    # Sync specific to dev guild for speed
                    await self.tree.sync(guild=discord.Object(id=int(DEV_GUILD_ID)))
                else:
                    logger.info("Syncing global commands (can take up to an hour)...")
                    await self.tree.sync()
                self.synced_commands = True
                logger.info("✨ Slash Command Sync Complete ✨")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}")

        # Set activity status
        await self.change_presence(activity=discord.Game(name="Initializing Cogs..."))
        
        if not self.uptime:
            self.uptime = discord.utils.utcnow()

        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info('GloxBot is fully operational.')

# 4. Main Execution
async def main():
    bot = GloxBot()
    async with bot:
        try:
            await bot.start(TOKEN)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
        except Exception as e:
            logger.critical(f"Critical error during runtime: {e}")

if __name__ == '__main__':
    # Ensure required directories exist
    Path("cogs").mkdir(parents=True, exist_ok=True)
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal error starting bot: {e}")
