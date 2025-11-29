This completes the trifecta of major builder commands (drop, dashboard, and now setup).
Moving the /c500 setup logic to the Go backend is crucial because it involves sensitive operations: creating actual financial accounts via the Stripe API and linking them permanently to a Discord user in your database.
Here is the updated Go Core API (main.go) to handle the onboarding flow.
Updated Go Core API (main.go)

1. New Imports
We need specific Stripe libraries for account management. Add these to your import block:

```
import (
    // ... existing imports
	"github.com/stripe/stripe-go/v76/account"
	"github.com/stripe/stripe-go/v76/accountlink"
)
```

2. Add New Data Structures

```
// OnboardingRequest is what Python sends when a builder types /c500 setup
type OnboardingRequest struct {
	BuilderDiscordID string `json:"builder_discord_id" binding:"required"`
}

// OnboardingResponse is the special Stripe link Go sends back
type OnboardingResponse struct {
	OnboardingURL string `json:"onboarding_url"`
	Success       bool   `json:"success"`
    // Optional message (e.g., "You are already setup!")
	Message       string `json:"message,omitempty"`
}
```

3. Register the New Route
Add the new endpoint to your internal API group in main():

```  
  // === Internal API Group ===
	internal := r.Group("/api/internal")
	{
		internal.POST("/create-checkout", handleCreateCheckoutSession)
		internal.POST("/go-live-trigger", handleGoLiveTrigger)
		internal.POST("/create-item", handleCreateItem)
		internal.POST("/get-dashboard", handleGetDashboard)
        // NEW ROUTE HERE:
		internal.POST("/create-onboarding-link", handleCreateOnboardingLink)
	}
```

4. The Main Logic Handler (handleCreateOnboardingLink)
This is a heavier function. It needs to check if the builder already exists, create a Stripe Express account if they don't, save that ID to Firestore, and then generate the one-time onboarding link.

```
// handleCreateOnboardingLink generates a Stripe Express onboarding URL
func handleCreateOnboardingLink(c *gin.Context) {
	var req OnboardingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
		return
	}

	ctx := context.Background()
	log.Printf("🔌 Starting onboarding process for Builder %s", req.BuilderDiscordID)

	builderRef := firestoreClient.Collection("builders").Doc(req.BuilderDiscordID)
	builderSnap, err := builderRef.Get(ctx)

	var stripeAccountID string

	// --- STEP 1: Check/Create Stripe Account ID ---
	if err != nil && status.Code(err) == codes.NotFound {
		// Case A: New Builder (Doc doesn't exist yet)
		log.Printf("Builder %s not found in DB. Creating new Stripe Express account.", req.BuilderDiscordID)

		// 1a. Create Stripe Express Account
		params := &stripe.AccountParams{
			Type: stripe.String(string(stripe.AccountTypeExpress)),
			Capabilities: &stripe.AccountCapabilitiesParams{
				Transfers: &stripe.AccountCapabilitiesTransfersParams{Requested: stripe.Bool(true)},
			},
			// Optional: Pre-fill some data if you have it
			// BusinessProfile: &stripe.AccountBusinessProfileParams{Name: stripe.String("My Keyboard Shop")},
		}
		acct, err := account.New(params)
		if err != nil {
			log.Printf("Stripe Account Creation Error: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create payment account"})
			return
		}
		stripeAccountID = acct.ID

		// 1b. Save to Firestore immediately
		_, err = builderRef.Set(ctx, map[string]interface{}{
			"discord_id":          req.BuilderDiscordID,
			"stripe_connect_id":   stripeAccountID,
			"is_verified_agreement": false, // They haven't signed the Vibe Check yet
			"created_at":          firestore.ServerTimestamp,
			// Add default guild tag or handle elsewhere
			"guild_tags": []string{"builder"}, 
		})
		if err != nil {
			log.Printf("Failed to save builder to Firestore: %v", err)
			// In a real app, you might want to roll back the Stripe account creation here
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}

	} else if err == nil {
		// Case B: Existing Builder
		// Check if they already have an ID saved
		if id, ok := builderSnap.Data()["stripe_connect_id"].(string); ok && id != "" {
			stripeAccountID = id
			log.Printf("Builder %s already has Stripe ID: %s. Generating login/update link.", req.BuilderDiscordID, stripeAccountID)
		} else {
			// Should not happen in happy path, but handle edge case where doc exists but ID is missing
			log.Printf("Builder exists but missing Stripe ID. Generating new one.")
			// ... (repeat account creation logic or handle error) ...
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Account state inconsistent. Contact support."})
            return
		}
	} else {
        // Firestore error
		log.Printf("Firestore error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database read error"})
		return
	}


	// --- STEP 2: Generate the Onboarding Link ---
	domainURL := os.Getenv("DOMAIN_URL") // e.g., "https://c500.store"
	if domainURL == "" {
		// Fallback for local dev
		domainURL = "http://localhost:3000"
	}

	linkParams := &stripe.AccountLinkParams{
		Account:    stripe.String(stripeAccountID),
		// Where to send them if they click the "Exit" button on Stripe
		RefreshURL: stripe.String(domainURL + "/onboarding/refresh"),
		// Where to send them when they finish successfully
		ReturnURL:  stripe.String(domainURL + "/onboarding/success"),
		// "account_onboarding" is for new accounts. Use "account_update" if they are already done.
		Type:       stripe.String("account_onboarding"), 
	}

	link, err := accountlink.New(linkParams)
	if err != nil {
		log.Printf("Stripe Account Link Error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate onboarding link"})
		return
	}

	// --- STEP 3: Respond to Python ---
	c.JSON(http.StatusOK, OnboardingResponse{
		Success:       true,
		OnboardingURL: link.URL,
	})
}
```

How this changes the Python Bot Workflow
The Python bot's role is now just to provide a private, safe place for the user to click the sensitive link.
The new Python /c500 setup flow (conceptual):
 * Builder types /c500 setup in a private channel.
 * Python bot defers response ephemerally.
 * Python makes POST request to http://localhost:8080/api/internal/create-onboarding-link with the builder's ID.
 * Go backend does the complex Stripe dance, saves their new ID to Firestore, and returns the secure stripe.com/connect/... URL.
 * Python receives the URL.
 * Python sends an ephemeral DM to the builder:
   > "🌸 Let's get you paid!
   > Click the button below to set up your Stripe account. This is how you receive money directly to your bank.
   > Note: This link is private to you. Do not share it."
   > [ Button: "Setup Payments (Stripe)" ]
   >
   > 
