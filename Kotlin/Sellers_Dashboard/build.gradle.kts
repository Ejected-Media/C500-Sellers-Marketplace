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
