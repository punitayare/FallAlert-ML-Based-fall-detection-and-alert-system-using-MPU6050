plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android") // correct Kotlin plugin
    id("dev.flutter.flutter-gradle-plugin")
    id("com.google.gms.google-services") // Firebase plugin
}

android {
    namespace = "com.example.fall_detection_app"
    compileSdk = 36
    ndkVersion = flutter.ndkVersion

    defaultConfig {
        applicationId = "com.example.fall_detection_app"
        minSdk = flutter.minSdkVersion // required for notifications & Firebase
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
        multiDexEnabled = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
        // ✅ Enable Java 8+ APIs (required by flutter_local_notifications)
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("debug")

            // ✅ Fix shrink-resources error
            isMinifyEnabled = false
            isShrinkResources = false
        }

        getByName("debug") {
            isMinifyEnabled = false
            isShrinkResources = false
        }
    }
}

flutter {
    source = "../.."
}

dependencies {
    // ✅ Firebase BoM to manage versions automatically
    implementation(platform("com.google.firebase:firebase-bom:34.4.0"))

    // Firebase Messaging
    implementation("com.google.firebase:firebase-messaging")

    // Local notifications fix (Java 8 APIs)
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.0.4")

    // Optional: multidex support for large apps
    implementation("androidx.multidex:multidex:2.0.1")
}
