This is a very insightful question. It drills down into the core operational differences between the platforms.
If you rewrite the bot in GoLang so the entire stack is pure Go, I would still strongly recommend Google Cloud Run.
Here is exactly why, and it has nothing to do with the language anymore, but rather how a Discord bot fundamentally works.
The Deciding Factor: The Persistent Connection
A Discord bot is not a typical web server. A web server sits and waits for someone to send it a request (like loading a webpage).
A Discord bot needs to actively open a long-lived connection (a WebSocket) to Discord's servers and keep it open 24/7. This is how it "hears" chat messages and commands instantly.

Why App Engine fails at this:
Google App Engine (Standard Environment) is optimized specifically for short-lived HTTP requests. It expects a request to come in, the server to do some work quickly, send a response, and then go back to sleep.
If an application tries to keep a connection open for a long time (like a bot waiting for a command), App Engine will assume something is wrong and eventually kill the process to free up resources. This will constantly disconnect your bot, making it unreliable.

Why Cloud Run succeeds at this:
Cloud Run is designed to run general-purpose containers. While it is also primarily built for request/response workloads, it has robust support for WebSockets and long-lived connections.
As long as your container is active, it can maintain that crucial lifeline to Discord without getting shut down prematurely by the platform controller.
Summary

Even with a pure Go stack:
 * App Engine is great for: The core-api and web-server (standard web apps).
 * App Engine is bad for: The discord-bot (long-running connection worker).
Because you need to run the bot somewhere, and it's best to keep your architecture uniform, Cloud Run remains the superior choice for hosting the entire microservices ecosystem.
