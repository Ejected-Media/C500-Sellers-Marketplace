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
