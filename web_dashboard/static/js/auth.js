/**
 * Authentication JavaScript
 * Handles login and registration with Firebase Auth
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    
    // Check which page we're on
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        initLoginPage();
    }
    
    if (registerForm) {
        initRegisterPage();
    }
    
    // Check if user is already logged in
    checkAuthState();
});

/**
 * Check authentication state
 */
function checkAuthState() {
    firebase.auth().onAuthStateChanged((user) => {
        if (user) {
            // User is signed in
            console.log('User logged in:', user.email);
            
            // Redirect to dashboard if on login/register page
            const currentPage = window.location.pathname;
            if (currentPage === '/login' || currentPage === '/register') {
                window.location.href = '/';
            }
        } else {
            // User is signed out
            console.log('User not logged in');
        }
    });
}

/**
 * Initialize Login Page
 */
function initLoginPage() {
    const form = document.getElementById('loginForm');
    const btn = document.getElementById('loginBtn');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember').checked;
        
        // Validate inputs
        if (!email || !password) {
            showError('Please fill in all fields');
            return;
        }
        
        // Set loading state
        setLoading(btn, true);
        hideAlerts();
        
        try {
            // Set persistence based on remember me
            const persistence = remember 
                ? firebase.auth.Auth.Persistence.LOCAL 
                : firebase.auth.Auth.Persistence.SESSION;
            
            await firebase.auth().setPersistence(persistence);
            
            // Sign in with email and password
            const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);
            const user = userCredential.user;
            
            console.log('Login successful:', user.email);
            
            // Show success message
            showSuccess('Login successful! Redirecting...');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
            
        } catch (error) {
            console.error('Login error:', error);
            handleAuthError(error);
        } finally {
            setLoading(btn, false);
        }
    });
}

/**
 * Initialize Register Page
 */
function initRegisterPage() {
    const form = document.getElementById('registerForm');
    const btn = document.getElementById('registerBtn');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const terms = document.getElementById('terms').checked;
        
        // Validate inputs
        if (!name || !email || !password || !confirmPassword) {
            showError('Please fill in all fields');
            return;
        }
        
        if (!terms) {
            showError('Please accept the terms of service');
            return;
        }
        
        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }
        
        if (password.length < 6) {
            showError('Password must be at least 6 characters');
            return;
        }
        
        // Set loading state
        setLoading(btn, true);
        hideAlerts();
        
        try {
            // Create user with email and password
            const userCredential = await firebase.auth().createUserWithEmailAndPassword(email, password);
            const user = userCredential.user;
            
            // Update user profile with name
            await user.updateProfile({
                displayName: name
            });
            
            console.log('Registration successful:', user.email);
            
            // Create user document in Firestore via API
            await createUserInDatabase(user.uid, email, name);
            
            // Show success message
            showSuccess('Account created successfully! Redirecting...');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
            
        } catch (error) {
            console.error('Registration error:', error);
            handleAuthError(error);
        } finally {
            setLoading(btn, false);
        }
    });
}

/**
 * Create user in database via API
 */
async function createUserInDatabase(userId, email, name) {
    try {
        const response = await fetch('/api/users/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: userId,
                email: email,
                name: name
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('User created in database');
        } else {
            console.error('Failed to create user in database:', data.error);
        }
    } catch (error) {
        console.error('Error creating user in database:', error);
        // Don't throw error - authentication already succeeded
    }
}

/**
 * Handle Firebase Authentication Errors
 */
function handleAuthError(error) {
    let message = 'An error occurred. Please try again.';
    
    switch (error.code) {
        case 'auth/email-already-in-use':
            message = 'This email is already registered. Please login instead.';
            break;
        case 'auth/invalid-email':
            message = 'Invalid email address.';
            break;
        case 'auth/operation-not-allowed':
            message = 'Email/password authentication is not enabled.';
            break;
        case 'auth/weak-password':
            message = 'Password is too weak. Use at least 6 characters.';
            break;
        case 'auth/user-disabled':
            message = 'This account has been disabled.';
            break;
        case 'auth/user-not-found':
            message = 'No account found with this email.';
            break;
        case 'auth/wrong-password':
            message = 'Incorrect password.';
            break;
        case 'auth/too-many-requests':
            message = 'Too many failed attempts. Please try again later.';
            break;
        case 'auth/network-request-failed':
            message = 'Network error. Please check your connection.';
            break;
        default:
            message = error.message || message;
    }
    
    showError(message);
}

/**
 * Show error alert
 */
function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorAlert && errorMessage) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'flex';
        
        // Hide after 5 seconds
        setTimeout(() => {
            errorAlert.style.display = 'none';
        }, 5000);
    }
}

/**
 * Show success alert
 */
function showSuccess(message) {
    const successAlert = document.getElementById('successAlert');
    const successMessage = document.getElementById('successMessage');
    
    if (successAlert && successMessage) {
        successMessage.textContent = message;
        successAlert.style.display = 'flex';
    }
}

/**
 * Hide all alerts
 */
function hideAlerts() {
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');
    
    if (errorAlert) errorAlert.style.display = 'none';
    if (successAlert) successAlert.style.display = 'none';
}

/**
 * Set button loading state
 */
function setLoading(button, loading) {
    if (loading) {
        button.classList.add('loading');
        button.disabled = true;
    } else {
        button.classList.remove('loading');
        button.disabled = false;
    }
}

/**
 * Sign out user
 */
async function signOut() {
    try {
        await firebase.auth().signOut();
        console.log('User signed out');
        window.location.href = '/login';
    } catch (error) {
        console.error('Sign out error:', error);
        showError('Failed to sign out. Please try again.');
    }
}

/**
 * Get current user
 */
function getCurrentUser() {
    return firebase.auth().currentUser;
}

/**
 * Get user token for API requests
 */
async function getUserToken() {
    const user = getCurrentUser();
    if (user) {
        return await user.getIdToken();
    }
    return null;
}

/**
 * Check if user is authenticated and return user
 * Used by other pages to verify auth
 */
async function checkUserAuth() {
    return new Promise((resolve) => {
        firebase.auth().onAuthStateChanged((user) => {
            resolve(user);
        });
    });
}

// Export functions for use in other scripts
window.fallDetection = {
    signOut,
    getCurrentUser,
    getUserToken,
    checkAuthState: checkUserAuth,
    // Also export the original checkAuthState for compatibility
    checkAuth: checkUserAuth
};

console.log('✓ Fall Detection auth module loaded');
