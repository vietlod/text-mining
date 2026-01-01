"""
Helper script to generate Firebase Web Config file.

This script helps you create config/firebase_web_config.json by:
1. Reading your existing firebase_config.json (Admin SDK)
2. Guiding you to get the Web API Key from Firebase Console
3. Auto-generating the web config file

Usage:
    python setup_firebase_web_config.py
"""

import json
import os
import sys
from pathlib import Path


def print_header():
    """Print script header."""
    print("=" * 70)
    print("Firebase Web Config Setup Helper")
    print("=" * 70)
    print()
    print("This script will help you create config/firebase_web_config.json")
    print("which is required for Google Sign-in button to work properly.")
    print()


def load_admin_config():
    """Load Firebase Admin SDK config."""
    config_path = Path(__file__).parent / 'config' / 'firebase_config.json'
    
    if not config_path.exists():
        print("❌ Error: config/firebase_config.json not found!")
        print()
        print("Please complete Firebase Admin SDK setup first:")
        print("1. Go to https://console.firebase.google.com/")
        print("2. Create a Firebase project")
        print("3. Go to Project Settings → Service Accounts")
        print("4. Click 'Generate new private key'")
        print("5. Save as config/firebase_config.json")
        print()
        print("See SETUP_FIREBASE.md for detailed instructions.")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'project_id' not in config:
            print("❌ Error: Invalid firebase_config.json (missing project_id)")
            return None
        
        return config
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in firebase_config.json")
        return None
    except Exception as e:
        print(f"❌ Error reading firebase_config.json: {e}")
        return None


def get_firebase_web_config_instructions():
    """Print instructions for getting Firebase Web config."""
    print("📋 How to get Firebase Web Config:")
    print()
    print("1. Go to: https://console.firebase.google.com/")
    print("2. Select your Firebase project")
    print("3. Click ⚙️ Settings → Project settings")
    print("4. Scroll down to 'Your apps' section")
    print("5. If no web app exists:")
    print("   - Click the Web icon (</>) to add a web app")
    print("   - Enter app nickname (e.g., 'Text-Mining Web App')")
    print("   - Click 'Register app'")
    print("6. You'll see a firebaseConfig object like this:")
    print()
    print("   const firebaseConfig = {")
    print("     apiKey: \"AIza...\",")
    print("     authDomain: \"your-project.firebaseapp.com\",")
    print("     projectId: \"your-project-id\",")
    print("     storageBucket: \"your-project.appspot.com\",")
    print("     messagingSenderId: \"123456789\",")
    print("     appId: \"1:123456789:web:abcdef\"")
    print("   };")
    print()
    print("7. Copy the values from this object")
    print()


def interactive_mode(admin_config):
    """Interactive mode: ask user for all values."""
    print("=" * 70)
    print("Interactive Mode")
    print("=" * 70)
    print()
    
    project_id = admin_config.get('project_id', '')
    client_id = admin_config.get('client_id', '')
    
    print(f"Detected from firebase_config.json:")
    print(f"  Project ID: {project_id}")
    print(f"  Client ID: {client_id}")
    print()
    
    get_firebase_web_config_instructions()
    
    # Get apiKey (required)
    print("Enter Firebase Web API Key (apiKey):")
    print("  (This is the 'apiKey' value from firebaseConfig object)")
    api_key = input("> ").strip()
    
    if not api_key:
        print("❌ Error: API Key is required!")
        return None
    
    if not api_key.startswith('AIza'):
        print("⚠️  Warning: API Key usually starts with 'AIza'")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return None
    
    # Get appId (optional but recommended)
    print()
    print("Enter Firebase Web App ID (appId) - Optional but recommended:")
    print("  (This is the 'appId' value from firebaseConfig, e.g., '1:123456789:web:abcdef')")
    print("  (Press Enter to skip)")
    app_id = input("> ").strip()
    
    # Get messagingSenderId (optional)
    print()
    print("Enter Messaging Sender ID - Optional:")
    print("  (This is the 'messagingSenderId' value from firebaseConfig)")
    print(f"  (Press Enter to use default: {client_id})")
    messaging_sender_id = input("> ").strip() or client_id
    
    # Construct config
    web_config = {
        'apiKey': api_key,
        'authDomain': f"{project_id}.firebaseapp.com",
        'projectId': project_id,
        'storageBucket': f"{project_id}.appspot.com",
        'messagingSenderId': messaging_sender_id
    }
    
    if app_id:
        web_config['appId'] = app_id
    
    return web_config


def quick_mode(admin_config):
    """Quick mode: only ask for apiKey, auto-generate the rest."""
    print("=" * 70)
    print("Quick Mode (Recommended)")
    print("=" * 70)
    print()
    
    project_id = admin_config.get('project_id', '')
    client_id = admin_config.get('client_id', '')
    
    print(f"Detected from firebase_config.json:")
    print(f"  Project ID: {project_id}")
    print(f"  Client ID: {client_id}")
    print()
    
    get_firebase_web_config_instructions()
    
    print("Enter Firebase Web API Key (apiKey):")
    print("  (This is the 'apiKey' value from firebaseConfig object)")
    api_key = input("> ").strip()
    
    if not api_key:
        print("❌ Error: API Key is required!")
        return None
    
    if not api_key.startswith('AIza'):
        print("⚠️  Warning: API Key usually starts with 'AIza'")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return None
    
    # Auto-generate config
    web_config = {
        'apiKey': api_key,
        'authDomain': f"{project_id}.firebaseapp.com",
        'projectId': project_id,
        'storageBucket': f"{project_id}.appspot.com",
        'messagingSenderId': client_id
    }
    
    print()
    print("✅ Auto-generated config (appId will be empty, but that's OK)")
    
    return web_config


def save_config(web_config):
    """Save web config to file."""
    config_path = Path(__file__).parent / 'config' / 'firebase_web_config.json'
    
    # Create config directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file already exists
    if config_path.exists():
        print()
        print(f"⚠️  File already exists: {config_path}")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("❌ Cancelled. File not saved.")
            return False
    
    try:
        with open(config_path, 'w') as f:
            json.dump(web_config, f, indent=2)
        
        print()
        print(f"✅ Successfully saved to: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False


def validate_config(web_config):
    """Validate the web config."""
    print()
    print("=" * 70)
    print("Validating Config")
    print("=" * 70)
    print()
    
    required_fields = ['apiKey', 'authDomain', 'projectId']
    missing = [field for field in required_fields if not web_config.get(field)]
    
    if missing:
        print(f"❌ Missing required fields: {', '.join(missing)}")
        return False
    
    print("✅ Required fields present:")
    for field in required_fields:
        value = web_config.get(field, '')
        # Mask sensitive values
        if field == 'apiKey' and len(value) > 10:
            display_value = value[:10] + '...' + value[-4:]
        else:
            display_value = value
        print(f"   {field}: {display_value}")
    
    optional_fields = ['storageBucket', 'messagingSenderId', 'appId']
    present_optional = [field for field in optional_fields if web_config.get(field)]
    
    if present_optional:
        print()
        print("✅ Optional fields present:")
        for field in present_optional:
            print(f"   {field}: {web_config.get(field)}")
    
    return True


def main():
    """Main function."""
    print_header()
    
    # Load Admin SDK config
    print("1. Loading Firebase Admin SDK config...")
    admin_config = load_admin_config()
    if not admin_config:
        sys.exit(1)
    
    print("   ✅ Found firebase_config.json")
    print()
    
    # Choose mode
    print("2. Choose setup mode:")
    print("   [1] Quick Mode - Only enter API Key (Recommended)")
    print("   [2] Interactive Mode - Enter all values manually")
    print()
    choice = input("Select mode (1 or 2): ").strip()
    
    if choice == '2':
        web_config = interactive_mode(admin_config)
    else:
        web_config = quick_mode(admin_config)
    
    if not web_config:
        print()
        print("❌ Failed to create config")
        sys.exit(1)
    
    # Validate
    if not validate_config(web_config):
        print()
        print("❌ Config validation failed")
        sys.exit(1)
    
    # Save
    print()
    print("3. Saving config file...")
    if not save_config(web_config):
        sys.exit(1)
    
    # Success
    print()
    print("=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Run your app: python run_app.py")
    print("2. The 'Sign in with Google' button should now work!")
    print()
    print("If you still see warnings, check:")
    print("- File exists at: config/firebase_web_config.json")
    print("- File contains valid JSON")
    print("- All required fields are present")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

