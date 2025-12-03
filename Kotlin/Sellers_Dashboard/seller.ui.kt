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
