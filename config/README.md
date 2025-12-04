# Configuration Files

This directory contains sensitive configuration files for cloud services.

## Required Files

### 1. `firebase_config.json`
Firebase Admin SDK credentials. Get from:
https://console.firebase.google.com/ → Project Settings → Service Accounts → Generate New Private Key

**Structure:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "...",
  "token_uri": "...",
  "auth_provider_x509_cert_url": "...",
  "client_x509_cert_url": "..."
}
```

### 2. `google_oauth_credentials.json`
Google Cloud OAuth2 credentials for Drive API. Get from:
https://console.cloud.google.com/ → APIs & Services → Credentials → Create OAuth 2.0 Client ID

**Structure:**
```json
{
  "web": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost:8501"]
  }
}
```

### 3. `azure_config.json`
Microsoft Azure App Registration credentials for OneDrive. Get from:
https://portal.azure.com/ → Azure Active Directory → App Registrations

**Structure:**
```json
{
  "client_id": "your-azure-client-id",
  "client_secret": "your-azure-client-secret",
  "tenant_id": "common",
  "redirect_uri": "http://localhost:8501"
}
```

### 4. `.env`
Environment variables for local development.

**Structure:**
```env
# Encryption key for API keys (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your-fernet-key

# Firebase Admin SDK path
FIREBASE_CREDENTIALS_PATH=config/firebase_config.json

# Google OAuth credentials path
GOOGLE_OAUTH_CREDENTIALS_PATH=config/google_oauth_credentials.json

# Azure credentials path
AZURE_CREDENTIALS_PATH=config/azure_config.json
```

## Security Notes

⚠️ **IMPORTANT:**
- Never commit these files to version control
- Add `config/*.json` and `config/.env` to `.gitignore`
- Use environment variables in production
- Rotate credentials regularly

## Setup Instructions

See the setup guides in the root directory:
- `SETUP_FIREBASE.md`
- `SETUP_GOOGLE_CLOUD.md`
- `SETUP_AZURE.md`
