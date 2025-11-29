This is the other side of the coin. While builders have complex commands for managing their shops, Buyers need simplicity.
A buyer's interaction with the C500 Bot should feel almost invisible—like a helpful assistant that only pops up when needed. They don't want to learn a CLI; they just want to buy cool stuff and know it's safe.
Here is the overview of the C500 Buyer Commands & Interactions, designed for the cozy, low-friction experience we want.
C500 Buyer Command & Interaction Guide
Philosophy: Buyers should rarely have to type a command. Most of their interactions are via buttons on embeds or automated DMs from the bot.

1. The Core Interaction: Buying
There is no /buy command. The act of buying is trigger-based.
 * Action: Buyer clicks the "Buy Now with C500" button on a product embed in a builder's server.
 * Bot Response (Ephemeral DM):
   > "🌸 Great choice! We've reserved this item for you for 10 minutes.
   > Click below to pay secure via Stripe.
   > [ Secure Checkout (Stripe) ]"
   > 
 * Outcome: The user leaves Discord to pay on a secure Stripe page.

2. Order Tracking & History
Buyers need a way to see what they've bought and its status without digging through DMs.
 * Command: /c500 orders (or /c500 history)
 * Context: Can be run in any server where the bot is present, or in a DM with the bot.
 * Bot Response (Ephemeral Embed): A private, scrollable list of their purchase history across the entire Collective.
> [Embed Title] My Cozy Collection 📦
> Snow White TKL (Order #12345)
>  * Builder: @Keyz (Builder Guild 🛠️)
>  * Status: 🟡 Building (Live Stream Proof: [twitch.tv/link])
>  * Price: $450.00
> Pastel Deskmat (Order #67890)
>  * Builder: @CozyCaps (Artisan Guild 🎨)
>  * Status: 🟢 Shipped (Tracking: USPS 9400...)
> Need help with an order? Contact the builder directly in their server.
> 

3. Reputation & Profile
Gamification for buyers to see their standing in the community.
 * Command: /c500 profile (or /c500 rep)
 * Context: Any server or DM.
 * Bot Response (Ephemeral Embed): A cute "passport" style card showing their trust tier.
> [Embed Title] C500 Citizen Passport ✨
> User: @Alex
> Tier: 👑 VIP Citizen
> Reputation Score: 850 Points
> Your Perks:
>  * ✅ Unlimited Purchase Cap
>  * ✅ Access to Early-Bird Drops
>  * ✅ "Pay Later" Eligible
> Keep collecting to maintain your VIP status!
> 

4. Trust & Safety Actions
How a buyer handles issues.
 * Command: /c500 report [Order ID] (This is a "Nuclear Option")
 * Context: DM with the Bot ONLY.
 * Usage: Used only if a builder has gone completely silent after funds were released, or if there is a severe safety issue.
 * Bot Response: Opens a formal ticket directly with C500 HQ admins. It does not notify the builder.
 * Command: /c500 verify [Service] (e.g., /c500 verify twitch)
 * Context: DM with the Bot.
 * Purpose: For "Guest" tier buyers to quickly level up their trust score by linking external accounts.
 * Bot Response: Sends an OAuth link to connect their Twitch or Reddit account to prove they are a real person.
Summary of Buyer Commands

| Command | Purpose | Vibe |
|---|---|---|
| (Button Click) | The main way to buy. | "Ooh, I want that!" |
| /c500 orders | Check status of pending/past buys. | "Where's my stuff?" |
| /c500 profile | Check trust tier and perks. | "How cool am I?" |
| /c500 verify | Link accounts to gain trust. | "I'm real, I swear." |
| /c500 report | Emergency only help from HQ. | "Something is wrong." |
