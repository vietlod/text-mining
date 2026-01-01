# Firebase Setup Guide

This guide will walk you through setting up Firebase Authentication and Cloud Firestore for the Text-Mining application.

## Prerequisites

- Google account
- Project with internet connection

## Estimated Time: 15-20 minutes

---

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or **"Create a project"**
3. Enter project name (e.g., `text-mining-tool`)
4. (Optional) Enable Google Analytics (recommended for production)
5. Click **"Create project"** and wait for setup to complete
6. Click **"Continue"** when done

---

## Step 2: Enable Firebase Authentication

1. In Firebase Console (**Build**), click **"Authentication"** from left sidebar
2. Click **"Get started"**
3. Go to **"Sign-in method"** tab
4. Enable **"Google"** provider:
   - Click on **"Google"**
   - Toggle **"Enable"** switch
   - Enter **Project support email** (your email)
   - Click **"Save"**

5. (Optional) Configure authorized domains:
   - Scroll down to **"Authorized domains"**
   - Add your domain if deploying to production
   - `localhost` is already authorized by default for development

---

## Step 3: Create Cloud Firestore Database

1. In Firebase Console (**Build**), click **"Firestore Database"** from left sidebar
2. Click **"Create database"**
3. Select **"Start in production mode"** (we'll configure rules next)
4. Choose your Firestore location (e.g., `us-central1` or closest to your users)
   - ⚠️ **Cannot be changed later**
5. Click **"Enable"**

---

## Step 4: Configure Firestore Security Rules

1. In Firestore Database, go to **"Rules"** tab
2. Replace the default rules with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // User profiles - users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // User settings - users can only access their own settings
    match /settings/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // API keys - users can only access their own keys
    match /api_keys/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Cloud storage credentials - users can only access their own credentials
    match /cloud_credentials/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

3. Click **"Publish"**

---

## Step 5: Get Firebase Admin SDK Credentials

1. In Project Overview, click **⚙️ Settings** icon → **"Project settings"**
2. Go to **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Confirm by clicking **"Generate key"**
5. A JSON file will be downloaded (e.g., `text-mining-tool-firebase-adminsdk-xxxxx.json`)

6. **IMPORTANT:** Rename this file to `firebase_config.json`
7. Move it to `D:\TEXT-MINING\config\firebase_config.json`

⚠️ **Security Warning:**
- **NEVER** commit this file to version control
- **NEVER** share this file publicly
- It contains sensitive credentials with admin access to your Firebase project

---

## Step 6: Get Firebase Web API Configuration

1. In Project Overview → **Project settings** → **"General"** tab
2. Scroll down to **"Your apps"** section
3. Click **Web icon** (</>) to add a web app
4. Enter app nickname (e.g., `Text-Mining Web App`)
5. ✅ Check **"Also set up Firebase Hosting"** (optional)
6. Click **"Register app"**

7. Copy the **Firebase configuration object**:

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

8. **Save Firebase Web Config:**

   **Option A: Use Helper Script (Recommended) 🚀**
   
   ```bash
   python setup_firebase_web_config.py
   ```
   
   This interactive script will:
   - Read your `firebase_config.json` automatically
   - Guide you to get the API Key from Firebase Console
   - Auto-generate `firebase_web_config.json` file
   - Validate the config before saving
   
   **Option B: Manual Setup**
   
   - Create a new file: `config/firebase_web_config.json`
   - Copy the config object and convert to JSON format (remove `const firebaseConfig =` and semicolon)
   - Save the file at `D:\TEXT-MINING\config\firebase_web_config.json`

   **Example file content:**
   ```json
   {
     "apiKey": "AIza...",
     "authDomain": "your-project.firebaseapp.com",
     "projectId": "your-project-id",
     "storageBucket": "your-project.appspot.com",
     "messagingSenderId": "123456789",
     "appId": "1:123456789:web:abcdef"
   }
   ```

   ⚠️ **Note:** Without this file, the app will show a warning and use alternative sign-in method. This config is required for Google Sign-in button to work properly.

   **Option C: Environment Variable (Alternative)**
   
   You can also set `FIREBASE_WEB_API_KEY` environment variable with just the `apiKey` value, and the app will auto-construct the config from your `firebase_config.json`.

---

## Step 7: Initialize Firestore Collections

Firebase will automatically create collections when first document is written, but you can create them manually:

1. In **Firestore Database**, click **"Start collection"**
2. Create these collections (one at a time):
   - Collection ID: `users` → Add first document with ID: `_placeholder` (can delete later)
   - Collection ID: `settings`
   - Collection ID: `api_keys`
   - Collection ID: `cloud_credentials`

---

## Step 8: Configure Firebase Billing (Required for Production)

⚠️ **Note:** Firebase Spark (free) plan has limitations:
- 50,000 document reads/day
- 20,000 document writes/day
- 1 GB storage

For production use, upgrade to **Blaze (pay-as-you-go)** plan:

1. Go to Firebase Console → **⚙️ Settings** → **"Usage and billing"**
2. Click **"Modify plan"**
3. Select **"Blaze plan"**
4. Set up payment method
5. (Optional) Set budget alerts

Pricing: https://firebase.google.com/pricing

---

## Step 9: Verify Setup

Run this test script to verify Firebase connection:

```python
# test_firebase_connection.py
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase
cred = credentials.Certificate('config/firebase_config.json')
firebase_admin.initialize_app(cred)

# Test Firestore connection
db = firestore.client()
print("✅ Firestore connected successfully")

# Test creating a test document
test_ref = db.collection('users').document('test')
test_ref.set({'test': 'connection', 'timestamp': firestore.SERVER_TIMESTAMP})
print("✅ Firestore write successful")

# Test reading
doc = test_ref.get()
if doc.exists:
    print(f"✅ Firestore read successful: {doc.to_dict()}")

# Clean up
test_ref.delete()
print("✅ Test document deleted")

print("\n🎉 Firebase setup verified successfully!")
```

Run with:
```bash
python test_firebase_connection.py
```

---

## Troubleshooting

### Error: "Permission denied" when accessing Firestore

**Solution:** Check Firestore security rules and ensure user is authenticated

### Error: "Project not found"

**Solution:** Verify `firebase_config.json` is in correct location and has valid credentials

### Error: "The caller does not have permission"

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **"IAM & Admin"** → **"Service Accounts"**
4. Find your service account and ensure it has **"Firebase Admin SDK Service Agent"** role

### Error: "Firebase App named '[DEFAULT]' already exists"

**Solution:** Firebase app is already initialized. Use `firebase_admin.get_app()` instead of `initialize_app()`

---

## Security Best Practices

1. ✅ Use Firebase Admin SDK only on backend/server
2. ✅ Never expose Admin SDK credentials in client-side code
3. ✅ Use Firestore security rules to protect data
4. ✅ Enable App Check for production (prevents abuse)
5. ✅ Rotate service account keys regularly
6. ✅ Set up budget alerts to avoid unexpected charges
7. ✅ Use Firebase Emulator Suite for local development

---

## Next Steps

After completing Firebase setup:

1. ✅ Verify `config/firebase_config.json` exists
2. → Continue to [Google Cloud Setup](SETUP_GOOGLE_CLOUD.md)
3. → Continue to [Azure Setup](SETUP_AZURE.md)
4. → Start implementing authentication (Session 2)

---

## Useful Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firebase Admin SDK Python](https://firebase.google.com/docs/admin/setup)
- [Cloud Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Firebase Pricing Calculator](https://firebase.google.com/pricing#blaze-calculator)

---

**Setup Date:** 2025-12-04
**Version:** 1.0
**Status:** ✅ Ready for implementation
