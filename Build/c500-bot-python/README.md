Here is the technical overview for the C500 Python Bot (c500-bot-python/bot.py).
This bot is the user interface. It has very little "brain" of its own. Its main job is to look good in Discord, listen for clicks, and then send those signals to the powerful Go Core API to get things done.
🤖 C500 Python Bot Main Functions (Human-Readable)
setup_hook
What it does: Runs immediately when the bot starts up. It takes all the slash commands (like /c500 drop) and instantly syncs them to your private test server so you can use them right away without waiting.
c500_drop (Slash Command)
What it does: When a builder types /c500 drop, this function pops up the "Create New Drop" modal window on their screen so they can enter item details.
DropModal.on_submit
What it does: Runs when the builder clicks "Submit" on the drop modal. It gathers all the text they typed, packages it up, and sends it to the Go Core API to create a real item in the database. Then, it takes the response and posts the beautiful pastel product embed to the channel.
BuyView.buy_callback
What it does: Runs when a buyer clicks the green "Buy Now" button. It grabs the user's ID and the item's ID, sends them to the Go Core API to generate a Stripe checkout link, and then sends that link to the buyer in a private, cozy DM.
c500_setup (Slash Command)
What it does: When a builder types /c500 setup, it asks the Go backend for a special Stripe onboarding link and DM's it to the builder so they can get paid.
c500_dashboard (Slash Command)
What it does: When a builder asks for their stats, this function requests the data from the Go backend and formats it into a private, pastel-themed embed showing their sales and escrow balance.
c500_live (Slash Command)
What it does: Used by builders to trigger a "go live" event (like verifying a build on stream). It simply passes the command and context to the Go backend to handle the logic.
