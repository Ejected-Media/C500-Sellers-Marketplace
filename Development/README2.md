This is a great move for consistency. Having both your backend API and your Discord bot written in Go makes your entire stack uniform, highly performant, and easier to deploy as a single unit later on if you choose.
We will use the standard Go Discord library: bwmarrin/discordgo.
While Go is more verbose than Python for UI tasks (like defining modals), it is incredibly robust once written.
Developer Prerequisites
 * Go 1.20+ installed.
 * Create a new folder (e.g., c500-bot-go) and initialize the module:
   mkdir c500-bot-go
cd c500-bot-go
go mod init c500-bot-go

 * Install necessary dependencies:
   go get github.com/bwmarrin/discordgo
go get github.com/joho/godotenv

 * CRITICAL: Ensure your Go Backend API (main.go from the previous steps) is running on localhost:8080.
The .env File
(Same as before, save in the c500-bot-go directory)
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
# The ID of your development server for instant command registration
TEST_GUILD_ID=1234567890
# The URL of your other Go service running locally
GO_API_URL=http://localhost:8080/api/internal

The main.go File (Discord Bot Version)


```
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/bwmarrin/discordgo"
	"github.com/joho/godotenv"
)

// --- Configuration ---
const (
	ColorSakura   = 0xFFD1DC
	ColorDreamy   = 0xAEEEEE
	ColorLavender = 0xE6E6FA
	GuildIconBuilder = "🛠️"
)

var (
	botToken   string
	guildID    string
	goApiUrl   string
)

func init() {
	_ = godotenv.Load()
	botToken = os.Getenv("DISCORD_BOT_TOKEN")
	guildID = os.Getenv("TEST_GUILD_ID")
	goApiUrl = os.Getenv("GO_API_URL")

	if botToken == "" || guildID == "" {
		log.Fatal("Missing required environment variables")
	}
}

func main() {
	// Create Discord session
	dg, err := discordgo.New("Bot " + botToken)
	if err != nil {
		log.Fatalf("Error creating Discord session: %v", err)
	}

	// Register the centralized interaction handler
	dg.AddHandler(interactionHandler)

	// Open websocket connection
	err = dg.Open()
	if err != nil {
		log.Fatalf("Error opening connection: %v", err)
	}
	defer dg.Close()

	// Register the slash command
	// Note: In production, you might register commands globally once, not on every startup.
	cmd := discordgo.ApplicationCommand{
		Name:        "c500-drop",
		Description: "[Builder Only] Create a new item listing.",
	}
	_, err = dg.ApplicationCommandCreate(dg.State.User.ID, guildID, &cmd)
	if err != nil {
		log.Panicf("Cannot create slash command: %v", err)
	}

	log.Println("✅ C500 Go Bot is online and cozy.")
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop
	log.Println("Gracefully shutting down...")
}

// --- The Main Event Router ---
// This function handles ALL interactions: Slash commands, Modals, and Button clicks.
func interactionHandler(s *discordgo.Session, i *discordgo.InteractionCreate) {
	switch i.Type {
	case discordgo.InteractionApplicationCommand:
		handleSlashCommand(s, i)
	case discordgo.InteractionModalSubmit:
		handleModalSubmit(s, i)
	case discordgo.InteractionMessageComponent:
		handleButtonClick(s, i)
	}
}

// --- 1. Handle Slash Command (/c500-drop) ---
func handleSlashCommand(s *discordgo.Session, i *discordgo.InteractionCreate) {
	data := i.ApplicationCommandData()
	if data.Name == "c500-drop" {
		// Send the Modal response
		err := s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseModal,
			Data: &discordgo.InteractionResponseData{
				CustomID: "drop_modal",
				Title:    "Create New C500 Drop 🛍️",
				Components: []discordgo.MessageComponent{
					// TextInput components must be wrapped in ActionsRows
					discordgo.ActionsRow{Components: []discordgo.MessageComponent{
						discordgo.TextInput{CustomID: "item_title", Label: "Item Title", Placeholder: "e.g., Snow White TKL", Style: discordgo.TextInputShort, Required: true},
					}},
					discordgo.ActionsRow{Components: []discordgo.MessageComponent{
						discordgo.TextInput{CustomID: "price", Label: "Price ($)", Placeholder: "450.00", Style: discordgo.TextInputShort, Required: true},
					}},
					discordgo.ActionsRow{Components: []discordgo.MessageComponent{
						discordgo.TextInput{CustomID: "description", Label: "Description & Specs", Style: discordgo.TextInputParagraph, Required: true},
					}},
					discordgo.ActionsRow{Components: []discordgo.MessageComponent{
						discordgo.TextInput{CustomID: "image_url", Label: "Image URL (Direct Link)", Placeholder: "https://...", Style: discordgo.TextInputShort, Required: true},
					}},
				},
			},
		})
		if err != nil {
			log.Printf("Error sending modal: %v", err)
		}
	}
}

// --- 2. Handle Modal Submission (Create the Embed) ---
func handleModalSubmit(s *discordgo.Session, i *discordgo.InteractionCreate) {
	data := i.ModalSubmitData()
	if data.CustomID != "drop_modal" { return }

	// Helper to extract data from nested modal components
	inputs := make(map[string]string)
	for _, row := range data.Components {
		if ar, ok := row.(*discordgo.ActionsRow); ok {
			for _, comp := range ar.Components {
				if ti, ok := comp.(*discordgo.TextInput); ok {
					inputs[ti.CustomID] = ti.Value
				}
			}
		}
	}

	// Generate fake item ID for MVP
	fakeItemID := fmt.Sprintf("item_%s", i.ID)

	// Construct the Cozy Embed
	embed := &discordgo.MessageEmbed{
		Title:       inputs["item_title"],
		Description: inputs["description"],
		Color:       ColorSakura,
		Image:       &discordgo.MessageEmbedImage{URL: inputs["image_url"]},
		Fields: []*discordgo.MessageEmbedField{
			{Name: "Price", Value: fmt.Sprintf("$%s", inputs["price"]), Inline: true},
			{Name: "Builder", Value: fmt.Sprintf("<@%s> %s", i.Member.User.ID, GuildIconBuilder), Inline: true},
		},
		Footer: &discordgo.MessageEmbedFooter{Text: "Powered by the C500 Collective | Verified Build"},
	}

	// Construct the Buy Button
	// We embed the item ID into the customID so we know what they clicked later
	btnCustomID := fmt.Sprintf("buy_btn:%s", fakeItemID)
	button := discordgo.Button{
		Label:    "Buy Now with C500",
		Style:    discordgo.Success, // Green
		Emoji:    discordgo.ComponentEmoji{Name: "🛒"},
		CustomID: btnCustomID,
	}

	// Send the resulting message
	err := s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{
			Embeds: []*discordgo.MessageEmbed{embed},
			Components: []discordgo.MessageComponent{
				discordgo.ActionsRow{Components: []discordgo.MessageComponent{button}},
			},
		},
	})
	if err != nil { log.Printf("Error sending drop message: %v", err) }
}

// --- 3. Handle Button Click (Call Backend API) ---
func handleButtonClick(s *discordgo.Session, i *discordgo.InteractionCreate) {
	customID := i.MessageComponentData().CustomID
	if !strings.HasPrefix(customID, "buy_btn:") { return }

	// 1. Acknowledge click instantly (Deferred Ephemeral) to prevent timeout
	s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
		Type: discordgo.InteractionResponseDeferredChannelMessageWithSource,
		Data: &discordgo.InteractionResponseData{Flags: discordgo.MessageFlagsEphemeral},
	})

	// Extract Item ID from the button's Custom ID
	parts := strings.Split(customID, ":")
	itemID := parts[1]
	buyerID := i.Member.User.ID

	log.Printf("🤖 User %s clicked buy on item %s", buyerID, itemID)

	// 2. THE BRIDGE: Call the Go Backend API
	reqBody, _ := json.Marshal(map[string]string{
		"buyer_discord_id": buyerID,
		"item_id":          itemID,
	})

	resp, err := http.Post(goApiUrl+"/create-checkout", "application/json", bytes.NewBuffer(reqBody))
	if err != nil || resp.StatusCode != http.StatusOK {
		log.Printf("API Error: %v", err)
		s.InteractionResponseEdit(i.Interaction, &discordgo.WebhookEdit{
			Content: strPtr("😓 Oh no! Something went wrong connecting to the C500 vault."),
		})
		return
	}
	defer resp.Body.Close()

	var data map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&data)
	checkoutURL := data["checkout_url"].(string)

	// 3. Success Response (Cozy DM with Link Button)
	embed := &discordgo.MessageEmbed{
		Title:       "Great choice! 🌸",
		Description: "We have reserved the item for you for 10 minutes.\n\nClick below to pay securely via Stripe.",
		Color:       ColorDreamy,
	}
	linkButton := discordgo.Button{
		Label: "Secure Checkout (Stripe)",
		Style: discordgo.Link,
		URL:   checkoutURL,
	}

	// Edit the deferred response with the actual content
	s.InteractionResponseEdit(i.Interaction, &discordgo.WebhookEdit{
		Embeds: []*discordgo.MessageEmbed{embed},
		Components: &[]discordgo.MessageComponent{
			discordgo.ActionsRow{Components: []discordgo.MessageComponent{linkButton}},
		},
	})
}

// Helper for string pointer
func strPtr(s string) *string { return &s }

```

How to Test the Full Go Stack
 * Start the Backend API: Terminal 1 -> cd c500-core -> go run main.go (Ensure it's listening on 8080).
 * Start the Discord Bot: Terminal 2 -> cd c500-bot-go -> go run main.go.
 * Discord: Go to your test server.
 * Run Command: Type /c500-drop. The modal appears. Fill it out.
 * Click Buy: Click the green button on the resulting embed.
 * Verify: You should receive an ephemeral message with a Stripe link, and your Backend API terminal should log the incoming request.
 * 
