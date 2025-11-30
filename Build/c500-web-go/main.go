package main

import (
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

func main() {
	// Use gin.ReleaseMode in production
	// gin.SetMode(gin.ReleaseMode)

	r := gin.Default()

	// --- 1. Static Asset Serving ---
	// Serves files from the ./static directory at the /static path.
	// Expected structure: ./static/css/style.css, ./static/images/logo.png
	r.Static("/static", "./static")
	log.Println("📂 Serving static assets from ./static")

	// --- 2. HTML Template Loading ---
	// Loads all .html files from the ./templates directory.
	// Expected structure: ./templates/index.html, ./templates/success.html
	r.LoadHTMLGlob("templates/*")
	log.Println("📃 Loaded HTML templates from ./templates")

	// --- 3. Routes ---

	// Landing Page
	r.GET("/", func(c *gin.Context) {
		c.HTML(http.StatusOK, "index.html", gin.H{
			"title": "C500 Collective | Cozy Keyboard Marketplace",
		})
	})

	// Stripe Success Return Page
	r.GET("/success", func(c *gin.Context) {
		sessionID := c.Query("session_id")
		if sessionID == "" {
			c.Redirect(http.StatusTemporaryRedirect, "/")
			return
		}
		// This page is just for user confirmation. The actual order processing
		// happens via the Stripe Webhook in the Core API service.
		c.HTML(http.StatusOK, "success.html", gin.H{
			"title": "Payment Successful! 🎉",
			"message": "Your funds are secure in the C500 Vault. Check your Discord DMs for confirmation!",
		})
	})

	// Stripe Cancel Return Page
	r.GET("/cancel", func(c *gin.Context) {
		c.HTML(http.StatusOK, "cancel.html", gin.H{
			"title": "Change of Heart?",
			"message": "No worries! Your cart has been cleared. Stay cozy.",
		})
	})

	// --- Server Start ---
	port := os.Getenv("PORT")
	if port == "" {
		port = "3000" // Standard web port
	}
	log.Printf("🌸 C500 Web Server started at http://localhost:%s", port)
	r.Run(":" + port)
}
