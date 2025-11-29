This is the perfect companion piece to the general handbook. This page serves as the "cheat sheet" for your builders, ensuring they know exactly how to operate their storefront.

Here is the Markdown content for the **Builder Command Center** documentation.

***

# 🛠️ Builder Command Center

Welcome to the engine room.

As a Certified C500 Builder, the C500 Bot is your shop manager. It handles payments, tracks inventory, and manages the escrow release so you can get paid.

These commands are powerful. We recommend running them in a **private staff-only channel** on your Discord server so your public chat stays clean.

---

## ⚡ Quick Start: The Essentials

If you only learn three commands, make it these. They are the lifecycle of a sale.

1.  **Sell it:** `/c500 drop` (Opens the menu to list an item)
2.  **Build it:** `/c500 live [OrderID]` (Unlocks funds via stream verification)
3.  **Ship it:** `/c500 ship [OrderID] [Tracking]` (Completes order, releases funds)

---

## 📋 Command Reference Guide

### 1. Getting Started

Before you can sell, the bot needs to know who you are and where to send the money.

#### `/c500 setup`
**Description:** Launches the onboarding wizard. The bot will DM you private links to connect your **Stripe Express** account (for payouts) and your **Twitch** account (for live verification).
* **Usage:** Type once when you first join the Collective.
* *Note: You cannot post drops until Stripe is connected.*

---

### 2. The Shop: Selling Items

This is how you stock your shelves.

#### `/c500 drop`
**Description:** Opens a pop-up modal window to create a new product listing. Once submitted, the bot will post a beautiful, purchasable embed in the current channel.
* **The Modal Inputs:**
    * **Title:** Keep it punchy (e.g., "Snow White TKL - Commission Spot").
    * **Price ($):** Enter the full amount (e.g., `450.00`). The bot handles the 10% fee calculation automatically.
    * **Description:** List specs, flaws, and what's included.
    * **Image URL:** A direct link to a high-res photo (imgur, discord attachment link, etc.).

> 💡 **Pro Tip:** Create the drop in a hidden channel first to preview it. If it looks good, you can drag-and-drop the embed message into your public `#shop` channel.

---

### 3. Getting Paid: Fulfillment & Verification

**Crucial:** When a buyer pays, the funds sit in the **C500 Escrow Vault**. To unlock them into your Stripe account, you must prove you are doing the work.

#### `/c500 live [Order ID]`
**The "Twitch Trigger" (Preferred Method)**
**Description:** Use this *while* you are streaming the build.
1.  Go live on your linked Twitch channel.
2.  Put the Order ID in your stream title or chat.
3.  Run this command in Discord.
* **What happens:** The bot verifies you are live on Twitch. It updates the order status to "Building," DMs the buyer a link to watch, and **marks funds for release**.

#### `/c500 ship [Order ID] [Tracking Number]`
**The "Shipping Trigger" (Final Step)**
**Description:** Use this when the box is sealed and labelled.
* **Usage:** `/c500 ship 12345 USPS 940010000000000000`
* **What happens:** The bot DMs the buyer the tracking info, marks the order complete, and **instantly releases the escrowed funds** to your Stripe balance.

---

### 4. Shop Management

#### `/c500 dashboard`
**Description:** Shows a private overview of your current shop status.
* **Displays:** Active listings, orders waiting to be built, and pending escrow balance.

#### `/c500 vouch @user`
**Description:** Help grow the Collective. If you know a buyer is trustworthy and an asset to the community, vouch for them to give their Reputation Score a small boost.

---

## 🆘 Troubleshooting Commands

If something goes wrong, don't panic.

* **`/c500 help`**: Displays a quick list of available commands within Discord.
* **SUPPORT TICKET:** If a command fails or a payment is stuck, do not try to fix it yourself. Open a ticket in the **C500 HQ Server** `#help-desk` channel immediately.
