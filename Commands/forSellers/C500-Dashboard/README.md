This is exactly the right pattern. We are moving the "thinking" out of Python and into Go.
The /c500 dashboard command is a read-only operation. The Python bot needs to ask the Go backend: "Hey, tell me the stats for Builder X," and the Go backend needs to query Firestore and return a neat summary.
Here is the updated Go Core API (main.go) to handle the dashboard logic.
Updated Go Core API (main.go)

1. Add New Data Structures
We need to define what Python asks for, and what Go sends back.

```
// DashboardRequest is what Python sends when a builder types /c500 dashboard
type DashboardRequest struct {
	BuilderDiscordID string `json:"builder_discord_id" binding:"required"`
}

// DashboardResponse is the summary data Go sends back to Python
type DashboardResponse struct {
	ActiveListingsCount int    `json:"active_listings_count"`
	PendingOrdersCount  int    `json:"pending_orders_count"`
	// We send a pre-formatted string for easy display in the Python embed
	TotalEscrowedString string `json:"total_escrowed_string"`
	// We also send raw cents just in case Python needs it
	TotalEscrowedCents  int64  `json:"total_escrowed_cents"`
	Success             bool   `json:"success"`
}
```

2. Register the New Route
Add the new endpoint to your internal API group:

  ```
  // === Internal API Group ===
	internal := r.Group("/api/internal")
	{
		internal.POST("/create-checkout", handleCreateCheckoutSession)
		internal.POST("/go-live-trigger", handleGoLiveTrigger)
		internal.POST("/create-item", handleCreateItem)
        // NEW ROUTE HERE:
		internal.POST("/get-dashboard", handleGetDashboard)
	}
```

3. The Main Logic Handler (handleGetDashboard)
This function needs to run two separate queries against Firestore and calculate a total.

```
// handleGetDashboard aggregates stats for a specific builder
func handleGetDashboard(c *gin.Context) {
	var req DashboardRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
		return
	}

	ctx := context.Background()
	log.Printf("📊 Fetching dashboard stats for Builder %s", req.BuilderDiscordID)

	// --- QUERY 1: Count Active Listings ---
	// Find items belonging to this builder that are marked 'available'
	inventorySnaps, err := firestoreClient.Collection("inventory").
		Where("builder_id", "==", req.BuilderDiscordID).
		Where("status", "==", "available").
		Documents(ctx).GetAll()

	if err != nil {
		log.Printf("Error querying inventory: %v", err)
		// Don't fail completely, just report 0 for now
		inventorySnaps = []*firestore.DocumentSnapshot{}
	}
	activeCount := len(inventorySnaps)


	// --- QUERY 2: Count Pending Orders & Sum Escrow ---
	// Find orders for this builder where funds are still 'held'
	orderSnaps, err := firestoreClient.Collection("orders").
		Where("builder_id", "==", req.BuilderDiscordID).
		Where("payout_status", "==", "held").
		Documents(ctx).GetAll()

	if err != nil {
		log.Printf("Error querying orders: %v", err)
		orderSnaps = []*firestore.DocumentSnapshot{}
	}
	pendingCount := len(orderSnaps)

	// Calculate total gross sales sitting in escrow
	var totalGrossCents int64 = 0
	for _, snap := range orderSnaps {
		// Safely extract the total_paid_cents field
		if cents, ok := snap.Data()["total_paid_cents"].(int64); ok {
			totalGrossCents += cents
		}
	}

	// --- ESTIMATE BUILDER'S SHARE (The 90% Split) ---
	// Important: The REAL split happens on Stripe payout.
	// This calculation is just an estimate for the UI display.
	estimatedBuilderShareCents := int64(math.Round(float64(totalGrossCents) * 0.90))

	// Format string: e.g., $1250.50
	formattedEscrow := fmt.Sprintf("$%.2f", float64(estimatedBuilderShareCents)/100.0)


	// --- FINAL RESPONSE ---
	c.JSON(http.StatusOK, DashboardResponse{
		Success:             true,
		ActiveListingsCount: activeCount,
		PendingOrdersCount:  pendingCount,
		TotalEscrowedString: formattedEscrow,
		TotalEscrowedCents:  estimatedBuilderShareCents,
	})
}
```

How this changes the Python Bot Workflow
The Python bot's role becomes very simple: ask for data, receive data, format data into a pretty embed.
The new Python /c500 dashboard flow (conceptual):
 * Builder types /c500 dashboard.
 * Python bot defers response (shows "thinking...").
 * Python makes POST request to http://localhost:8080/api/internal/get-dashboard with the builder's ID.
 * Go backend runs the Firestore queries and returns json:
 
```
   {
  "success": true,
  "active_listings_count": 3,
  "pending_orders_count": 2,
  "total_escrowed_string": "$850.00",
  "total_escrowed_cents": 85000
}
```

 * Python receives JSON.
 * Python constructs a "Cozy Pastel" embed using those numbers and sends it as an ephemeral message so only the builder sees their financial info.
 * 
