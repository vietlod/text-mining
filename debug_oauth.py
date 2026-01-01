"""
Debug script to test Google OAuth flow manually.
This will help identify the exact issue with invalid_grant error.
"""

import requests
import json
from urllib.parse import urlencode

# Load OAuth credentials
with open('config/google_oauth_credentials.json', 'r') as f:
    oauth_creds = json.load(f)

client_id = oauth_creds['web']['client_id']
client_secret = oauth_creds['web']['client_secret']
redirect_uri = 'http://localhost:8501'

print("=" * 70)
print("GOOGLE OAUTH DEBUG SCRIPT")
print("=" * 70)
print()

# Step 1: Generate authorization URL
print("STEP 1: Generate Authorization URL")
print("-" * 70)

scopes = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

auth_params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'scope': ' '.join(scopes),
    'access_type': 'offline',
    'prompt': 'consent',
    'state': 'test_state_12345'
}

auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"

print(f"Client ID: {client_id[:30]}...")
print(f"Redirect URI: {redirect_uri}")
print(f"Scopes: {scopes}")
print()
print("Authorization URL:")
print(auth_url)
print()
print("=" * 70)
print("INSTRUCTIONS:")
print("=" * 70)
print("1. Copy the URL above")
print("2. Open it in a browser")
print("3. Authorize the application")
print("4. You'll be redirected to: http://localhost:8501?code=XXXXX&state=XXXXX")
print("5. Copy the 'code' value from the URL")
print("6. Run this script again and provide the code when prompted")
print("=" * 70)
print()

# Step 2: Exchange code for token
code_input = input("Enter the authorization code (or press Enter to skip): ").strip()

if code_input:
    print()
    print("STEP 2: Exchange Code for Token")
    print("-" * 70)

    token_data = {
        'code': code_input,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    print("Token exchange request:")
    print(f"  URL: https://oauth2.googleapis.com/token")
    print(f"  client_id: {client_id[:30]}...")
    print(f"  redirect_uri: {redirect_uri}")
    print(f"  code length: {len(code_input)}")
    print(f"  code (first 30 chars): {code_input[:30]}...")
    print()

    print("Sending request...")
    response = requests.post('https://oauth2.googleapis.com/token', data=token_data)

    print()
    print("RESPONSE:")
    print("-" * 70)
    print(f"Status Code: {response.status_code}")
    print()

    if response.status_code == 200:
        print("✅ SUCCESS! Token exchange worked!")
        print()
        token_response = response.json()
        print("Response keys:", list(token_response.keys()))
        if 'access_token' in token_response:
            print(f"Access token (first 30 chars): {token_response['access_token'][:30]}...")
        if 'refresh_token' in token_response:
            print(f"Refresh token exists: Yes")
    else:
        print("❌ FAILED! Token exchange failed!")
        print()
        print("Error response:")
        print(response.text)
        print()

        # Try to parse error
        try:
            error_data = response.json()
            print("Parsed error:")
            for key, value in error_data.items():
                print(f"  {key}: {value}")
        except:
            pass

    print("=" * 70)
else:
    print("No code provided. Exiting.")
