This is a great step. Moving the documentation out of scattered Discord channels and onto a central, searchable web page adds a massive layer of professionalism and trust.
Since your website is built in Go using templates, the easiest way to handle this is to create a Markdown file (docs.md) and then have your Go server render it into an HTML template when someone visits /docs.
Here is the content for the C500 Collective Handbook, written in Markdown, maintaining the cozy but professional tone.
☁️ The C500 Collective Handbook
Welcome to the cozy side of the mechanical keyboard hobby.
C500 is a creator-owned marketplace comprised of independent builders, artists, and modders. We exist to make buying high-end, custom keyboards safe, simple, and fun.
This handbook is your guide to navigating the Collective, whether you are here to collect or here to create.
🌸 For Buyers: The Cozy Collectors
We know buying high-end commissions on the internet can be scary. Here is how C500 makes it safe.
How to Shop
C500 isn't one single store; it's a network of trusted builders' private Discord servers.
 * Join a Server: Find a Certified C500 Builder (look for them on Twitter/Twitch) and join their Discord.
 * Browse Drops: Look for the #marketplace or #shop channel. Builders post exclusive "Drops" there using our bot.
 * The Cozy Embed: When you see a board you love, you'll see a beautiful pastel card with photos, specs, and the builder's Guild badges.

The Buying Process & Safety (Escrow)
We use a system called Escrow to protect your money. You never pay a builder directly; you pay C500, and we hold it safe.
 * Click "Buy Now": Click the green button on the Discord drop.
 * Check DMs: The C500 Bot will send you a private, secure Stripe checkout link.
 * The Vault: Once you pay, your money sits in the C500 Escrow Vault. The builder can see the funds are there, but they cannot touch them yet.
 * The Release: Funds are only released to the builder after they verify the work (by streaming the build live on Twitch or providing tracking).
If a builder ghosted you (which won't happen with our certified team, but just in case), C500 can instantly refund you from the vault.

Reputation Tiers & Perks
Trust is our currency. We use a tiered system to ensure safety for high-value items.
 * 👼 Guest Tier: New users.
   * Limit: Can buy items under $150 (Keycaps, switches, accessories).
 * 🌟 Member Tier: Verified users with good history.
   * Requirement: Verify phone number on Discord OR complete 1 successful purchase.
   * Limit: Can buy items up to $600.
 * 👑 VIP Tier: The inner circle.
   * Requirement: Multiple successful purchases with 0 disputes.
   * Perks: Unlimited purchasing cap, access to early-bird drops, and "Pay Later" options.
🛠️ For Builders: The Artisan Collective

C500 exists to let you focus on building and streaming, while the bot handles the boring admin work, payments, and safety.
Becoming Certified
We are currently invitation-only. We look for established builders with a history of quality work on Instagram, Twitch, or Geekhack.
Once accepted, you will receive a Welcome Kit and access to the private Founders Discord to set up your shop.

The Money Flow & Fees
We believe in transparency.
 * The Split: You keep 90% of the sale price. C500 takes a flat 10% platform fee to cover Stripe processing costs, escrow management, bot hosting, and fraud protection.
 * Getting Paid: You must link a bank account via Stripe Express during onboarding.
 * Unlocking Funds: When a buyer pays, the funds are marked as "Pending." To unlock them into your bank account, you must trigger one of two verifications via the bot:
   * Go Live: Stream the build on Twitch and use the /c500 live [OrderID] command.
   * Ship It: Provide a valid tracking number using the /c500 ship [OrderID] command.
Funds are released directly to your Stripe balance immediately upon verification.
The Guilds
Show off your specialty. You will be assigned badges based on your craft, displayed on every drop you make.
 * 🛠️ Builder Guild: Assembly, tuning, and soldering experts.
 * 🎨 Artisan Guild: Sculptors and casters of unique keycaps.
 * 💧 Modder Guild: Specialists in lubing, filming, and refining.
 * 💾 Vintage Guild: Restorers of retro hardware.
✨ The "Vibe Check" (Rules & Safety)

To keep the Collective cozy, we have a strict Zero Tolerance policy for bad actors. Breaking these rules will result in a Global Ban from the entire C500 network of servers.
The Promise
 * Be Kind: No toxicity, harassment, or hate speech. We lift each other up.
 * Be Real (No Scalping): Do not use C500 to flip in-stock items for massive profits. Respect the craft.
 * Honest Listings: Photos and descriptions must accurately reflect the item. No catfishing.
 * The "Friendly Fraud" Rule: Buyers who falsely file chargebacks after receiving an item will be blacklisted globally and evidence will be submitted to their bank.
❓ FAQ & Support
Q: What if my item arrives damaged?
A: All C500 Builders are required to insure their packages. Contact the builder directly in their server first. If you cannot resolve it, open a ticket in the main C500 HQ server, and we will mediate.
Q: Can I cancel an order?
A: Since these are often custom commissions, cancellations are generally up to the individual builder's policy. However, if the builder has not started the work within the agreed timeframe, C500 can process a cancellation from escrow.
Q: Where do I get support?
A: For issues with a specific order, talk to the Builder. For technical issues with the Bot or payments, join the C500 HQ Discord and open a #help-desk ticket.
