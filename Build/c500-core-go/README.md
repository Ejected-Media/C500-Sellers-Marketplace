This is a great way to visualize the "engine room" of your operation.
The c500-core-go/main.go file is the central nervous system. It doesn't have a user interface; its only job is to listen for instructions, talk to the database (Firestore), handle money (Stripe), and check external facts (Twitch).
Here is a human-readable outline of its main functions, grouped by responsibility.
The "Engine Room" (c500-core-go/main.go) Overview

1. Internal Actions (Requests from the Python Bot)
These functions run when a user or builder clicks something in Discord. The Python bot sends a signal here to get the heavy lifting done.
 * Saving a New Drop (handleCreateItem)
   * What it does: Receives the title, photo, and price from the builder's Discord modal. It safely converts the price into cents (e.g., "$450.00" becomes 45000) and saves the item into the Firestore database as "available."
   * Why it matters: It ensures financial data is stored correctly and creates the official database record for the item.
 * Generating the Payment Link (handleCreateCheckoutSession)
   * What it does: When a buyer clicks "Buy Now," this function looks up the item's price and the builder's Stripe ID. It then tells Stripe to create a secure checkout page that automatically splits the payment (10% to C500, 90% to the Builder).
   * Why it matters: This is the core of the business model. It ensures payments are secure and splits are handled automatically by Stripe before the money even touches your bank.
 * Creating Stripe Setup Links (handleCreateOnboardingLink)
   * What it does: Checks if a builder already has a Stripe Express account in the database. If not, it tells Stripe to create one and generates a secure, one-time link for the builder to finish setting up their banking info.
   * Why it matters: It’s the bridge that allows builders to get paid directly to their bank accounts.
 * Calculating Dashboard Stats (handleGetDashboard)
   * What it does: runs queries against the database to count how many active items and pending orders a specific builder has. It also sums up the total value of funds currently held in escrow for them.
   * Why it matters: It provides the data for the private financial snapshot builders see in Discord.
 * Verifying a "Go Live" Event (handleGoLiveTrigger)
   * What it does: When a builder types /c500 live, this function checks the real Twitch API to ensure they are actually streaming. If they are, it updates the specific order status in the database from "Paid" to "Building."
   * Why it matters: This is the "Proof of Work" mechanism that stops builders from unlocking funds without actually doing the work.

2. External Actions (Listening to the Outside World)
These functions wait for signals from other powerful systems.
 * Processing Successful Payments (handleStripeWebhook)
   * What it does: This is a secure listener that waits for Stripe to shout, "Hey! Payment session ID #123 just finished successfully!" It verifies the signal is genuine, then instantly marks the item as "Sold" in the database and creates a formal Order record.
   * Why it matters: It closes the loop on a sale automatically, 24/7, without humans needing to check bank statements.

3. Startup & Helpers (Keeping the Lights On)
 * Server Startup (main)
   * What it does: The ignition key. It loads the secret API keys (for Stripe/Twitch), connects to the Google Firestore database, and starts listening for incoming requests on specific ports.
 * Safely Handling Money Math (convertPriceStringToCents)
   * What it does: A small utility that takes messy human inputs like "$450.00" or "450,00" and converts them into a clean integer representing cents (45000).
   * Why it matters: Prevents dangerous rounding errors in financial calculations.
   * 
