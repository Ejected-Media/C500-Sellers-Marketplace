This is a significant upgrade to the backend logic. We are moving from a simple transaction processor to a system that understands context and handles differing business logic based on a single command.
To implement the evolved /c500 live command, we need to modify the Go Core API (main.go).
Architectural Note before Coding
This implementation requires your Go backend to actively send messages out to Discord (DMs to buyers, announcements in channels).
In a production environment, you would use a full Go Discord library like discordgo to send these messages. To keep this example readable and focused on the business logic rather than hundreds of lines of API setup, I have stubbed the external API calls (Twitch and Discord message sending) with print statements.
Your developer will need to replace the // TODO: REAL API CALL sections with actual library calls.
Updated Go Core API (main.go)
Here are the additions needed for your existing main.go file.

1. Add New Data Structures
Add these near the top with your other structs. This defines the data payload coming from the Python bot.

```
// GoLiveRequest is the payload sent from Python when /c500 live is run
type GoLiveRequest struct {
	BuilderDiscordID string `json:"builder_discord_id" binding:"required"`
	// LiveContext will be "chat", "drop", "order:123", or "orders:123,456"
	LiveContext      string `json:"live_context" binding:"required"`
}
```

2. Register the New Route
In the main() function, inside the internal := r.Group("/api/internal") block, add the new endpoint:

```
  // === Internal API Group ===
	internal := r.Group("/api/internal")
	{
		internal.POST("/create-checkout", handleCreateCheckoutSession)
		// NEW ROUTE HERE:
		internal.POST("/go-live-trigger", handleGoLiveTrigger)
	}
```

3. The Main Logic Handler (handleGoLiveTrigger)
Add this new function to your handlers section. This is the brain that decides what to do based on the input mode.

```
// handleGoLiveTrigger processes the context of the /c500 live command
func handleGoLiveTrigger(c *gin.Context) {
	var req GoLiveRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	ctx := context.Background()
	log.Printf("🎥 Received Go Live trigger from Builder %s. Context: %s", req.BuilderDiscordID, req.LiveContext)

	// --- STEP 1: Fetch Builder Data & Verify Twitch ---
	// 1. Get builder doc from Firestore to get their Twitch Username
	builderDoc, err := firestoreClient.Collection("builders").Doc(req.BuilderDiscordID).Get(ctx)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Builder profile not found"})
		return
	}
	twitchUsername := builderDoc.Data()["twitch_username"].(string)
	streamLink := fmt.Sprintf("https://twitch.tv/%s", twitchUsername)

	// 2. Verify they are actually live on Twitch
	// (This prevents people from faking the command to unlock funds)
	isLive := mockCheckTwitchStatus(twitchUsername) // <--- REPLACE WITH REAL API CALL
	if !isLive {
		log.Printf("⚠️ Builder %s tried to use /c500 live but Twitch says offline.", req.BuilderDiscordID)
		c.JSON(http.StatusConflict, gin.H{"error": "You are not currently live on Twitch."})
		return
	}

	// --- STEP 2: Determine Mode and Execute Logic ---
	// We parse the "live_context" string (e.g., split "order:123" into mode="order", data="123")
	parts := strings.SplitN(req.LiveContext, ":", 2)
	mode := parts[0]
	data := ""
	if len(parts) > 1 {
		data = parts[1]
	}

	switch mode {
	case "order":
		// MODE 1: Proof of Work (Single Order)
		// data equals single Order ID (e.g., "cs_test_123")
		handleSingleOrderVerification(ctx, data, streamLink)
		c.JSON(http.StatusOK, gin.H{"message": "Order verified and buyer notified."})

	case "orders":
		// MODE 4: Multi-Tasking (Multiple Orders)
		// data equals comma separated IDs (e.g., "cs_123,cs_456")
		orderIDs := strings.Split(data, ",")
		for _, orderID := range orderIDs {
			// Process them sequentially (or use goroutines for parallel processing in prod)
			handleSingleOrderVerification(ctx, strings.TrimSpace(orderID), streamLink)
		}
		c.JSON(http.StatusOK, gin.H{"message": fmt.Sprintf("Processed %d orders.", len(orderIDs))})

	case "chat":
		// MODE 2: General Hangout
		msg := fmt.Sprintf("🔴 **LIVE NOW: Cozy Workshop Vibes**\nCome hang out while I work on projects!\n👉 **Watch here:** %s", streamLink)
		mockSendDiscordChannelMessage("GENERAL_CHANNEL_ID", msg) // <--- REPLACE WITH REAL CALL
		c.JSON(http.StatusOK, gin.H{"message": "Posted hangout announcement."})

	case "drop":
		// MODE 3: Hype Drop Event
		msg := fmt.Sprintf("🚨 **HYPE ALERT: LIVE DROP INCOMING**\nI am streaming right now and will be dropping a limited item DURING the stream.\nDon't miss it!\n👉 **Join the Hype:** %s", streamLink)
		// In real life, ping a role here like @DropNotifications
		mockSendDiscordChannelMessage("MARKETPLACE_CHANNEL_ID", msg) // <--- REPLACE WITH REAL CALL
		c.JSON(http.StatusOK, gin.H{"message": "Posted live drop alert!"})

	default:
		// Unknown mode handle gracefully
		c.JSON(http.StatusBadRequest, gin.H{"error": "Unknown live context mode."})
	}
}
```

4. The Helper Functions (The Business Logic)
Add these functions to handle the specific tasks of updating the database and sending notifications.

```
// --- Helper Logic Functions ---

// handleSingleOrderVerification performs the "Proof of Work" logic
func handleSingleOrderVerification(ctx context.Context, orderID string, streamLink string) {
	log.Printf("Processing verification for OrderID: %s", orderID)

	// 1. Get Order Data from Firestore
	orderRef := firestoreClient.Collection("orders").Doc(orderID)
	orderSnap, err := orderRef.Get(ctx)
	if err != nil {
		log.Printf("Error fetching order %s: %v", orderID, err)
		return
	}
	buyerID := orderSnap.Data()["buyer_id"].(string)

	// 2. Update Firestore: Mark as building and save proof link
	// Using MergeAll to only update specific fields
	_, err = orderRef.Set(ctx, map[string]interface{}{
		"fulfillment_status": "building",
		"twitch_vod_link":    streamLink, // Saving the current stream link as proof
		"updated_at":         firestore.ServerTimestamp,
	}, firestore.MergeAll)

	if err != nil {
		log.Printf("Failed to update order status in DB: %v", err)
		return
	}

	// 3. Notify the Buyer via DM
	dmMessage := fmt.Sprintf("✨ **Exciting News!** Your order (`%s`) is on the workbench RIGHT NOW.\n\nWatch it being built live here: %s", orderID, streamLink)
	mockSendDiscordDM(buyerID, dmMessage) // <--- REPLACE WITH REAL API CALL
}


// --- MOCK EXTERNAL API CALLS (Replace with real libraries in production) ---

func mockCheckTwitchStatus(username string) bool {
	// TODO FOR DEVELOPER: Implement real Twitch Helix API call here.
	// Needs Client-ID and App Access Token. Query /helix/streams?user_login=username
	log.Printf("[MOCK API] Checking Twitch status for %s... returning True (Live)", username)
	return true
}

func mockSendDiscordDM(userID string, message string) {
	// TODO FOR DEVELOPER: Use discordgo to open a DM channel and send message.
	log.Printf("-----\n[MOCK DISCORD DM] To User: %s\nMessage: %s\n-----", userID, message)
}

func mockSendDiscordChannelMessage(channelID string, message string) {
	// TODO FOR DEVELOPER: Use discordgo or a Webhook URL to post to a channel.
	log.Printf("-----\n[MOCK DISCORD CHANNEL POST] To Channel: %s\nMessage: %s\n-----", channelID, message)
}
```

Summary of What We Just Built
You now have a sophisticated Go backend that acts as a central dispatcher.
When the Python bot sends a signal like {"mode": "orders:A,B,C"}, this Go code intelligently parses it, interacts with the database multiple times, and triggers external actions (simulated Discord messages).
This keeps your Python bot stupid (just passing commands along) and your Go backend smart (handling business rules and data integrity).
