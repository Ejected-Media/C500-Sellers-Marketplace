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
