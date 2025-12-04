# API Key Configuration Guide

## Overview

Each user can now configure their personal Google Gemini API key. API keys are encrypted and stored securely in Firestore, isolated per user.

---

## 🚀 Quick Start

### For Users

1. **Sign in** to the application
2. **Open Settings** in the left sidebar (⚙️ Settings)
3. **Enter your Gemini API key**
4. **Click "Save API Key"** - The key will be validated automatically
5. **Done!** Your API key is saved and encrypted

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated key
5. Paste it in the Settings section

**Free tier includes:**
- 15 requests per minute
- 1 million tokens per day
- Sufficient for personal use

---

## 🔒 Security Features

### Encryption

- ✅ API keys are encrypted using **Fernet symmetric encryption**
- ✅ Encryption key stored separately from data
- ✅ No plaintext API keys in database
- ✅ Keys are only decrypted when needed

### Isolation

- ✅ Each user's API key is stored in their own Firestore document
- ✅ Firestore security rules ensure users can only access their own keys
- ✅ No API key sharing between users

### Storage

**Firestore Structure:**
```
settings/{user_id}/
  ├── gemini_api_key: "encrypted_base64_string"
  ├── gemini_api_key_updated_at: timestamp
  └── ... other settings
```

---

## ✨ Features

### API Key Validation

When you save an API key, the system automatically:
1. Tests the key with a lightweight Gemini API request
2. Lists available models to confirm access
3. Displays validation results immediately

**Validation Messages:**
- ✅ **Valid!** Found X available models
- ❌ **Invalid API key** - Check and try again
- ⚠️ **Valid but quota exceeded** - API limit reached
- ⚠️ **Valid but permissions insufficient** - Check API permissions

### Show/Hide API Key

- Click "Show API key" to display your saved key
- Click "Hide API key" to conceal it
- Keys are masked by default for security

### Delete API Key

- Click "Delete API Key" button
- Confirm deletion
- Key is permanently removed from Firestore

---

## 🔧 Technical Details

### SettingsManager Class

**Location:** `app/database/settings_manager.py`

**Key Methods:**
```python
# Save encrypted API key
settings_manager.save_api_key(user_id, api_key)

# Retrieve and decrypt API key
api_key = settings_manager.get_api_key(user_id)

# Delete API key
settings_manager.delete_api_key(user_id)
```

**Encryption Process:**
```python
1. Load encryption key from environment (ENCRYPTION_KEY)
2. Initialize Fernet cipher
3. Encrypt plaintext API key
4. Encode as base64
5. Store in Firestore
```

**Decryption Process:**
```python
1. Retrieve encrypted key from Firestore
2. Decode from base64
3. Decrypt using Fernet cipher
4. Return plaintext API key
```

### GeminiService Integration

**Updated Constructor:**
```python
# Old way (hardcoded config)
ai_service = GeminiService()  # Uses config.GEMINI_API_KEY

# New way (user-specific)
ai_service = GeminiService(api_key=user_api_key)
```

**Fallback Behavior:**
- If `api_key` parameter is None, falls back to `config.GEMINI_API_KEY`
- Allows backward compatibility with existing code
- Admins can still set a default key in config

### UI Component

**Location:** `ui/components/api_key_input.py`

**Function:** `render_api_key_input(settings_manager, user_id, language)`

**Features:**
- Bilingual support (English/Vietnamese)
- Input field with password masking
- Validation on save
- Show/hide toggle
- Delete confirmation
- Instructions with link to AI Studio
- Security note

---

## 🌐 Multi-language Support

### English UI

- Title: "🔑 Google Gemini API Configuration"
- Subtitle: "Configure your personal Gemini API key"
- Get key link: "Get your free API key here"
- Save button: "💾 Save API Key"
- Delete button: "🗑️ Delete API Key"

### Vietnamese UI (Sentence case)

- Title: "🔑 Cấu hình Google Gemini API"
- Subtitle: "Cấu hình khóa API Gemini cá nhân của bạn"
- Get key link: "Tạo khóa API miễn phí tại đây"
- Save button: "💾 Lưu khóa API"
- Delete button: "🗑️ Xóa khóa API"

---

## 📊 User Experience Flow

### First Time User

```
1. Sign in to app
   ↓
2. See "⚠️ No API key configured" in Settings
   ↓
3. Settings expander is auto-expanded
   ↓
4. Read instructions "How to get your API key"
   ↓
5. Click link to AI Studio
   ↓
6. Copy API key
   ↓
7. Paste in input field
   ↓
8. Click "Save API Key"
   ↓
9. System validates key (Loading...)
   ↓
10. ✅ Success! API key saved
   ↓
11. Settings expander auto-collapses
   ↓
12. Ready to use AI features
```

### Returning User

```
1. Sign in to app
   ↓
2. See "✅ API key configured" in Settings
   ↓
3. Settings expander is collapsed
   ↓
4. Can immediately use app
```

---

## ⚙️ Configuration

### Encryption Key Setup

**Option 1: Environment Variable (Recommended)**
```bash
export ENCRYPTION_KEY="your-fernet-key-here"
```

**Option 2: .env File**
```bash
# config/.env
ENCRYPTION_KEY=your-fernet-key-here
```

**Option 3: Auto-Generation**
- If no key is found, system generates one automatically
- Key is saved to `config/.env`
- ⚠️ Warning logged to ensure key is backed up

**Generate a New Key:**
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

---

## 🐛 Troubleshooting

### "Failed to save API key"

**Possible causes:**
- Firestore connection issue
- Invalid user ID
- Permission denied

**Solution:**
- Check Firebase configuration
- Verify Firestore security rules
- Check application logs

### "Invalid API key" during validation

**Possible causes:**
- Typo in API key
- Key not activated yet
- Key revoked

**Solution:**
- Double-check the key from AI Studio
- Try generating a new key
- Ensure key has proper permissions

### "Decryption error"

**Possible causes:**
- Encryption key changed
- Corrupted data in Firestore

**Solution:**
- Check ENCRYPTION_KEY environment variable
- Delete and re-save API key
- Check application logs for details

### "API key valid but quota exceeded"

**Possible causes:**
- Free tier limits reached
- Too many requests

**Solution:**
- Wait for quota to reset (daily)
- Upgrade to paid tier
- Reduce request frequency

---

## 🔐 Security Best Practices

### For Developers

1. ✅ **Never log plaintext API keys**
2. ✅ **Use environment variables for encryption key**
3. ✅ **Rotate encryption key periodically**
4. ✅ **Implement rate limiting**
5. ✅ **Monitor for suspicious activity**
6. ✅ **Use HTTPS in production**
7. ✅ **Validate API keys server-side only**

### For Users

1. ✅ **Never share your API key**
2. ✅ **Don't commit API keys to version control**
3. ✅ **Revoke compromised keys immediately**
4. ✅ **Monitor usage in Google AI Studio**
5. ✅ **Use separate keys for different applications**

---

## 📈 Future Enhancements

### Planned Features

- [ ] **Multiple API keys** per user (dev/prod separation)
- [ ] **Usage statistics** per API key
- [ ] **Automatic key rotation**
- [ ] **Quota alerts** via email/notification
- [ ] **API key expiration** with renewal reminders
- [ ] **Support for other AI providers** (OpenAI, Claude, etc.)

---

## 🆘 Support

### Common Questions

**Q: Can I use the same API key on multiple devices?**
A: Yes, but you'll need to enter it on each device. Keys are stored per-user, not per-device.

**Q: What happens if I change my API key?**
A: Old key is overwritten. Any in-progress operations using the old key will fail. Save the new key before processing.

**Q: Can I see my API key after saving?**
A: Yes, click "Show API key" button. It's masked by default for security.

**Q: Is my API key really secure?**
A: Yes. Keys are encrypted with Fernet (AES-128) and stored in Firestore with strict access rules.

---

**Last Updated:** 2025-12-04
**Version:** Session 3 Complete
**Status:** ✅ User-Specific API Keys Implemented
