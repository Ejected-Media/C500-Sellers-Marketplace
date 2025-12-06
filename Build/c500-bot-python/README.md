# C500-Sellers-Marketplace
## C500-Bot-Python

~

![°](https://github.com/Ejected-Media/C500-Sellers-Marketplace/blob/main/Build/c500-bot-python/pics/Gemini_Generated_Image_ymrghcymrghcymrg.png "$")

![°](https://github.com/Ejected-Media/C500-Sellers-Marketplace/blob/main/Build/c500-bot-python/pics/Gemini_Generated_Image_r1lmmzr1lmmzr1lm.png "$")

![°](https://github.com/Ejected-Media/C500-Sellers-Marketplace/blob/main/Build/c500-bot-python/pics/Gemini_Generated_Image_b2gwneb2gwneb2gw.png "$")

___

![°](https://github.com/Ejected-Media/C500-Sellers-Marketplace/blob/main/Build/c500-bot-python/pics/1764717755729.jpg "$")

___

~

![°](https://github.com/Ejected-Media/C500-Sellers-Marketplace/blob/main/Build/c500-bot-python/pics/1764528446337.jpg "$")

![°](https://github.com/Ejected-Media/C500-Sellers-Marketplace/blob/main/Build/c500-bot-python/pics/1764528373922.jpg "$")

___

_

~


Here is the markdown table for the C500 Python Bot commands, ready for your GitHub README.
🤖 C500 Python Bot Command Reference


| Command / Function | Triggered By | Simplified Purpose |
|---|---|---|
| setup_hook | Bot Startup | Automatically syncs slash commands to the test server for instant availability. |
| /c500 drop | Builder (Slash Command) | Opens a pop-up modal form for a builder to create a new product listing. |
| DropModal.on_submit | Builder (Modal Submit) | Submits drop details to the Go API to create the item, then posts the product embed to the Discord channel. |
| BuyView.buy_callback | Buyer (Button Click) | Requests a secure Stripe checkout link from the Go API and sends it to the buyer in a private DM. |
| /c500 setup | Builder (Slash Command) | Requests a unique Stripe Express onboarding link from the Go API and DM's it to the builder. |
| /c500 dashboard | Builder (Slash Command) | Fetches sales and escrow stats from the Go API and displays them in a private, pastel-themed embed. |
| /c500 live | Builder (Slash Command) | Triggers a "go live" event (e.g., for stream verification) by passing the command context to the Go backend. |


___

Here is the technical overview for the C500 

Python Bot (c500-bot-python/bot.py).
This bot is the user interface. It has very little "brain" of its own. Its main job is to look good in Discord, listen for clicks, and then send those signals to the powerful Go Core API to get things done.

🤖 C500 Python Bot Main Functions (Human-Readable)
setup_hook

What it does: Runs immediately when the bot starts up. It takes all the slash commands (like /c500 drop) and instantly syncs them to your private test server so you can use them right away without waiting.

c500_drop (Slash Command)  
What it does: When a builder types /c500 drop, this function pops up the "Create New Drop" modal window on their screen so they can enter item details.

DropModal.on_submit. 
What it does: Runs when the builder clicks "Submit" on the drop modal. It gathers all the text they typed, packages it up, and sends it to the Go Core API to create a real item in the database. Then, it takes the response and posts the beautiful pastel product embed to the channel.  

BuyView.buy_callback
What it does: Runs when a buyer clicks the green "Buy Now" button. It grabs the user's ID and the item's ID, sends them to the Go Core API to generate a Stripe checkout link, and then sends that link to the buyer in a private, cozy DM.  

c500_setup (Slash Command)
What it does: When a builder types /c500 setup, it asks the Go backend for a special Stripe onboarding link and DM's it to the builder so they can get paid.  

c500_dashboard (Slash Command)
What it does: When a builder asks for their stats, this function requests the data from the Go backend and formats it into a private, pastel-themed embed showing their sales and escrow balance.  

c500_live (Slash Command). 
What it does: Used by builders to trigger a "go live" event (like verifying a build on stream). It simply passes the command and context to the Go backend to handle the logic.


