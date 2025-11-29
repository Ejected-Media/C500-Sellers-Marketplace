This is the exact right approach. We need to move the "state change" (creating a new item in the database) out of the Python bot and into the Go backend.
Previously, your Python bot was creating a fake item ID. Now, it will ask the Go backend to create a real item ID in Firestore before posting the embed.
Here is the updated Go Core API (main.go) to handle the /c500 drop logic.
Updated Go Core API (main.go)

1. Add New Data Structures
We need structs to define what data the Python bot sends when a builder submits the drop modal, and what Go sends back.

```
// CreateItemRequest is the data submitted by the builder in the Discord Modal
type CreateItemRequest struct {
	BuilderDiscordID string `json:"builder_discord_id" binding:"required"`
	Title            string `json:"title" binding:"required"`
	Description      string `json:"description" binding:"required"`
	ImageURL         string `json:"image_url" binding:"required"`
	// We accept price as a string (e.g., "450.00") to handle user input safely
	PriceString      string `json:"price_string" binding:"required"`
	GuildTag         string `json:"guild_tag"` // e.g., "builder", "artisan"
}

// CreateItemResponse is what we send back to Python so it can build the Embed
type CreateItemResponse struct {
	ItemID         string `json:"item_id"`          // The REAL Firestore ID
	FormattedPrice string `json:"formatted_price"`  // e.g., "$450.00"
	Success        bool   `json:"success"`
}
```

2. Register the New Route
In the main() function, add the new endpoint to the internal group:

  ```
  // === Internal API Group ===
	internal := r.Group("/api/internal")
	{
		internal.POST("/create-checkout", handleCreateCheckoutSession)
		internal.POST("/go-live-trigger", handleGoLiveTrigger)
        // NEW ROUTE HERE:
		internal.POST("/create-item", handleCreateItem)
	}
```

3. The Main Logic Handler (handleCreateItem)
This function receives the raw form data, converts the price to cents, saves it to Firestore, and returns the new real ID.

```
// handleCreateItem processes the submission of the "Create Drop" modal
func handleCreateItem(c *gin.Context) {
	var req CreateItemRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		log.Printf("Error binding JSON: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
		return
	}

	ctx := context.Background()
	log.Printf("📦 Creating new item for Builder %s: %s", req.BuilderDiscordID, req.Title)

	// --- STEP 1: Price Conversion (String -> Cents) ---
	priceCents, err := convertPriceStringToCents(req.PriceString)
	if err != nil {
		log.Printf("Price conversion error for '%s': %v", req.PriceString, err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid price format. Use format like '450.00'"})
		return
	}

	// --- STEP 2: Save to Firestore ---
	// We use .Add() to let Firestore generate a unique ID for us.
	// Note: In a real app, you should verify the builderId exists in the 'builders' collection first.
	docRef, _, err := firestoreClient.Collection("inventory").Add(ctx, map[string]interface{}{
		"builder_id":   req.BuilderDiscordID,
		"title":        req.Title,
		"description":  req.Description,
		"image_url":    req.ImageURL,
		"price_cents":  priceCents,
		"status":       "available", // Default status
		"guild_tag":    req.GuildTag, // Default to "builder" if empty in prod logic
		"created_at":   firestore.ServerTimestamp,
	})

	if err != nil {
		log.Printf("Failed to save item to Firestore: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error saving item"})
		return
	}

	realItemID := docRef.ID
	log.Printf("✅ Item created successfully. ID: %s", realItemID)

	// --- STEP 3: Respond to Python ---
	// Return the real ID so Python can attach it to the "Buy Now" button
	c.JSON(http.StatusOK, CreateItemResponse{
		Success:        true,
		ItemID:         realItemID,
		// Send back a clean formatted string for the embed display
		FormattedPrice: fmt.Sprintf("$%.2f", float64(priceCents)/100.0),
	})
}
```

4. The Helper Function (Safety)
Handling money requires care. We need a safe way to turn user input like "450.00" into integer cents (45000).
Add this helper function at the bottom of your file:

```
import (
    // ... existing imports
    "strconv"
    "math"
)

// convertPriceStringToCents safely converts "450.00" or "450" to int64 45000
func convertPriceStringToCents(priceStr string) (int64, error) {
	// Remove any existing $ signs or commas just in case
	cleaned := strings.ReplaceAll(priceStr, "$", "")
	cleaned = strings.ReplaceAll(cleaned, ",", "")
	cleaned = strings.TrimSpace(cleaned)

	// Convert string to float
	priceFloat, err := strconv.ParseFloat(cleaned, 64)
	if err != nil {
		return 0, fmt.Errorf("invalid price format")
	}

	// IMPORTANT: Financial rounding to avoid floating point errors.
	// Multiply by 100 to get cents, round to nearest whole number.
	cents := int64(math.Round(priceFloat * 100))

	if cents <= 0 {
		return 0, fmt.Errorf("price must be greater than zero")
	}

	return cents, nil
}
```

How this changes the Python Bot Workflow
Now your Go backend is doing the heavy lifting. Your Python bot's on_submit modal handler needs to change from immediately posting an embed to first calling this API.
The new Python flow (conceptual):
 * Builder submits Modal.
 * Python gathers data.
 * Python makes POST request to http://localhost:8080/api/internal/create-item.
 * Go creates DB entry and returns {"item_id": "REAL_FIRESTORE_ID_123"}.
 * Python receives that ID.
 * Python creates the embed and attaches the Buy Button using custom_id="buy_btn:REAL_FIRESTORE_ID_123".
 * Python posts the message.
Now, when a user clicks "Buy," the ID in the button is a real ID that the backend recognizes.
