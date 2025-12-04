# Microsoft Azure Setup Guide

This guide will walk you through setting up Microsoft OneDrive integration using Microsoft Graph API for the Text-Mining application.

## Prerequisites

- Microsoft account (personal or work/school account)
- Project with internet connection

## Estimated Time: 15-20 minutes

---

## Step 1: Access Azure Portal

1. Go to [Azure Portal](https://portal.azure.com/)
2. Sign in with your Microsoft account
3. If you don't have an Azure subscription, you can still use Azure AD for app registration (free)

---

## Step 2: Register Application in Azure AD

1. In Azure Portal, search for **"Azure Active Directory"** or **"Microsoft Entra ID"** (new name)
2. Click on **Azure Active Directory**
3. In left sidebar, click **"App registrations"**
4. Click **"+ New registration"**

### 2.1 Configure Application Registration

**Name:** `Text-Mining Research Tool`

**Supported account types:** Select one:
- ✅ **Accounts in any organizational directory and personal Microsoft accounts** (Recommended)
  - Allows both personal OneDrive and OneDrive for Business
- Accounts in any organizational directory only
  - OneDrive for Business only
- Personal Microsoft accounts only
  - Personal OneDrive only

**Redirect URI:**
- **Platform:** Select **"Web"**
- **URI:** Enter `http://localhost:8501`

Click **"Register"**

---

## Step 3: Save Application (Client) ID

After registration, you'll see the **Overview** page:

1. Copy and save these values:
   - **Application (client) ID:** e.g., `12345678-1234-1234-1234-123456789abc`
   - **Directory (tenant) ID:** e.g., `common` or specific tenant ID

💡 **Note:** Use `common` for multi-tenant apps (personal + work accounts)

---

## Step 4: Create Client Secret

1. In left sidebar, click **"Certificates & secrets"**
2. Go to **"Client secrets"** tab
3. Click **"+ New client secret"**

**Description:** `Text-Mining App Secret`

**Expires:**
- Select **24 months** (recommended for development)
- For production, use certificates instead of secrets

4. Click **"Add"**

5. **IMPORTANT:** Copy the **Value** immediately!
   - This is your **Client Secret**
   - It will never be shown again
   - If you lose it, you'll need to create a new one

Save as: `your-client-secret-value`

---

## Step 5: Configure API Permissions

1. In left sidebar, click **"API permissions"**
2. You'll see **"Microsoft Graph"** already added with `User.Read` permission

3. Click **"+ Add a permission"**
4. Select **"Microsoft Graph"**
5. Select **"Delegated permissions"** (not Application permissions)

6. Search and add these permissions:
   - ✅ **Files.Read** - Read user files
   - ✅ **Files.Read.All** - Read all files user can access
   - ✅ **Files.ReadWrite** - Read and write user files
   - ✅ **Files.ReadWrite.All** - Read and write all files user can access
   - ✅ **User.Read** - Sign in and read user profile (already added)

7. Click **"Add permissions"**

### 5.1 Grant Admin Consent (Optional but Recommended)

⚠️ **Note:** Some organizations require admin consent

1. Click **"Grant admin consent for [Your Organization]"**
2. Click **"Yes"** to confirm

If you don't have admin rights, users will need to consent when they first sign in.

---

## Step 6: Configure Authentication Settings

1. In left sidebar, click **"Authentication"**

### 6.1 Add Redirect URIs

**Web Platform:**
- `http://localhost:8501`
- `http://localhost:8501/oauth2callback`

For production, add:
- `https://yourdomain.com`
- `https://yourdomain.com/oauth2callback`

### 6.2 Implicit Grant and Hybrid Flows

**Don't enable** these for security reasons. Use Authorization Code flow instead.

### 6.3 Advanced Settings

**Allow public client flows:** **No** (keep disabled)

**Enable the following mobile and desktop flows:** **No** (keep disabled)

3. Click **"Save"**

---

## Step 7: Create Configuration File

Create `config/azure_config.json` with this structure:

```json
{
  "client_id": "your-application-client-id",
  "client_secret": "your-client-secret-value",
  "tenant_id": "common",
  "authority": "https://login.microsoftonline.com/common",
  "redirect_uri": "http://localhost:8501",
  "scopes": [
    "https://graph.microsoft.com/Files.Read.All",
    "https://graph.microsoft.com/Files.ReadWrite.All",
    "https://graph.microsoft.com/User.Read"
  ]
}
```

Replace:
- `your-application-client-id` with Application (client) ID from Step 3
- `your-client-secret-value` with Client Secret from Step 4

⚠️ **Security Warning:**
- **NEVER** commit this file to version control
- **NEVER** share your Client Secret publicly

---

## Step 8: Understanding Microsoft Graph API

Microsoft Graph API provides access to OneDrive and other Microsoft 365 services.

### Key Endpoints

**Get user's OneDrive:**
```
GET https://graph.microsoft.com/v1.0/me/drive
```

**List root folder:**
```
GET https://graph.microsoft.com/v1.0/me/drive/root/children
```

**List files in folder:**
```
GET https://graph.microsoft.com/v1.0/me/drive/items/{folder-id}/children
```

**Download file:**
```
GET https://graph.microsoft.com/v1.0/me/drive/items/{file-id}/content
```

**Upload file:**
```
PUT https://graph.microsoft.com/v1.0/me/drive/items/{folder-id}:/{filename}:/content
```

---

## Step 9: Test Microsoft Graph API Connection

Create a test script to verify the setup:

```python
# test_onedrive_connection.py
import msal
import requests
import json

def test_onedrive_connection():
    """Test Microsoft Graph API / OneDrive connection"""

    # Load config
    with open('config/azure_config.json', 'r') as f:
        config = json.load(f)

    # Create MSAL app
    app = msal.ConfidentialClientApplication(
        client_id=config['client_id'],
        client_credential=config['client_secret'],
        authority=config['authority']
    )

    # Get authorization URL
    auth_url = app.get_authorization_request_url(
        scopes=config['scopes'],
        redirect_uri=config['redirect_uri']
    )

    print("🔗 Open this URL in browser to authorize:")
    print(auth_url)
    print()

    # User authorizes and gets redirected with code
    auth_code = input("📋 Enter the authorization code from URL: ")

    # Exchange code for token
    result = app.acquire_token_by_authorization_code(
        code=auth_code,
        scopes=config['scopes'],
        redirect_uri=config['redirect_uri']
    )

    if 'access_token' in result:
        access_token = result['access_token']
        print("✅ Access token acquired successfully!")

        # Test API call - Get user info
        headers = {'Authorization': f'Bearer {access_token}'}

        # Get user profile
        user_response = requests.get(
            'https://graph.microsoft.com/v1.0/me',
            headers=headers
        )

        if user_response.status_code == 200:
            user = user_response.json()
            print(f"✅ Connected as: {user['displayName']} ({user['userPrincipalName']})")

        # Get OneDrive info
        drive_response = requests.get(
            'https://graph.microsoft.com/v1.0/me/drive',
            headers=headers
        )

        if drive_response.status_code == 200:
            drive = drive_response.json()
            print(f"✅ OneDrive: {drive['name']}")
            print(f"   Owner: {drive['owner']['user']['displayName']}")

        # List root folder files
        files_response = requests.get(
            'https://graph.microsoft.com/v1.0/me/drive/root/children',
            headers=headers
        )

        if files_response.status_code == 200:
            files = files_response.json()['value']
            print(f"✅ Found {len(files)} items in root folder:")
            for item in files[:5]:  # Show first 5
                item_type = 'Folder' if 'folder' in item else 'File'
                print(f"   - {item['name']} ({item_type})")

        print("\n🎉 OneDrive integration verified successfully!")

    else:
        print(f"❌ Error acquiring token: {result.get('error_description')}")

if __name__ == '__main__':
    test_onedrive_connection()
```

Run with:
```bash
python test_onedrive_connection.py
```

**Expected behavior:**
1. Script prints authorization URL
2. You open URL in browser and sign in
3. After authorization, you're redirected to `http://localhost:8501/?code=...`
4. Copy the `code` parameter value from URL
5. Paste into terminal
6. Script shows your OneDrive files

---

## Step 10: Understanding OAuth Flow with MSAL

Microsoft Authentication Library (MSAL) handles OAuth 2.0 flow:

### Authorization Code Flow (Recommended)

```python
import msal

# Create app
app = msal.ConfidentialClientApplication(
    client_id='your-client-id',
    client_credential='your-client-secret',
    authority='https://login.microsoftonline.com/common'
)

# Step 1: Get authorization URL
auth_url = app.get_authorization_request_url(
    scopes=['https://graph.microsoft.com/Files.Read.All'],
    redirect_uri='http://localhost:8501'
)

# User visits auth_url and authorizes
# Azure redirects to: http://localhost:8501?code=AUTH_CODE

# Step 2: Exchange code for token
result = app.acquire_token_by_authorization_code(
    code=auth_code,
    scopes=['https://graph.microsoft.com/Files.Read.All'],
    redirect_uri='http://localhost:8501'
)

access_token = result['access_token']
refresh_token = result['refresh_token']
```

### Token Refresh

```python
# When access token expires (1 hour), refresh it
result = app.acquire_token_by_refresh_token(
    refresh_token=refresh_token,
    scopes=['https://graph.microsoft.com/Files.Read.All']
)

new_access_token = result['access_token']
```

---

## Step 11: OneDrive vs OneDrive for Business

### Personal OneDrive
- Associated with personal Microsoft account (Outlook.com, Hotmail, Live)
- Consumer storage
- Use tenant: `common` or `consumers`

### OneDrive for Business
- Associated with work or school account (Microsoft 365, Office 365)
- Enterprise storage with admin controls
- Use tenant: `common` or `organizations` or specific tenant ID

💡 **Tip:** Use `common` tenant to support both account types

---

## Troubleshooting

### Error: "AADSTS50011: The redirect URI specified does not match"

**Solution:**
1. Go to Azure Portal → App registrations → Authentication
2. Add exact redirect URI used in code
3. Make sure it matches exactly (including trailing slash or not)

### Error: "AADSTS65001: User or administrator has not consented"

**Solution:**
1. Go to API permissions
2. Click "Grant admin consent"
3. Or ensure users consent during first sign-in

### Error: "AADSTS700016: Application not found in directory"

**Solution:**
- Verify client ID is correct
- Check if app registration exists
- Ensure you're using correct tenant

### Error: "InvalidAuthenticationToken" or "Access Denied"

**Solution:**
1. Check if access token is valid and not expired
2. Verify required permissions are granted
3. Re-authenticate user

### Error: "itemNotFound" when accessing files

**Solution:**
- Ensure file/folder ID is correct
- Check user has permission to access the item
- Verify scope includes `Files.Read.All` or `Files.ReadWrite.All`

---

## Security Best Practices

1. ✅ Use Authorization Code flow (not Implicit flow)
2. ✅ Store client secret securely (use Azure Key Vault in production)
3. ✅ Request minimum necessary permissions
4. ✅ Implement token refresh logic
5. ✅ Use HTTPS in production
6. ✅ Implement PKCE for additional security
7. ✅ Set short token expiration
8. ✅ Validate all API responses
9. ✅ Handle rate limiting (Graph API: 10,000 requests/10 minutes)

---

## Microsoft Graph API Quotas and Limits

### Per-user Limits
- **10,000 requests** per 10 minutes per user
- **4 concurrent requests** per user

### Per-app Limits
- Depends on license and tenant size
- Enterprise can have higher limits

### File Size Limits
- **Single upload:** Up to 250 MB
- **Large file upload (sessions):** Up to 10 GB

Throttling: https://learn.microsoft.com/en-us/graph/throttling

---

## Production Checklist

Before deploying to production:

- [ ] Use certificate authentication instead of client secret
- [ ] Add production redirect URIs
- [ ] Enable only required permissions (principle of least privilege)
- [ ] Implement proper error handling
- [ ] Add logging and monitoring
- [ ] Handle token expiration gracefully
- [ ] Implement retry logic for throttling
- [ ] Set up Azure Key Vault for secrets
- [ ] Review [Microsoft Graph API Terms](https://developer.microsoft.com/en-us/graph/terms-of-use)
- [ ] Consider using Microsoft Graph SDK instead of raw API calls

---

## Next Steps

After completing Azure setup:

1. ✅ Verify `config/azure_config.json` exists
2. ✅ All three cloud services configured:
   - Firebase (Authentication + Database)
   - Google Cloud (Drive API)
   - Azure (OneDrive API)
3. → Ready to start Session 2: Authentication Implementation

---

## Useful Resources

- [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/overview)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [OneDrive API Reference](https://learn.microsoft.com/en-us/graph/api/resources/onedrive)
- [Azure AD App Registration](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Microsoft Graph Permissions Reference](https://learn.microsoft.com/en-us/graph/permissions-reference)
- [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer) - Test API calls
- [Microsoft Graph SDK for Python](https://github.com/microsoftgraph/msgraph-sdk-python)

---

**Setup Date:** 2025-12-04
**Version:** 1.0
**Status:** ✅ Ready for implementation
