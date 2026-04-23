/**
 * Firebase Configuration
 * 
 * IMPORTANT: Replace these values with your actual Firebase project credentials
 * Get these from: Firebase Console > Project Settings > General > Your apps
 */

// Firebase configuration object
const firebaseConfig = {
    apiKey: "AIzaSyBdC9wy-VAddc70lQKJD34LqkZIGfY_7_k",
    authDomain: "fall-simulated-3865c.firebaseapp.com",
    projectId: "fall-simulated-3865c",
    storageBucket: "fall-simulated-3865c.firebasestorage.app",
    messagingSenderId: "417982045231",
    appId: "1:417982045231:web:7f535a67e9075114ca3ada"
  };

// Initialize Firebase
try {
    firebase.initializeApp(firebaseConfig);
    console.log('✓ Firebase initialized successfully');
} catch (error) {
    console.error('✗ Firebase initialization failed:', error);
}

// Get Firebase Auth instance
const auth = firebase.auth();

// Enable persistence (keeps user logged in)
auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL)
    .then(() => {
        console.log('✓ Firebase auth persistence enabled');
    })
    .catch((error) => {
        console.error('✗ Auth persistence error:', error);
    });

/**
 * HOW TO GET YOUR FIREBASE CONFIG:
 * 
 * 1. Go to https://console.firebase.google.com/
 * 2. Select your project
 * 3. Click the gear icon (⚙️) > Project settings
 * 4. Scroll down to "Your apps" section
 * 5. Click on the Web app (</>) icon
 * 6. Copy the firebaseConfig object values
 * 7. Paste them above
 * 
 * Example:
 * apiKey: "AIzaSyC1234567890abcdefghijklmnop",
 * authDomain: "fall-detection-12345.firebaseapp.com",
 * projectId: "fall-detection-12345",
 * etc...
 */
