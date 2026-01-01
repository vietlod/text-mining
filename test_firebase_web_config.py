"""
Quick test script to verify Firebase Web Config is loaded correctly.

Usage:
    python test_firebase_web_config.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.auth.streamlit_auth import StreamlitAuth
from app.auth.firebase_manager import firebase_manager


def test_firebase_web_config():
    """Test if Firebase Web config can be loaded."""
    print("=" * 70)
    print("Firebase Web Config Test")
    print("=" * 70)
    print()
    
    # Step 1: Check if file exists
    config_path = Path(__file__).parent / 'config' / 'firebase_web_config.json'
    print("1. Checking config file...")
    if config_path.exists():
        print(f"   ✅ File exists: {config_path}")
    else:
        print(f"   ❌ File not found: {config_path}")
        return False
    
    # Step 2: Validate JSON
    print()
    print("2. Validating JSON structure...")
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_fields = ['apiKey', 'authDomain', 'projectId']
        missing = [field for field in required_fields if field not in config]
        
        if missing:
            print(f"   ❌ Missing required fields: {missing}")
            return False
        
        print("   ✅ JSON is valid")
        print(f"   Project ID: {config.get('projectId')}")
        print(f"   Auth Domain: {config.get('authDomain')}")
        print(f"   API Key: {config.get('apiKey', '')[:20]}...")
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False
    
    # Step 3: Test StreamlitAuth method
    print()
    print("3. Testing StreamlitAuth._get_firebase_web_config()...")
    try:
        # Initialize Firebase Manager (if needed)
        if not firebase_manager.is_initialized():
            print("   Initializing Firebase Admin SDK...")
            firebase_manager.initialize_app()
        
        auth = StreamlitAuth(firebase_manager)
        web_config_json = auth._get_firebase_web_config()
        
        if web_config_json:
            print("   ✅ Method returned config successfully")
            config_dict = json.loads(web_config_json)
            print(f"   Project ID: {config_dict.get('projectId')}")
            print(f"   Auth Domain: {config_dict.get('authDomain')}")
        else:
            print("   ❌ Method returned None")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing method: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Success
    print()
    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print()
    print("Your Firebase Web Config is ready!")
    print("You can now run: python run_app.py")
    print("The 'Sign in with Google' button should work properly.")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = test_firebase_web_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print("❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

