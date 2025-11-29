package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

func main() {
	// Set Gin to production mode for launch
	// gin.SetMode(gin.ReleaseMode)

	r := gin.Default()

	// --- 1. Static Asset Serving ---
	// This tells Gin: "If a request starts with /static, look in the local './static' folder."
	// This is how you serve your pastel CSS and cute images.
	r.Static("/static", "./static")
	log.Println("📂 Serving static assets from ./static")

	// --- 2. HTML Template Loading ---
	// Tell Gin where to find your .html files.
	// Using LoadHTMLGlob allows you to have a folder full of templates.
	r.LoadHTMLGlob("templates/*")
	log.Println("📃 Loaded HTML templates from ./templates")

	// --- 3. Routes ---

	// GET / -> The Landing Page
	// This is what people see when they visit C500.store
	r.GET("/", func(c *gin.Context) {
		// Render the index.html template.
		// We pass a data map in case the template needs dynamic info (e.g., page title).
		c.HTML(http.StatusOK, "index.html", gin.H{
			"title": "C500 Collective | Cozy Keyboard Marketplace",
			// You could pass brand colors here if your template uses them dynamically
			"themeColor": "#FFD1DC", // Sakura Milk
		})
	})

	// GET /about -> Explaining the project
	r.GET("/about", func(c *gin.Context) {
		c.HTML(http.StatusOK, "about.html", gin.H{
			"title": "About the Collective",
		})
	})

	// --- Stripe Return Handlers ---

	// GET /success -> Where Stripe redirects after a successful payment.
	// Stripe will append the session ID like: /success?session_id=cs_test_xxxx
	r.GET("/success", func(c *gin.Context) {
		sessionID := c.Query("session_id")

		if sessionID == "" {
			// If they hit this page directly without paying, redirect home.
			c.Redirect(http.StatusTemporaryRedirect, "/")
			return
		}

		log.Printf("🎉 Serving Success Page for Session: %s", sessionID)

		// Render the cute "Payment Successful!" page.
		// NOTE: We don't verify the session ID against the DB here.
		// The Stripe Webhook in the CORE service handles the actual verification logic.
		// This page is just for user reassurance.
		c.HTML(http.StatusOK, "success.html", gin.H{
			"title": "YAY! Payment Got!",
			"message": "Your funds are secure in the C500 Vault. Check your Discord DMs for confirmation!",
		})
	})

	// GET /cancel -> Where Stripe redirects if they back out of checkout.
	r.GET("/cancel", func(c *gin.Context) {
		// Render a gentle "It's okay, maybe next time" page.
		c.HTML(http.StatusOK, "cancel.html", gin.H{
			"title": "Change of Heart?",
			"message": "No worries! Your cart has been cleared. Stay cozy.",
		})
	})

	// --- Server Start ---
	port := os.Getenv("PORT")
	if port == "" {
		port = "3000" // Standard web port used by many frontend apps
	}
	log.Printf("🌸 C500 Web Server started at http://localhost:%s", port)
	r.Run(":" + port)
}
