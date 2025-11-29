This is the landing page for C500.store.
Since the actual commerce happens on Discord, this website's primary job is brand establishment and redirection. It needs to immediately communicate the "cozy pastel" aesthetic, explain that this is a unique Discord-based marketplace, and direct users to join the server.
Developer Instructions
 * Save this file as index.html.
 * Place it inside the templates/ folder you created in your Go project directory.
 * Crucial Step: This HTML relies on a corresponding CSS file for the pastel visuals. I have included the HTML structure below. Your developer (or designer) will need to create the static/css/style.css file to apply the specific hex codes (#FFD1DC, #AEEEEE, etc.) and fonts (like Recoleta and Quicksand) we defined earlier.
The templates/index.html File

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="C500 Collective: The coziest, safest marketplace for high-end custom mechanical keyboards, living on Discord and Twitch.">
    <title>{{ .title }}</title> <link rel="stylesheet" href="/static/css/style.css">
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&display=swap" rel="stylesheet">

    <link rel="icon" type="image/png" href="/static/images/favicon.png">
</head>
<body>

    <header class="cozy-header">
        <div class="container header-content">
            <div class="logo-container">
                <img src="/static/images/c500-cloud-logo.png" alt="C500 Logo" class="nav-logo">
                <span class="brand-name">C500 Collective</span>
            </div>
            <nav class="nav-links">
                <a href="#how-it-works">How it Works</a>
                <a href="#safety">Trust & Safety</a>
                <a href="YOUR_DISCORD_INVITE_LINK_HERE" class="btn btn--pastel-pink cta-button">
                    <i class="fa-brands fa-discord"></i> Join the Discord
                </a>
            </nav>
        </div>
    </header>


    <main>
        <section class="hero-section">
            <div class="container hero-content">
                <div class="hero-text">
                    <h1 class="cozy-title">Your cozy home for high-end custom keyboards.</h1>
                    <p class="hero-subtitle">
                        We are a creator-owned collective living on Discord and Twitch. 
                        Discover unique builds, buy securely, and watch it being created live.
                    </p>
                    <div class="hero-buttons">
                        <a href="YOUR_DISCORD_INVITE_LINK_HERE" class="btn btn--pastel-pink btn--large">
                            ☁️ Enter the Collective
                        </a>
                        <a href="#how-it-works" class="btn btn--pastel-blue btn--outline">
                            Learn More
                        </a>
                    </div>
                </div>
                <div class="hero-image-container">
                    <img src="/static/images/hero-desk-illustration.png" alt="Cozy Desk Setup" class="hero-img float-animation">
                </div>
            </div>
        </section>


        <section id="how-it-works" class="section-padding">
            <div class="container">
                <h2 class="section-title center-text">How the Magic Happens ✨</h2>
                <p class="section-subtitle center-text">We aren't a standard website. The C500 Bot connects top-tier builders directly to you.</p>
                
                <div class="steps-grid">
                    <div class="pastel-card card--yellow">
                        <div class="card-icon">🔍</div>
                        <h3>1. Find Your Grail</h3>
                        <p>Join our builders' private Discord servers. Browse exclusive "Drops" posted directly in their shop channels.</p>
                    </div>

                    <div class="pastel-card card--blue">
                        <div class="card-icon">🔒</div>
                        <h3>2. Secure Checkout</h3>
                        <p>Click "Buy" in Discord. You pay C500 directly. We hold your funds safely in our Escrow Vault.</p>
                    </div>

                    <div class="pastel-card card--green">
                        <div class="card-icon">📹</div>
                        <h3>3. Verified Vibes</h3>
                        <p>The builder streams the assembly on Twitch or provides tracking. Only then do we release the funds.</p>
                    </div>
                </div>
            </div>
        </section>


        <section id="safety" class="trust-banner section-padding">
            <div class="container trust-content">
                <div class="trust-text">
                    <h2>No Scams. Just Thock. 🛡️</h2>
                    <p>
                        The keyboard hobby can be risky. We fixed it. Our tiered reputation system and 
                        financial escrow mean you never have to worry about flaky sellers again.
                        If a verified builder doesn't deliver, you get a full refund. Simple as that.
                    </p>
                </div>
                <div class="trust-badges">
                    <div class="badge-item"><i class="fa-solid fa-shield-heart"></i> Escrow Protection</div>
                    <div class="badge-item"><i class="fa-brands fa-twitch"></i> Live Verification</div>
                    <div class="badge-item"><i class="fa-solid fa-star"></i> Reputation System</div>
                </div>
            </div>
        </section>

    </main>

    <footer class="cozy-footer">
        <div class="container footer-content">
            <div class="footer-brand">
                <span class="brand-name">C500 Collective</span>
                <p>Stay Cozy.</p>
            </div>
            <div class="footer-links">
                <a href="#">Terms of Service (The Promise)</a>
                <a href="#">Privacy Policy</a>
                <a href="https://twitter.com/YOUR_ACCOUNT" target="_blank"><i class="fa-brands fa-twitter"></i></a>
            </div>
        </div>
        <div class="copyright">
            © 2025 C500 Collective. Not affiliated with Discord or Twitch.
        </div>
    </footer>

</body>
</html>
```
