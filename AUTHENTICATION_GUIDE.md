# Authentication Guide

## Overview

The Text-Mining Research Tool now includes Google Sign-in authentication powered by Firebase. This ensures secure access and enables user-specific features like personalized API keys and cloud storage integration.

---

## 🚀 Quick Start

### For Users (First Time)

1. **Open the application:**
   ```bash
   streamlit run ui/main.py
   ```

2. **If Firebase is not configured**, you'll see a setup warning:
   - Follow the on-screen instructions
   - Or ask your administrator to complete Firebase setup

3. **Sign in with Google:**
   - Click "Sign in with Google" button
   - Authorize the application
   - You're in!

### For Administrators (Setup Required)

Before users can sign in, you need to configure Firebase:

1. **Complete Firebase Setup:**
   - Follow instructions in `SETUP_FIREBASE.md`
   - Create Firebase project
   - Enable Google Authentication
   - Download service account credentials
   - Place `firebase_config.json` in `config/` directory

2. **Test Firebase Connection:**
   ```bash
   python test_firebase_connection.py
   ```

3. **Start the application:**
   ```bash
   streamlit run ui/main.py
   ```

---

## 📋 Architecture

### Authentication Flow

```
User Opens App
     ↓
Firebase Initialized?
     ↓ No → Show Setup Warning
     ↓ Yes
User Authenticated?
     ↓ No → Show Login Page
     ↓ Yes
Main App (with logout button)
```

### File Structure

```
app/auth/
├── firebase_manager.py      # Firebase Admin SDK integration
├── session_manager.py        # Streamlit session state management
└── streamlit_auth.py         # Authentication UI components

ui/
├── main.py                   # Entry point with auth guard
└── main_app.py              # Main application logic

config/
└── firebase_config.json      # Firebase credentials (not in git)
```

---

## 🔐 Features

### Current Features (Session 2 - Completed)

✅ **Google Sign-in Authentication**
- Secure OAuth2 flow with Firebase
- User profile management in Firestore
- Session persistence across page reloads

✅ **Session Management**
- Secure session state handling
- Automatic token verification
- Logout functionality

✅ **User Profile**
- Display user name and email
- User-specific data storage in Firestore
- Profile picture support

✅ **Protected Routes**
- Authentication guard for main app
- Automatic redirect to login if not authenticated

### Upcoming Features

🔜 **User-Specific API Keys** (Session 3)
- Secure GEMINI_API_KEY storage per user
- Encrypted in Firestore
- UI for API key management

🔜 **Cloud Storage Integration** (Session 4)
- Google Drive file access
- OneDrive file access
- User-specific folder permissions

🔜 **Theme Switcher** (Session 5)
- Light/Dark/System themes
- Per-user preference storage

🔜 **Multi-language Support** (Session 6)
- English and Vietnamese
- Per-user language preference

---

## 🔧 Configuration

### Firebase Configuration File

Location: `config/firebase_config.json`

**Required structure:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### Environment Variables (Optional)

Create `config/.env`:
```env
FIREBASE_CREDENTIALS_PATH=config/firebase_config.json
DEBUG=False
```

---

## 🧪 Testing

### Test Firebase Connection

```bash
python test_firebase_connection.py
```

**Expected output:**
```
==============================================================
Firebase Connection Test
==============================================================

1. Initializing Firebase Admin SDK...
   ✅ Firebase initialized successfully!

2. Testing Firestore connection...
   ✅ Firestore client created successfully!

3. Testing Firestore write operation...
   ✅ Successfully wrote test document to Firestore!

4. Testing Firestore read operation...
   ✅ Successfully read test document!

5. Cleaning up test document...
   ✅ Test document deleted successfully!

6. Testing user profile operations...
   ✅ User profile created successfully!
   ✅ User profile retrieved: test@example.com
   ✅ Test user profile deleted!

==============================================================
🎉 All tests passed successfully!
==============================================================
```

### Manual Testing

1. **Test Login Flow:**
   - Start app
   - Should see login page
   - Click sign-in (will need Firebase Web SDK configured)

2. **Test Session Persistence:**
   - Sign in
   - Refresh page
   - Should remain signed in

3. **Test Logout:**
   - Click "Sign Out" button in sidebar
   - Should return to login page

---

## ❓ Troubleshooting

### Error: "Firebase not configured"

**Solution:**
- Ensure `config/firebase_config.json` exists
- Verify file contains valid Firebase credentials
- Run `python test_firebase_connection.py` to diagnose

### Error: "Invalid or expired token"

**Solution:**
- Token may have expired (tokens expire after 1 hour)
- Sign out and sign in again
- Check system clock (incorrect time causes token validation to fail)

### Error: "Permission denied" when accessing Firestore

**Solution:**
- Check Firestore security rules in Firebase Console
- Ensure rules allow authenticated users to read/write their own data
- See `SETUP_FIREBASE.md` for correct security rules

### Login button doesn't work

**Solution:**
- Firebase Web SDK configuration needed
- Current implementation requires manual token input for testing
- Production deployment needs Firebase Web SDK config
- See "Firebase Web Configuration" section below

---

## 🌐 Firebase Web Configuration (For Production)

To enable full Google Sign-in flow:

1. **Get Firebase Web Config:**
   - Go to Firebase Console → Project Settings
   - Scroll to "Your apps" → Web app
   - Copy the `firebaseConfig` object

2. **Add to application:**
   - Store config securely (environment variable or encrypted file)
   - Update `StreamlitAuth._get_firebase_web_config()` method
   - Redeploy application

**Example config:**
```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef"
};
```

---

## 📚 API Reference

### FirebaseManager

```python
from app.auth.firebase_manager import firebase_manager

# Initialize
firebase_manager.initialize_app()

# Verify token
user_info = firebase_manager.verify_id_token(id_token)

# Create user profile
firebase_manager.create_user_profile(uid, email, display_name)

# Get user profile
profile = firebase_manager.get_user_profile(uid)
```

### SessionManager

```python
from app.auth.session_manager import SessionManager

# Initialize session
SessionManager.initialize_session()

# Set user
SessionManager.set_user(user_data, id_token)

# Check authentication
if SessionManager.is_authenticated():
    user = SessionManager.get_current_user()

# Logout
SessionManager.logout()
```

### StreamlitAuth

```python
from app.auth.streamlit_auth import StreamlitAuth

auth = StreamlitAuth(firebase_manager)

# Render login page
auth.render_login_page()

# Check authentication
if auth.is_authenticated():
    # User is signed in
    pass

# Logout
auth.logout()
```

---

## 🔒 Security Best Practices

1. ✅ **Never commit `firebase_config.json`** to version control
2. ✅ **Use environment variables** in production
3. ✅ **Implement proper Firestore security rules**
4. ✅ **Rotate service account keys** regularly
5. ✅ **Use HTTPS** in production
6. ✅ **Enable Firebase App Check** for production
7. ✅ **Monitor authentication logs** in Firebase Console

---

## 📖 Related Documentation

- [SETUP_FIREBASE.md](SETUP_FIREBASE.md) - Firebase setup guide
- [SETUP_GOOGLE_CLOUD.md](SETUP_GOOGLE_CLOUD.md) - Google Drive setup
- [SETUP_AZURE.md](SETUP_AZURE.md) - OneDrive setup
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Full development roadmap

---

## 🆘 Support

### Common Questions

**Q: Can I use the app without authentication?**
A: Authentication is required. For local testing without auth, you can modify the code to bypass authentication, but this disables user-specific features.

**Q: Which Google accounts can sign in?**
A: Any Google account authorized in Firebase Console. For testing, add specific accounts as test users in Firebase Authentication settings.

**Q: How long do sessions last?**
A: Firebase ID tokens expire after 1 hour. The app should handle token refresh automatically (to be implemented in future updates).

**Q: Is my data secure?**
A: Yes. Data is stored in Firestore with security rules that ensure users can only access their own data. Firebase provides enterprise-grade security.

### Getting Help

- Check [Firebase Documentation](https://firebase.google.com/docs)
- Review `SETUP_FIREBASE.md` for setup issues
- Run `python test_firebase_connection.py` to diagnose
- Check application logs in `data/app.log`

---

**Last Updated:** 2025-12-04
**Version:** Session 2 Complete
**Status:** ✅ Authentication Implemented
