# Google Cloud Setup Guide

This guide will walk you through setting up Google Drive API for the Text-Mining application.

## Prerequisites

- Google account
- Firebase project already created (see [Firebase Setup](SETUP_FIREBASE.md))
- Project with internet connection

## Estimated Time: 15-20 minutes

---

## Step 1: Access Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. **Important:** Select the same project as your Firebase project
   - Click on project dropdown at the top
   - Select your Firebase project (e.g., `text-mining-tool`)

💡 **Tip:** Firebase automatically creates a Google Cloud project with the same name

---

## Step 2: Enable Google Drive API

1. In Google Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Drive API"**
3. Click on **"Google Drive API"**
4. Click **"Enable"**
5. Wait for API to be enabled (takes a few seconds)

---

## Step 3: Create OAuth 2.0 Credentials

### 3.1 Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type (unless you have Google Workspace)
3. Click **"Create"**

4. Fill in **App information**:
   - **App name:** `Text-Mining Research Tool`
   - **User support email:** Your email
   - **App logo:** (Optional) Upload logo if available
   - **Application home page:** (Optional) Your website URL
   - **Application privacy policy link:** (Optional)
   - **Application terms of service link:** (Optional)

5. **Developer contact information:**
   - Add your email address

6. Click **"Save and Continue"**

### 3.2 Add Scopes

1. Click **"Add or Remove Scopes"**
2. Search and select these scopes:
   - ✅ `.../auth/drive.readonly` - View files in Google Drive
   - ✅ `.../auth/drive.file` - View and manage files created by this app
   - ✅ `.../auth/userinfo.email` - See your email address
   - ✅ `.../auth/userinfo.profile` - See your personal info

3. Click **"Update"**
4. Click **"Save and Continue"**

### 3.3 Add Test Users (for development)

⚠️ **Important:** While in "Testing" mode, only test users can access the app

1. Click **"Add Users"**
2. Add email addresses of test users (including yourself)
3. Click **"Save and Continue"**
4. Review summary and click **"Back to Dashboard"**

💡 **Production Note:** To publish the app for all users:
- Go back to OAuth consent screen
- Click **"Publish App"**
- Submit for Google verification (required for production)

---

## Step 4: Create OAuth 2.0 Client ID

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**

3. **Application type:** Select **"Web application"**

4. **Name:** `Text-Mining OAuth Client`

5. **Authorized JavaScript origins:**
   - Click **"+ Add URI"**
   - Add: `http://localhost:8501` (for local development)
   - Add: Your production domain if deploying (e.g., `https://yourdomain.com`)

6. **Authorized redirect URIs:**
   - Click **"+ Add URI"**
   - Add: `http://localhost:8501` (for Streamlit)
   - Add: `http://localhost:8501/oauth2callback` (for OAuth callback)
   - Add production URIs if applicable

7. Click **"Create"**

8. **Download credentials:**
   - A popup will show your Client ID and Client Secret
   - Click **"Download JSON"**
   - Save as `google_oauth_credentials.json`

9. Move the file to `D:\TEXT-MINING\config\google_oauth_credentials.json`

---

## Step 5: Verify Credentials File Structure

Open `config/google_oauth_credentials.json` and verify it has this structure:

```json
{
  "web": {
    "client_id": "123456789-abcdefghijk.apps.googleusercontent.com",
    "project_id": "text-mining-tool",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-abc123def456",
    "redirect_uris": ["http://localhost:8501/oauth2callback"],
    "javascript_origins": ["http://localhost:8501"]
  }
}
```

⚠️ **Security Warning:**
- **NEVER** commit this file to version control
- **NEVER** share your Client Secret publicly
- Client Secret allows access to Google APIs on behalf of users

---

## Step 6: Enable Additional Google APIs (Optional but Recommended)

### Google People API (for user profile information)

1. Go to **"APIs & Services"** → **"Library"**
2. Search for **"Google People API"**
3. Click **"Enable"**

### Google Picker API (for file picker UI)

1. Search for **"Google Picker API"**
2. Click **"Enable"**

---

## Step 7: Configure API Quotas and Limits

1. Go to **"APIs & Services"** → **"Dashboard"**
2. Click on **"Google Drive API"**
3. Go to **"Quotas & System Limits"** tab
4. Review default quotas:
   - **Queries per day:** 1,000,000,000 (1 billion)
   - **Queries per 100 seconds per user:** 1,000
   - **Queries per 100 seconds:** 10,000

💡 **Tip:** These are generous free tier limits. For most applications, you won't hit these limits.

To increase quotas:
- Click **"Request quota increase"** (requires billing account)

---

## Step 8: Set Up Billing (Optional for Development)

⚠️ **Note:** Google Drive API is free for most use cases, but requires billing account for:
- Higher quota limits
- Production apps with many users

To enable billing:
1. Go to **"Billing"** in left sidebar
2. Click **"Link a billing account"**
3. Create or select existing billing account
4. Link to project

💡 **Don't worry:** You won't be charged unless you exceed free tier limits (which is rare)

Pricing: https://cloud.google.com/drive/pricing

---

## Step 9: Test Google Drive API Connection

Create a test script to verify the setup:

```python
# test_google_drive_connection.py
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def test_drive_connection():
    """Test Google Drive API connection"""

    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'config/google_oauth_credentials.json',
        scopes=SCOPES
    )

    # This will open browser for authentication
    credentials = flow.run_local_server(port=8501)

    # Build Drive service
    service = build('drive', 'v3', credentials=credentials)

    # Test: List first 10 files
    print("Testing Google Drive API connection...")
    results = service.files().list(
        pageSize=10,
        fields="files(id, name, mimeType)"
    ).execute()

    files = results.get('files', [])

    if not files:
        print('No files found in your Google Drive.')
    else:
        print('✅ Successfully connected to Google Drive!')
        print('\nFirst 10 files:')
        for file in files:
            print(f"  - {file['name']} ({file['mimeType']})")

    print("\n🎉 Google Drive API setup verified successfully!")

if __name__ == '__main__':
    test_drive_connection()
```

Run with:
```bash
python test_google_drive_connection.py
```

**Expected behavior:**
1. Browser opens for Google Sign-in
2. You authorize the app
3. Script lists your Google Drive files

---

## Step 10: Understanding OAuth Flow in Streamlit

Streamlit presents challenges for OAuth due to its stateless nature. Here's how we'll handle it:

### Approach 1: Query Parameters (Recommended)

```python
# OAuth flow in Streamlit
import streamlit as st
from google_auth_oauthlib.flow import Flow

# Get authorization URL
flow = Flow.from_client_secrets_file(
    'config/google_oauth_credentials.json',
    scopes=['https://www.googleapis.com/auth/drive.readonly'],
    redirect_uri='http://localhost:8501'
)

auth_url, state = flow.authorization_url(prompt='consent')

# Store state in session
st.session_state['oauth_state'] = state

# Show authorization link
st.markdown(f'[Authorize Google Drive]({auth_url})')

# After redirect, check query params
query_params = st.experimental_get_query_params()
if 'code' in query_params:
    code = query_params['code'][0]

    # Exchange code for token
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Save credentials
    st.session_state['drive_credentials'] = credentials_to_dict(credentials)
    st.success("Google Drive connected!")
```

### Approach 2: Streamlit Component (Alternative)

Use `streamlit-oauth` or custom component for seamless integration.

---

## Troubleshooting

### Error: "Access blocked: This app's request is invalid"

**Solution:**
1. Go to OAuth consent screen
2. Add your email to test users
3. Make sure app is in "Testing" status

### Error: "redirect_uri_mismatch"

**Solution:**
1. Go to OAuth credentials
2. Add exact redirect URI used in code to authorized redirect URIs
3. Common URIs: `http://localhost:8501`, `http://localhost:8501/oauth2callback`

### Error: "invalid_client"

**Solution:**
- Verify `google_oauth_credentials.json` is valid and complete
- Re-download credentials from Google Cloud Console

### Error: "insufficient permissions" or "insufficientFilePermissions"

**Solution:**
1. Check OAuth scopes requested
2. Ensure user granted all permissions
3. Re-authenticate with correct scopes

### Error: "The caller does not have permission"

**Solution:**
1. Ensure Google Drive API is enabled
2. Check OAuth consent screen configuration
3. Verify user is in test users list (if app is in Testing mode)

---

## Security Best Practices

1. ✅ Use OAuth 2.0 for user authorization (never use API keys for Drive)
2. ✅ Request minimum necessary scopes
3. ✅ Store OAuth tokens securely (encrypt in database)
4. ✅ Implement token refresh logic
5. ✅ Use HTTPS in production
6. ✅ Validate redirect URIs
7. ✅ Implement CSRF protection (use `state` parameter)
8. ✅ Set token expiration and refresh

---

## Production Checklist

Before deploying to production:

- [ ] Publish OAuth consent screen
- [ ] Submit app for Google verification (if using sensitive scopes)
- [ ] Add production domain to authorized domains
- [ ] Update redirect URIs for production URLs
- [ ] Enable billing account (for higher quotas)
- [ ] Set up monitoring and error logging
- [ ] Implement rate limiting
- [ ] Add user consent revocation functionality
- [ ] Review and comply with [Google API Terms of Service](https://developers.google.com/terms)

---

## Next Steps

After completing Google Cloud setup:

1. ✅ Verify `config/google_oauth_credentials.json` exists
2. → Continue to [Azure Setup](SETUP_AZURE.md) for OneDrive integration
3. → Start implementing cloud storage integration (Session 4)

---

## Useful Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/guides/about-sdk)
- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Google Drive API Scopes](https://developers.google.com/drive/api/guides/api-specific-auth)
- [OAuth Consent Screen Setup](https://support.google.com/cloud/answer/10311615)
- [Google API Quotas](https://console.cloud.google.com/apis/api/drive.googleapis.com/quotas)

---

**Setup Date:** 2025-12-04
**Version:** 1.0
**Status:** ✅ Ready for implementation
