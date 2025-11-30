package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"cloud.google.com/go/firestore"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/stripe/stripe-go/v76"
	"github.com/stripe/stripe-go/v76/account"
	"github.com/stripe/stripe-go/v76/accountlink"
	"github.com/stripe/stripe-go/v76/checkout/session"
	"github.com/stripe/stripe-go/v76/webhook"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// --- Global Clients ---
var firestoreClient *firestore.Client

// --- Data Structures ---

// CreateItemRequest from Python
type CreateItemRequest struct {
	BuilderDiscordID string `json:"builder_discord_id" binding:"required"`
	Title            string `json:"title" binding:"required"`
	Description      string `json:"description" binding:"required"`
	ImageURL         string `json:"image_url" binding:"required"`
	PriceString      string `json:"price_string" binding:"required"`
	GuildTag         string `json:"guild_tag"`
}

// CreateItemResponse to Python
type CreateItemResponse struct {
	ItemID         string `json:"item_id"`
	FormattedPrice string `json:"formatted_price"`
	Success        bool   `json:"success"`
}

// CheckoutRequest from Python
type CheckoutRequest struct {
	BuyerDiscordID string `json:"buyer_discord_id" binding:"required"`
	ItemID         string `json:"item_id" binding:"required"`
}

// CheckoutResponse to Python
type CheckoutResponse struct {
	CheckoutURL string `json:"checkout_url"`
	SessionID   string `json:"session_id"`
}

// GoLiveRequest from Python
type GoLiveRequest struct {
	BuilderDiscordID string `json:"builder_discord_id" binding:"required"`
	LiveContext      string `json:"live_context" binding:"required"`
}

// DashboardRequest from Python
type DashboardRequest struct {
	BuilderDiscordID string `json:"builder_discord_id" binding:"required"`
}

// DashboardResponse to Python
type DashboardResponse struct {
	ActiveListingsCount int    `json:"active_listings_count"`
	PendingOrdersCount  int    `json:"pending_orders_count"`
	TotalEscrowedString string `json:"total_escrowed_string"`
	TotalEscrowedCents  int64  `json:"total_escrowed_cents"`
	Success             bool   `json:"success"`
}

// OnboardingRequest from Python
type OnboardingRequest struct {
	BuilderDiscordID string `json:"builder_discord_id" binding:"required"`
}

// OnboardingResponse to Python
type OnboardingResponse struct {
	OnboardingURL string `json:"onboarding_url"`
	Success       bool   `json:"success"`
}

// --- Initialization ---

func init() {
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, relying on system environment variables")
	}
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

// --- API Handlers ---

// /api/internal/create-item
func handleCreateItem(c *gin.Context) {
	var req CreateItemRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	ctx := context.Background()

	priceCents, err := convertPriceStringToCents(req.PriceString)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid price format"})
		return
	}

	docRef, _, err := firestoreClient.Collection("inventory").Add(ctx, map[string]interface{}{
		"builder_id":  req.BuilderDiscordID,
		"title":       req.Title,
		"description": req.Description,
		"image_url":   req.ImageURL,
		"price_cents": priceCents,
		"status":      "available",
		"guild_tag":   req.GuildTag,
		"created_at":  firestore.ServerTimestamp,
	})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
		return
	}

	c.JSON(http.StatusOK, CreateItemResponse{
		Success:        true,
		ItemID:         docRef.ID,
		FormattedPrice: fmt.Sprintf("$%.2f", float64(priceCents)/100.0),
	})
}

// /api/internal/create-checkout
func handleCreateCheckoutSession(c *gin.Context) {
	var req CheckoutRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	ctx := context.Background()

	// 1. Fetch Item & Builder Data from Firestore
	itemSnap, err := firestoreClient.Collection("inventory").Doc(req.ItemID).Get(ctx)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Item not found"})
		return
	}
	itemData := itemSnap.Data()
	if itemData["status"] != "available" {
		c.JSON(http.StatusConflict, gin.H{"error": "Item is no longer available"})
		return
	}

	builderID := itemData["builder_id"].(string)
	priceCents := itemData["price_cents"].(int64)
	itemTitle := itemData["title"].(string)

	builderSnap, err := firestoreClient.Collection("builders").Doc(builderID).Get(ctx)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Builder data not found"})
		return
	}
	builderStripeID := builderSnap.Data()["stripe_connect_id"].(string)

	// 2. Calculate Fees
	platformFee := int64(float64(priceCents) * 0.10)

	// 3. Create Stripe Checkout Session (Destination Charge)
	domainURL := os.Getenv("DOMAIN_URL")
	params := &stripe.CheckoutSessionParams{
		PaymentMethodTypes: stripe.StringSlice([]string{"card"}),
		LineItems: []*stripe.CheckoutSessionLineItemParams{{
			PriceData: &stripe.CheckoutSessionLineItemPriceDataParams{
				Currency: stripe.String(string(stripe.CurrencyUSD)),
				ProductData: &stripe.CheckoutSessionLineItemPriceDataProductDataParams{
					Name: stripe.String(itemTitle),
				},
				UnitAmount: stripe.Int64(priceCents),
			},
			Quantity: stripe.Int64(1),
		}},
		Mode: stripe.String(string(stripe.CheckoutSessionModePayment)),
		PaymentIntentData: &stripe.CheckoutSessionPaymentIntentDataParams{
			ApplicationFeeAmount: stripe.Int64(platformFee),
			TransferData: &stripe.CheckoutSessionTransferDataParams{
				Destination: stripe.String(builderStripeID),
			},
			OnBehalfOf: stripe.String(builderStripeID),
			Metadata: map[string]string{
				"buyer_discord_id": req.BuyerDiscordID,
				"builder_id":       builderID,
				"item_id":          req.ItemID,
			},
		},
		SuccessURL: stripe.String(domainURL + "/success?session_id={CHECKOUT_SESSION_ID}"),
		CancelURL:  stripe.String(domainURL + "/cancel"),
	}

	s, err := session.New(params)
	if err != nil {
		log.Printf("Stripe Error: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Payment provider error"})
		return
	}

	c.JSON(http.StatusOK, CheckoutResponse{CheckoutURL: s.URL, SessionID: s.ID})
}

// /api/internal/go-live-trigger
func handleGoLiveTrigger(c *gin.Context) {
	var req GoLiveRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	ctx := context.Background()

	// 1. Fetch Builder's Twitch Username
	builderDoc, err := firestoreClient.Collection("builders").Doc(req.BuilderDiscordID).Get(ctx)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Builder profile not found"})
		return
	}
	// In a real app, handle the case where twitch_username is missing/nil
	twitchUsername := builderDoc.Data()["twitch_username"].(string)
	streamLink := fmt.Sprintf("https://twitch.tv/%s", twitchUsername)

	// 2. Verify Live Status (MOCK)
	// TODO: Replace with real Twitch API call
	isLive := true 
	if !isLive {
		c.JSON(http.StatusConflict, gin.H{"error": "You are not live on Twitch."})
		return
	}

	// 3. Process Context
	parts := strings.SplitN(req.LiveContext, ":", 2)
	mode := parts[0]
	data := ""
	if len(parts) > 1 { data = parts[1] }

	switch mode {
	case "order":
		handleSingleOrderVerification(ctx, data, streamLink)
		c.JSON(http.StatusOK, gin.H{"message": "Order verified."})
	// ... other cases (chat, drop) would go here
	default:
		c.JSON(http.StatusBadRequest, gin.H{"error": "Unknown context mode"})
	}
}

// /api/internal/get-dashboard
func handleGetDashboard(c *gin.Context) {
	var req DashboardRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	ctx := context.Background()

	// Query 1: Active Listings
	inventorySnaps, _ := firestoreClient.Collection("inventory").
		Where("builder_id", "==", req.BuilderDiscordID).
		Where("status", "==", "available").
		Documents(ctx).GetAll()
	activeCount := len(inventorySnaps)

	// Query 2: Pending Orders & Escrow Total
	orderSnaps, _ := firestoreClient.Collection("orders").
		Where("builder_id", "==", req.BuilderDiscordID).
		Where("payout_status", "==", "held").
		Documents(ctx).GetAll()
	
	pendingCount := len(orderSnaps)
	var totalGrossCents int64 = 0
	for _, snap := range orderSnaps {
		if cents, ok := snap.Data()["total_paid_cents"].(int64); ok {
			totalGrossCents += cents
		}
	}
	estimatedBuilderShareCents := int64(math.Round(float64(totalGrossCents) * 0.90))
	formattedEscrow := fmt.Sprintf("$%.2f", float64(estimatedBuilderShareCents)/100.0)

	c.JSON(http.StatusOK, DashboardResponse{
		Success:             true,
		ActiveListingsCount: activeCount,
		PendingOrdersCount:  pendingCount,
		TotalEscrowedString: formattedEscrow,
		TotalEscrowedCents:  estimatedBuilderShareCents,
	})
}

// /api/internal/create-onboarding-link
func handleCreateOnboardingLink(c *gin.Context) {
	var req OnboardingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	ctx := context.Background()
	builderRef := firestoreClient.Collection("builders").Doc(req.BuilderDiscordID)
	builderSnap, err := builderRef.Get(ctx)

	var stripeAccountID string

	if err != nil && status.Code(err) == codes.NotFound {
		// Create new Stripe Express Account
		params := &stripe.AccountParams{
			Type: stripe.String(string(stripe.AccountTypeExpress)),
			Capabilities: &stripe.AccountCapabilitiesParams{
				Transfers: &stripe.AccountCapabilitiesTransfersParams{Requested: stripe.Bool(true)},
			},
		}
		acct, err := account.New(params)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Stripe account creation failed"})
			return
		}
		stripeAccountID = acct.ID
		// Save to Firestore
		_, err = builderRef.Set(ctx, map[string]interface{}{
			"discord_id":        req.BuilderDiscordID,
			"stripe_connect_id": stripeAccountID,
			"created_at":        firestore.ServerTimestamp,
		})
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}
	} else if err == nil {
		stripeAccountID = builderSnap.Data()["stripe_connect_id"].(string)
	} else {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database read error"})
		return
	}

	// Generate Onboarding Link
	domainURL := os.Getenv("DOMAIN_URL")
	linkParams := &stripe.AccountLinkParams{
		Account:    stripe.String(stripeAccountID),
		RefreshURL: stripe.String(domainURL + "/onboarding/refresh"),
		ReturnURL:  stripe.String(domainURL + "/onboarding/success"),
		Type:       stripe.String("account_onboarding"),
	}
	link, err := accountlink.New(linkParams)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Link generation failed"})
		return
	}

	c.JSON(http.StatusOK, OnboardingResponse{Success: true, OnboardingURL: link.URL})
}

// /webhooks/stripe
func handleStripeWebhook(c *gin.Context) {
	const MaxBodyBytes = int64(65536)
	c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, MaxBodyBytes)
	payload, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.Status(http.StatusServiceUnavailable)
		return
	}
	webhookSecret := os.Getenv("STRIPE_WEBHOOK_SECRET")
	event, err := webhook.ConstructEvent(payload, c.GetHeader("Stripe-Signature"), webhookSecret)
	if err != nil {
		c.Status(http.StatusBadRequest)
		return
	}

	if event.Type == "checkout.session.completed" {
		var session stripe.CheckoutSession
		json.Unmarshal(event.Data.Raw, &session)
		
		buyerID := session.PaymentIntent.Metadata["buyer_discord_id"]
		builderID := session.PaymentIntent.Metadata["builder_id"]
		itemID := session.PaymentIntent.Metadata["item_id"]
		totalCents := session.AmountTotal

		ctx := context.Background()
		// 1. Mark item as sold
		firestoreClient.Collection("inventory").Doc(itemID).Update(ctx, []firestore.Update{
			{Path: "status", Value: "sold"},
		})
		// 2. Create order record
		firestoreClient.Collection("orders").Doc(session.ID).Set(ctx, map[string]interface{}{
			"buyer_id": buyerID,
			"builder_id": builderID,
			"item_id": itemID,
			"total_paid_cents": totalCents,
			"payout_status": "held",
			"fulfillment_status": "paid",
			"created_at": firestore.ServerTimestamp,
		})
		log.Printf("💰 Order %s created for item %s", session.ID, itemID)
	}
	c.Status(http.StatusOK)
}

// --- Helpers ---

func convertPriceStringToCents(priceStr string) (int64, error) {
	cleaned := strings.ReplaceAll(priceStr, "$", "")
	cleaned = strings.ReplaceAll(cleaned, ",", "")
	priceFloat, err := strconv.ParseFloat(strings.TrimSpace(cleaned), 64)
	if err != nil { return 0, err }
	return int64(math.Round(priceFloat * 100)), nil
}

func handleSingleOrderVerification(ctx context.Context, orderID string, streamLink string) {
	// In a real app, you would verify the order exists first.
	_, err := firestoreClient.Collection("orders").Doc(orderID).Set(ctx, map[string]interface{}{
		"fulfillment_status": "building",
		"twitch_vod_link":    streamLink,
		"updated_at":         firestore.ServerTimestamp,
	}, firestore.MergeAll)
	if err != nil {
		log.Printf("Failed to update order %s: %v", orderID, err)
		return
	}
	// TODO: Trigger a Discord DM to the buyer via a separate service/queue
	log.Printf("✅ Order %s verified via stream. Buyer should be notified.", orderID)
}

// --- Main ---

func main() {
	initFirestore()
	defer firestoreClient.Close()

	r := gin.Default()
	
	// Internal API for Python Bot
	internal := r.Group("/api/internal")
	{
		internal.POST("/create-item", handleCreateItem)
		internal.POST("/create-checkout", handleCreateCheckoutSession)
		internal.POST("/go-live-trigger", handleGoLiveTrigger)
		internal.POST("/get-dashboard", handleGetDashboard)
		internal.POST("/create-onboarding-link", handleCreateOnboardingLink)
	}

	// Public Webhooks
	webhooks := r.Group("/webhooks")
	{
		webhooks.POST("/stripe", handleStripeWebhook)
	}

	port := os.Getenv("PORT")
	if port == "" { port = "8080" }
	log.Printf("🚀 C500 Core Service running on port %s", port)
	r.Run(":" + port)
}
