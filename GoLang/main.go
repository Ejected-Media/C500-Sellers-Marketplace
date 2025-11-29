package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"cloud.google.com/go/firestore"
	"github.com/gorilla/mux" // Popular router for Go
)

// Product represents a mechanical keyboard product listing in Firestore
type Product struct {
	ID                 string                 `json:"id"`
	SellerID           string                 `json:"sellerId"`
	Name               string                 `json:"name"`
	Description        string                 `json:"description"`
	Category           string                 `json:"category"` // e.g., "Keyboard Kit", "Keycaps", "Switches"
	Price              float64                `json:"price"`
	Images             []string               `json:"images"`
	Stock              int                    `json:"stock"`
	Status             string                 `json:"status"` // e.g., "Active", "Draft", "Archived"
	Variants           map[string]interface{} `json:"variants"` // e.g., {"switchType": "Cherry MX Red", "keycapProfile": "Cherry"}
	ShippingPolicies   map[string]interface{} `json:"shippingPolicies"`
	CreatedAt          time.Time              `json:"createdAt"`
	UpdatedAt          time.Time              `json:"updatedAt"`
}

// Global variables for database client and context
var (
	firestoreClient *firestore.Client
	ctx             context.Context
)

func main() {
	// Initialize context for graceful shutdown
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// --- 1. Initialize Firestore Client ---
	projectID := os.Getenv("GOOGLE_CLOUD_PROJECT")
	if projectID == "" {
		log.Fatalf("GOOGLE_CLOUD_PROJECT environment variable not set.")
	}
	
	var err error
	firestoreClient, err = firestore.NewClient(ctx, projectID)
	if err != nil {
		log.Fatalf("Failed to create Firestore client: %v", err)
	}
	defer firestoreClient.Close()
	log.Printf("Successfully connected to Google Cloud Firestore for project: %s", projectID)

	// --- 2. Setup Router ---
	r := mux.NewRouter()

	// Middleware (e.g., for authentication, logging)
	r.Use(loggingMiddleware)
	r.Use(authMiddleware) // Placeholder for authentication

	// --- 3. Define API Routes and Handlers ---
	// Product Management Endpoints
	r.HandleFunc("/api/seller/products", createProductHandler).Methods("POST")
	r.HandleFunc("/api/seller/{sellerId}/products", getProductsHandler).Methods("GET")
	r.HandleFunc("/api/seller/{sellerId}/products/{productId}", getProductByIDHandler).Methods("GET")
	r.HandleFunc("/api/seller/{sellerId}/products/{productId}", updateProductHandler).Methods("PUT")
	r.HandleFunc("/api/seller/{sellerId}/products/{productId}", deleteProductHandler).Methods("DELETE")

	// Order Management Endpoints (conceptual)
	r.HandleFunc("/api/seller/{sellerId}/orders", getOrdersHandler).Methods("GET")
	r.HandleFunc("/api/seller/{sellerId}/orders/{orderId}", updateOrderStatusHandler).Methods("PUT")

	// Analytics Endpoints (conceptual)
	r.HandleFunc("/api/seller/{sellerId}/analytics", getAnalyticsHandler).Methods("GET")


	// --- 4. Start HTTP Server ---
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080" // Default port if not specified
	}

	server := &http.Server{
		Addr:         ":" + port,
		Handler:      r,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// Goroutine to start the server
	go func() {
		log.Printf("C500 Sellers Marketplace Backend starting on port %s", port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Could not listen on port %s: %v\n", port, err)
		}
	}()

	// --- 5. Graceful Shutdown ---
	// Listen for OS shutdown signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Server is shutting down...")

	// Create a deadline to wait for.
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer shutdownCancel()

	// Doesn't block if there are no connections, but will otherwise wait
	// until the timeout deadline.
	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	log.Println("Server exited gracefully.")
}

// --- Placeholder Middleware Functions ---

// loggingMiddleware logs incoming HTTP requests
func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("[%s] %s %s", r.Method, r.URL.Path, r.RemoteAddr)
		next.ServeHTTP(w, r)
	})
}

// authMiddleware is a placeholder for actual authentication logic
// It would typically validate tokens and authorize the seller.
func authMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// // Example: Check for an Authorization header
		// token := r.Header.Get("Authorization")
		// if token == "" || !isValidToken(token) { // isValidToken would be your actual validation
		// 	http.Error(w, "Unauthorized", http.StatusUnauthorized)
		// 	return
		// }
		//
		// // If authenticated, you might add seller ID to the request context
		// ctx := context.WithValue(r.Context(), "sellerId", "some_seller_id_from_token")
		// next.ServeHTTP(w, r.WithContext(ctx))

		// For now, just pass through (for conceptual purposes)
		next.ServeHTTP(w, r)
	})
}


// --- Placeholder Handler Functions for Product Management ---

// createProductHandler handles POST requests to create a new product listing
func createProductHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Decode request body into a Product struct
	// 2. Validate product data
	// 3. Generate a new product ID
	// 4. Set CreatedAt and UpdatedAt timestamps
	// 5. Save the new product to Firestore (e.g., firestoreClient.Collection("products").Doc(product.ID).Set(ctx, product))
	// 6. Respond with the created product and HTTP 201 Created
	fmt.Fprintf(w, "Create Product API - NOT IMPLEMENTED YET\n")
}

// getProductsHandler handles GET requests to retrieve all products for a given seller
func getProductsHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Extract sellerId from path variables (vars := mux.Vars(r))
	// 2. Query Firestore for products where SellerID matches the extracted sellerId
	// 3. Marshal results into JSON
	// 4. Respond with the list of products
	fmt.Fprintf(w, "Get Products API - NOT IMPLEMENTED YET\n")
}

// getProductByIDHandler handles GET requests to retrieve a single product by ID
func getProductByIDHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Extract sellerId and productId from path variables
	// 2. Query Firestore for the specific product (e.g., firestoreClient.Collection("products").Doc(productId).Get(ctx))
	// 3. Marshal result into JSON
	// 4. Respond with the product or 404 Not Found
	fmt.Fprintf(w, "Get Product By ID API - NOT IMPLEMENTED YET\n")
}

// updateProductHandler handles PUT requests to update an existing product
func updateProductHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Extract sellerId and productId from path variables
	// 2. Decode request body into a Product struct (or a map for partial updates)
	// 3. Validate incoming data
	// 4. Update the product in Firestore (e.g., firestoreClient.Collection("products").Doc(productId).Set(ctx, updatedProduct, firestore.MergeAll))
	// 5. Respond with the updated product
	fmt.Fprintf(w, "Update Product API - NOT IMPLEMENTED YET\n")
}

// deleteProductHandler handles DELETE requests to remove a product
func deleteProductHandler(w http.ResponseWriter, r *http.Request) {
	// 1. Extract sellerId and productId from path variables
	// 2. Delete the product from Firestore (e.g., firestoreClient.Collection("products").Doc(productId).Delete(ctx))
	// 3. Respond with HTTP 204 No Content
	fmt.Fprintf(w, "Delete Product API - NOT IMPLEMENTED YET\n")
}

// --- Placeholder Handler Functions for Order Management (Conceptual) ---

func getOrdersHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Get Orders API - NOT IMPLEMENTED YET\n")
}

func updateOrderStatusHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Update Order Status API - NOT IMPLEMENTED YET\n")
}

// --- Placeholder Handler Functions for Analytics (Conceptual) ---

func getAnalyticsHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Get Analytics API - NOT IMPLEMENTED YET\n")
}
