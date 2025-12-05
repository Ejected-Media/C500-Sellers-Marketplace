Based on the architecture we've designed, for this project on Google Cloud Console, we are using Google Cloud Run.
Here is a breakdown of why we chose it and the exact difference between the two services.

We are using Google Cloud Run

As outlined in the deployment strategy, we will be deploying three separate services within a single Google Cloud Project:
 * c500-bot-python (The Discord Bot)
 * c500-core-go (The Backend API)
 * c500-web-go (The Public Website)

All three will be deployed as individual services on Cloud Run.
The Difference: Cloud Run vs. App Engine
At a high level, both are "serverless" platforms that let you run code without managing servers. The key difference is in what you deploy and the flexibility you have.

| Feature | Google Cloud Run (Our Choice) | Google App Engine (Standard Environment) |
|---|---|---|
| What you deploy | A Docker Container. You package your code, its dependencies, and the exact runtime environment into a portable image. | Your Source Code. You upload your Python or Go files directly to Google. |
| Language Support | Any language, any library. If you can put it in a container, it will run. This is perfect for our mix of Python and Go. | Specific languages & versions only. You must use supported versions (e.g., Go 1.19, Python 3.10). Less flexibility with system libraries. |
| Execution Model | Serverless Containers. It spins up container instances on demand to handle requests. | Platform as a Service (PaaS). It provides a managed runtime for your code. |
| Scaling | Scales to zero. If no one is using your app, it spins down completely, and you pay nothing. Scales up instantly with traffic. | Scales to zero (Standard). Can also scale to zero, but has different cold-start characteristics. App Engine Flexible does not scale to zero. |
| Best Use Case | Microservices, REST APIs, and any application that can be containerized. Gives you full control over the environment. | Simple web applications and monoliths where you want to focus only on code and let Google handle the runtime. |

In Summary:
 * Think of App Engine as a curated garden. It's easy to plant things if you follow the rules, but you can't easily bring in exotic plants.
 * Think of Cloud Run as a shipping port. You provide a standard shipping container (Docker image), and Google doesn't care what's inside; it just manages loading, unloading, and moving it around efficiently.
We chose Cloud Run because it gives us the flexibility to run two different languages (Python and Go) side-by-side in their own custom environments, all while enjoying the benefits of a serverless, scale-to-zero platform.
