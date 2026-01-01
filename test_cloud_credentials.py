"""
Test script to check if cloud credentials are saved correctly.

Usage:
    python test_cloud_credentials.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.auth.firebase_manager import firebase_manager
from app.database.settings_manager import SettingsManager
from app.auth.session_manager import SessionManager


def test_cloud_credentials():
    """Test cloud credentials retrieval."""
    print("=" * 70)
    print("Cloud Credentials Test")
    print("=" * 70)
    print()
    
    # Initialize Firebase
    print("1. Initializing Firebase...")
    try:
        success = firebase_manager.initialize_app()
        if not success:
            print("   ❌ Firebase initialization failed")
            return False
        print("   ✅ Firebase initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Initialize Settings Manager
    print()
    print("2. Initializing Settings Manager...")
    try:
        settings_manager = SettingsManager(firebase_manager.get_firestore_client())
        print("   ✅ Settings Manager initialized")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Get user ID (you'll need to provide this)
    print()
    print("3. Testing credentials retrieval...")
    print("   Enter your user ID (or press Enter to test with 'test_user'):")
    user_id = input("   User ID: ").strip() or "test_user"
    
    # Check Google Drive credentials
    print()
    print(f"4. Checking Google Drive credentials for user: {user_id}")
    try:
        drive_creds = settings_manager.get_cloud_credentials(user_id, 'google_drive')
        if drive_creds:
            print("   ✅ Google Drive credentials found!")
            print(f"   Client ID: {drive_creds.get('client_id', 'N/A')[:20]}...")
            print(f"   Has token: {bool(drive_creds.get('token'))}")
            print(f"   Has refresh token: {bool(drive_creds.get('refresh_token'))}")
        else:
            print("   ❌ No Google Drive credentials found")
            print("   This means credentials were not saved or user ID is incorrect")
    except Exception as e:
        print(f"   ❌ Error checking credentials: {e}")
        import traceback
        traceback.print_exc()
    
    # Check OneDrive credentials
    print()
    print(f"5. Checking OneDrive credentials for user: {user_id}")
    try:
        onedrive_creds = settings_manager.get_cloud_credentials(user_id, 'onedrive')
        if onedrive_creds:
            print("   ✅ OneDrive credentials found!")
        else:
            print("   ℹ️  No OneDrive credentials (expected if not connected)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 70)
    print("Test completed!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        test_cloud_credentials()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

