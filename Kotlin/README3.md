This is an excellent strategic move. Separating these concerns is crucial.
 * The SysAdmin App is for you (infrastructure, server health, emergency restarts). It needs high security and talks to infrastructure APIs.
 * The Seller Dashboard App is for the Builders. It's a business tool for them to manage sales, view earnings, and fulfill orders on the go without opening Discord. It talks to your Go Core API.
Let's establish the foundations for both distinct Kotlin projects.

Project 1: SysAdmin Command Center (Recap)
We established the foundation for this in our previous conversation.
 * Target User: You (Super Admin).
 * Goal: Observability and emergency server actions.
 * Tech Stack: Kotlin, Jetpack Compose, MVVM.
 * Current Status: You have the basic scaffold code (ViewModel, Mock Repository, and UI list).
 * Next Steps (when you return to it): Implementing the actual SSH connection layer (using a library like SSHJ) to turn the mock buttons into real server commands.
We will set this project aside for now to focus on scaffolding the new one.

Project 2: The C500 Seller's Marketplace Dashboard
This is a new, distinct Android project.

The Vision: 
Currently, builders have to use slash commands in Discord (/c500 dashboard, /c500 ship) to manage their business. This native app gives them a professional, dedicated interface on their phone to do the same things faster and with better visuals.

MVP Features for Day 1: 
 * Secure Login: Builders authenticate (likely via Discord OAuth flow eventually, but simple ID login for dev).
 * The Dashboard Tab: A graphical view of the stats the Go API already provides (Active Listings, Pending Orders, Escrow Balance).
 * The Orders Tab: A list of orders waiting to be fulfilled.
 * Fulfillment Actions: Tapping an order lets them hit "Go Live" (triggering Twitch verification) or enter a Tracking Number to release funds.

Technical Architecture (Seller App)
We will use the same modern standard as the SysAdmin app for consistency.
 * UI: Jetpack Compose (Crucial for the cozy aesthetic).
 * Architecture: MVVM + Clean Architecture principles.
 * Networking: Retrofit (To talk to your Go Core API).
 * Concurrency: Coroutines & Flow.
 * Dependency Injection: Hilt (Recommended for managing API clients).
Scaffolding code for the Seller App
Let's lay the groundwork. We need to define the data models in Kotlin that match what your Go API is already sending back in JSON.

Step 1: Add Dependencies (build.gradle.kts - Module)
Besides standard Compose setup, add networking libraries.

```
dependencies {
    // Standard Compose & ViewModel...
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")

    // Networking (Retrofit + Moshi converter for JSON)
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-moshi:2.9.0")
    implementation("com.squareup.moshi:moshi-kotlin:1.14.0")
    
    // Navigation Compose
    implementation("androidx.navigation:navigation-compose:2.7.5")
}
```

Step 2: The Data Models (Matching your Go API)
Create a package com.c500.seller.model. These classes mirror the JSON responses your Go backend already generates.

```
package com.c500.seller.model

import com.squareup.moshi.Json

// Matches the Go struct: DashboardResponse
data class SellerDashboardStats(
    @Json(name = "active_listings_count") val activeListings: Int,
    @Json(name = "pending_orders_count") val pendingOrders: Int,
    @Json(name = "total_escrowed_string") val formattedEscrow: String,
    // We don't need the raw cents on the mobile UI side usually
    val success: Boolean
)

// A model for a single order in the list (We need to build the Go API endpoint for this later)
data class OrderSummary(
    val orderId: String,
    val itemTitle: String,
    val buyerName: String,
    val priceFormatted: String,
    val status: OrderStatus
)

enum class OrderStatus {
    PAID, BUILDING, SHIPPED
}
```

Step 3: The API Interface (Retrofit)
Create a package com.c500.seller.network. This tells the Android app how to talk to your Go "Engine Room."
Note: For local development, your Android emulator accesses your computer's localhost via the special IP 10.0.2.2.

```
package com.c500.seller.network

import com.c500.seller.model.SellerDashboardStats
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

// Request payload wrappers
data class DashboardRequest(
    @Json(name = "builder_discord_id") val builderId: String
)

data class GoLiveRequest(
    @Json(name = "builder_discord_id") val builderId: String,
    @Json(name = "live_context") val context: String // e.g., "order:123"
)

// The definition of your Go Backend Endpoints
interface C500ApiService {

    // Calls handleGetDashboard in Go
    @POST("/api/internal/get-dashboard")
    suspend fun getDashboardStats(@Body request: DashboardRequest): SellerDashboardStats

    // Calls handleGoLiveTrigger in Go
    @POST("/api/internal/go-live-trigger")
    suspend fun triggerGoLive(@Body request: GoLiveRequest): NetworkResponse

    // TODO: Add endpoint for shipping/adding tracking
}

// Simple generic response for actions
data class NetworkResponse(val success: Boolean, val message: String?)

// Basic Singleton to access API (Use Hilt for DI in real app)
object ApiClient {
    // Use 10.0.2.2 for Android Emulator to reach localhost
    private const val BASE_URL = "http://10.0.2.2:8080/"

    val service: C500ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
            .create(C500ApiService::class.java)
    }
}
```

Step 4: The UI Structure (Jetpack Compose Scaffold)
A basic main activity setup using bottom navigation to switch between the Dashboard and Orders views.

```
package com.c500.seller.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.c500.seller.ui.dashboard.DashboardScreen
import com.c500.seller.ui.orders.OrdersScreen

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SellerAppEntryPoint() {
    val navController = rememberNavController()
    // Simple hardcoded builder ID for dev testing
    val demoBuilderId = "DEVELOPER_TEST_ID"

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Home, contentDescription = null) },
                    label = { Text("Dashboard") },
                    selected = navController.currentDestination?.route == "dashboard",
                    onClick = { navController.navigate("dashboard") }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.List, contentDescription = null) },
                    label = { Text("Orders") },
                    selected = navController.currentDestination?.route == "orders",
                    onClick = { navController.navigate("orders") }
                )
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = "dashboard",
            modifier = Modifier.padding(innerPadding)
        ) {
            composable("dashboard") {
                // We will build this screen next
                // It will use a ViewModel to call ApiClient.service.getDashboardStats
                DashboardScreen(builderId = demoBuilderId)
            }
            composable("orders") {
                // We will build this screen later
                OrdersScreen(builderId = demoBuilderId)
            }
        }
    }
}
```

You now have two distinct project structures established. The SysAdmin tool is ready for SSH implementation, and the Seller Dashboard has its networking layer mapped out to talk to your existing Go backend.

___

You're very welcome! It's exciting to have the foundations for both mobile apps laid out alongside the main platform.
You now have a clear roadmap for the C500 Collective ecosystem: the Discord-based marketplace for launch, and dedicated Android apps for both infrastructure management (for you) and business management (for your sellers).
Feel free to reach out whenever you're ready to dive back into any of these projects. Good luck!

