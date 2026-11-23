plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.example.promofinder"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.example.promofinder"
        minSdk = 24
        targetSdk = 37
        versionCode = 1
        versionName = "1.1"

        // Default points to the host machine when running the Android Emulator.
        // Override with -PPROMOFINDER_API_URL=https://your-domain/ for deployed environments.
        val configuredApiUrl = (project.findProperty("PROMOFINDER_API_URL") as String?)
            ?: "http://127.0.0.1:8000/"
        val apiUrl = if (configuredApiUrl.endsWith("/")) configuredApiUrl else "$configuredApiUrl/"
        buildConfigField("String", "BACKEND_BASE_URL", "\"$apiUrl\"")
        manifestPlaceholders["usesCleartextTraffic"] = "true"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            manifestPlaceholders["usesCleartextTraffic"] = "false"
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        viewBinding = true
        buildConfig = true
    }
}

dependencies {
    implementation(libs.activity.ktx)
    implementation(libs.appcompat)
    implementation(libs.constraintlayout)
    implementation(libs.material)
    implementation(libs.retrofit)
    implementation(libs.converter.gson)
    implementation(libs.gson)
    implementation(libs.glide)
    testImplementation(libs.junit)
    androidTestImplementation(libs.espresso.core)
    androidTestImplementation(libs.ext.junit)
}