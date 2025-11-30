This is a high-level technical overview of the C500 Collective codebase, designed for a developer jumping into the project.
The architecture is a Microservices-based system with three main components operating on Google Cloud.

1. The Python Discord Bot ("Front of House")
Directory: c500-bot-python/
Stack: Python 3.9+, discord.py, aiohttp
This service is the user interface living inside Discord. It holds very little business logic. Its primary job is to render "cozy pastel" embeds, handle user interactions (slash commands, buttons, modals), and forward requests to the Go Core API.
 * bot.py: The main executable.
   * Slash Commands: Registers commands like /c500 drop (for builders) and /c500 profile (for buyers).
   * UI/UX: Defines the modal windows for creating drops and the view classes for buttons like "Buy Now."
   * API Client: Uses aiohttp to make asynchronous, non-blocking POST requests to the Go Core API’s internal endpoints (e.g., /api/internal/create-checkout).
 * .env: Stores the Discord Bot Token and the base URL for the internal Go Core API.

2. The Go Core API ("Engine Room")
Directory: c500-core-go/
Stack: Go 1.20+, gin-gonic (HTTP framework), Google Firestore, Stripe Go SDK
This is the central brain and source of truth. It operates as a backend API that handles data persistence, financial transactions, and external integrations. It is designed to be stable, performant, and secure.
 * main.go: The single-file entry point for the service.
   * Internal API Routes (/api/internal/*): Endpoints that accept JSON requests from the Python bot to perform actions like creating database items, generating Stripe checkout sessions, or fetching dashboard data.
   * Public Webhook Routes (/webhooks/*): Endpoints exposed to the public internet to handle events from Stripe (e.g., checkout.session.completed) and Twitch (e.g., stream.online).
   * Firestore Integration: Manages all reads and writes to the Google Firestore NoSQL database collections (users, builders, inventory, orders).
   * Stripe Logic: Handles complex operations like creating Express accounts, generating split-payment checkout sessions, and processing webhooks.
 * go.mod / go.sum: Manages Go dependencies.
 * .env: Stores sensitive API keys for Stripe (Secret Key, Webhook Secret), Twitch, and Google Cloud project configuration.

3. The Go Web Server ("Public Frontend")
Directory: c500-web-go/
Stack: Go 1.20+, gin-gonic, HTML/CSS
This service hosts the public-facing website at C500.store. It is separate from the Core API to isolate public traffic from internal logic.
 * main.go: The simple web server.
   * Static File Serving: Serves CSS, images, and fonts from the /static directory.
   * HTML Rendering: Renders Go HTML templates for pages like the landing page (/), the "About" page, and Stripe return pages (/success, /cancel).
 * templates/: Directory containing HTML files (index.html, success.html, etc.). These use Go's html/template syntax for dynamic data injection.
 * static/css/style.css: The main stylesheet defining the "cozy pastel" aesthetic, including custom color variables and font definitions.

External Services & Shared Config
 * Google Firestore: The NoSQL database storing all persistent data.
 * Stripe Connect: The payment platform handling marketplace transactions, escrow, and builder payouts.
 * Twitch API (EventSub): Used to detect when a builder goes live for verification.
 * .env (Shared Concept): Each service has its own .env file containing its specific configuration and secret keys. In a production Google Cloud Run environment, these would be set as environment variables.
 * 
