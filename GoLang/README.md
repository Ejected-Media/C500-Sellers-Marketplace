This is the right move for a robust, cloud-native architecture on Google Cloud.
Here is the updated main.go for the C500 Core Service (Back of House).
This Go service is designed to act as the stable "backend API" that handles money and data. Your separate Python Discord bot service will make simple HTTP requests to this Go service whenever it needs something done (like creating a payment link).
Prerequisites for the Developer
They will need to initialize a Go module and install necessary dependencies:
go mod init c500-core
go get -u github.com/gin-gonic/gin
go get -u cloud.google.com/go/firestore
go get -u github.com/stripe/stripe-go/v76
go get -u github.com/joho/godotenv

The main.go File

```
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"

	"cloud.google.com/go/firestore"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/stripe/stripe-go/v76"
	"github.com/stripe/stripe-go/v76/checkout/session"
	"github.com/stripe/stripe-go/v76/webhook"
	"google.golang.org/api/iterator"
)

// --- Global Clients ---
var firestoreClient *firestore.Client

// --- Data Structures for Internal API ---

// CheckoutRequest is what the Python Bot sends to Go
type CheckoutRequest struct {
	BuyerDiscordID string `json:"buyer_discord_id" binding:"required"`
	ItemID         string `json:"item_id" binding:"required"`
}

// CheckoutResponse is what Go sends back to the Python Bot
type CheckoutResponse struct {
	CheckoutURL string `json:"checkout_url"`
	SessionID   string `json:"session_id"`
}

// --- Initialization ---

func init() {
	// Load .env file for local development
	// In Google Cloud Run, these will be environment variables automatically
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, relying on system environment variables")
	}

	// Initialize Stripe
	stripe.Key = os.Getenv("STRIPE_SECRET_KEY")
	if stripe.Key == "" {
		log.Fatal("STRIPE_SECRET_KEY is not set")
	}
}

func initFirestore() {
	ctx := context.Background()
	projectID := os.Getenv("GOOGLE_CLOUD_PROJECT_ID")
	if projectID == "" {
		log.Fatal("GOOGLE_CLOUD_PROJECT_ID is not set")
	}

	client, err := firestore.NewClient(ctx, projectID)
	if err != nil {
		log.Fatalf("Failed to create Firestore client: %v", err)
	}
	firestoreClient = client
	log.Println("✅ Firestore connected successfully")
}

// --- Handlers ---

// handleCreateCheckoutSession is called internally by the Python Discord Bot service.
// It orchestrates fetching item data and creating the Stripe Destination Charge.
func handleCreateCheckoutSession(c *gin.Context) {
	var req CheckoutRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	ctx := context.Background()

	// 1. Fetch Item Data from Firestore
	// (In a real scenario, you would use req.ItemID to look up real price and seller ID)
	log.Printf("🤖 Python Service requesting checkout for Item: %s by Buyer: %s", req.ItemID, req.BuyerDiscordID)

	// STUB DATA FOR DEMONSTRATION:
	// We assume we fetched this from firestore.Collection("inventory").Doc(req.ItemID)
	itemTitle := "Snow White TKL - Lubed Gateron Inks"
	itemPriceCents := int64(45000) // $450.00
	// This is the Builder's Stripe Connect Express ID fetched from the 'builders' collection
	builderStripeAccountID := "acct_1Nm4WOC4xxxxxxxx" // Replace with a real test connect ID for actual testing

	// 2. Calculate C500 Application Fee (10%)
	platformFee := int64(float64(itemPriceCents) * 0.10)

	// 3. Create Stripe Checkout Session (Destination Charge Logic)
	params := &stripe.CheckoutSessionParams{
		PaymentMethodTypes: stripe.StringSlice([]string{
			"card",
		}),
		LineItems: []*stripe.CheckoutSessionLineItemParams{
			{
				PriceData: &stripe.CheckoutSessionLineItemPriceDataParams{
					Currency: stripe.String(string(stripe.CurrencyUSD)),
					ProductData: &stripe.CheckoutSessionLineItemPriceDataProductDataParams{
						Name: stripe.String(itemTitle),
						// Metadata helps track which Discord item this is for
						Metadata: map[string]string{
							"c500_item_id": req.ItemID,
						},
					},
					UnitAmount: stripe.Int64(itemPriceCents),
				},
				Quantity: stripe.Int64(1),
			},
		},
		Mode: stripe.String(string(stripe.CheckoutSessionModePayment)),
		// This is the crucial part for the Split Payment:
		PaymentIntentData: &stripe.CheckoutSessionPaymentIntentDataParams{
			// The total amount is charged on C500's platform account first
			// Then the remaining amount (Price - Fee) is transferred to the destination
			ApplicationFeeAmount: stripe.Int64(platformFee),
			TransferData: &stripe.CheckoutSessionTransferDataParams{
				Destination: stripe.String(builderStripeAccountID),
			},
			// IMPORTANT: Put the charge "on behalf of" the builder for tax/receipt purposes
			OnBehalfOf: stripe.String(builderStripeAccountID),
			Metadata: map[string]string{
				"buyer_discord_id": req.BuyerDiscordID,
				"item_id":          req.ItemID,
			},
		},
		// Redirect URLs (These would point to a simple C500 success/fail landing page)
		SuccessURL: stripe.String(os.Getenv("DOMAIN_URL") + "/success?session_id={CHECKOUT_SESSION_ID}"),
		CancelURL:  stripe.String(os.Getenv("DOMAIN_URL") + "/cancel"),
	}

	s, err := session.New(params)
	if err != nil {
		log.Printf("Stripe Error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to initiate payment provider"})
		return
	}

	// 4. Return the ephemeral URL to the Python service
	c.JSON(http.StatusOK, CheckoutResponse{
		CheckoutURL: s.URL,
		SessionID:   s.ID,
	})
}

// handleStripeWebhook listens for events from Stripe (like payment success).
func handleStripeWebhook(c *gin.Context) {
	const MaxBodyBytes = int64(65536)
	c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, MaxBodyBytes)
	payload, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.String(http.StatusServiceUnavailable, "Error reading request body")
		return
	}

	webhookSecret := os.Getenv("STRIPE_WEBHOOK_SECRET")
	if webhookSecret == "" {
		log.Fatal("STRIPE_WEBHOOK_SECRET is not set")
	}

	// Validate the signature to ensure it came from Stripe
	event, err := webhook.ConstructEvent(payload, c.GetHeader("Stripe-Signature"), webhookSecret)
	if err != nil {
		c.String(http.StatusBadRequest, "Invalid signature")
		log.Printf("Webhook signature verification failed: %v", err)
		return
	}

	// Handle the specific event type
	switch event.Type {
	case "checkout.session.completed":
		var session stripe.CheckoutSession
		err := json.Unmarshal(event.Data.Raw, &session)
		if err != nil {
			log.Printf("Error parsing webhook JSON: %v", err)
			c.Status(http.StatusBadRequest)
			return
		}

		log.Printf("💰 Payment Successful! Session ID: %s", session.ID)

		// Extract metadata we saved earlier
		buyerID := session.PaymentIntent.Metadata["buyer_discord_id"]
		itemID := session.PaymentIntent.Metadata["item_id"]

		log.Printf("Processing order for Item %s from Buyer %s", itemID, buyerID)

		// TODO FOR DEVELOPER:
		// 1. Update Firestore 'inventory' doc status to 'sold'
		// 2. Create new 'orders' doc in Firestore with status 'paid'
		// 3. (Optional) Fire an event that the Python service listens to,
		//    so it can update the Discord Embed to "Sold".

	default:
		log.Printf("Unhandled webhook event type: %s", event.Type)
	}

	c.Status(http.StatusOK)
}

// --- Main Entrypoint ---

func main() {
	initFirestore()
	defer firestoreClient.Close()

	// Initialize Gin router (using default logger and recovery middleware)
	r := gin.Default()

	// Health Check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "C500 Core is cozy and running properly"})
	})

	// === Internal API Group ===
	// This is where the Python bot will send requests.
	// In production on Google Cloud Run, you would restrict ingress
	// to only allow requests from your Python service's IP/VPC.
	internal := r.Group("/api/internal")
	{
		internal.POST("/create-checkout", handleCreateCheckoutSession)
	}

	// === External Webhooks Group ===
	// Exposed to the public internet for Stripe to hit.
	webhooks := r.Group("/webhooks")
	{
		webhooks.POST("/stripe", handleStripeWebhook)
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("🚀 C500 Core Service starting on port %s...", port)
	r.Run(":" + port)
}
```

How this fits the architecture
 * It's the "Engine Room": This Go program doesn't know anything about Discord channel IDs or embed colors. It only cares about data, money, and APIs.
 * The handleCreateCheckoutSession: This is the critical bridge. Your Python bot will contain code that looks roughly like this:
   # Inside the Python Discord Bot
import requests

async def buy_button_callback(interaction):
    # User clicked buy. Call the Go internal API.
    response = requests.post(
        "http://c500-core-service-url/api/internal/create-checkout",
        json={"buyer_discord_id": str(interaction.user.id), "item_id": "some_item_id"}
    )
    data = response.json()
    checkout_url = data["checkout_url"]

    # Send the cozy ephemeral DM
    await interaction.response.send_message(f"Here is your secure link: {checkout_url}", ephemeral=True)

 * Google Cloud Ready: This code uses standard environment variables (PORT, GOOGLE_CLOUD_PROJECT_ID) that make it ready to deploy directly to Google Cloud Run as a containerized microservice.
 
