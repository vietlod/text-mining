"""
Test script to verify Firebase setup and connection.

Run this script after completing Firebase setup to ensure everything works.

Usage:
    python test_firebase_connection.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.auth.firebase_manager import firebase_manager


def test_firebase_connection():
    """Test Firebase Admin SDK connection and Firestore operations."""

    print("=" * 60)
    print("Firebase Connection Test")
    print("=" * 60)
    print()

    # Step 1: Initialize Firebase
    print("1. Initializing Firebase Admin SDK...")
    try:
        success = firebase_manager.initialize_app()

        if success:
            print("   ✅ Firebase initialized successfully!")
        else:
            print("   ❌ Firebase initialization failed")
            print()
            print("   Please check:")
            print("   - config/firebase_config.json exists")
            print("   - File contains valid service account credentials")
            print("   - See SETUP_FIREBASE.md for setup instructions")
            return False

    except FileNotFoundError as e:
        print(f"   ❌ Error: {e}")
        print()
        print("   Setup Instructions:")
        print("   1. Go to https://console.firebase.google.com/")
        print("   2. Create a Firebase project")
        print("   3. Go to Project Settings → Service Accounts")
        print("   4. Click 'Generate new private key'")
        print("   5. Save as config/firebase_config.json")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

    print()

    # Step 2: Test Firestore connection
    print("2. Testing Firestore connection...")
    try:
        db = firebase_manager.get_firestore_client()
        print("   ✅ Firestore client created successfully!")
    except Exception as e:
        print(f"   ❌ Firestore error: {e}")
        return False

    print()

    # Step 3: Test write operation
    print("3. Testing Firestore write operation...")
    try:
        test_ref = db.collection('_test').document('connection_test')
        import datetime
        from firebase_admin import firestore

        test_ref.set({
            'test': 'Firebase connection test',
            'timestamp': firestore.SERVER_TIMESTAMP,
            'status': 'success'
        })
        print("   ✅ Successfully wrote test document to Firestore!")
    except Exception as e:
        print(f"   ❌ Write operation failed: {e}")
        print()
        print("   Possible causes:")
        print("   - Firestore not enabled in Firebase Console")
        print("   - Incorrect security rules")
        print("   - Network connection issues")
        return False

    print()

    # Step 4: Test read operation
    print("4. Testing Firestore read operation...")
    try:
        doc = test_ref.get()
        if doc.exists:
            data = doc.to_dict()
            print(f"   ✅ Successfully read test document!")
            print(f"   Data: {data}")
        else:
            print("   ❌ Document does not exist")
            return False
    except Exception as e:
        print(f"   ❌ Read operation failed: {e}")
        return False

    print()

    # Step 5: Clean up test document
    print("5. Cleaning up test document...")
    try:
        test_ref.delete()
        print("   ✅ Test document deleted successfully!")
    except Exception as e:
        print(f"   ⚠️ Warning: Could not delete test document: {e}")

    print()

    # Step 6: Test user profile operations
    print("6. Testing user profile operations...")
    try:
        test_uid = "test_user_123"
        test_email = "test@example.com"

        # Create test user profile
        firebase_manager.create_user_profile(
            uid=test_uid,
            email=test_email,
            display_name="Test User"
        )
        print("   ✅ User profile created successfully!")

        # Read user profile
        profile = firebase_manager.get_user_profile(test_uid)
        if profile:
            print(f"   ✅ User profile retrieved: {profile['email']}")
        else:
            print("   ❌ Could not retrieve user profile")
            return False

        # Clean up test user
        firebase_manager.delete_user_profile(test_uid)
        print("   ✅ Test user profile deleted!")

    except Exception as e:
        print(f"   ❌ User profile operations failed: {e}")
        return False

    print()
    print("=" * 60)
    print("🎉 All tests passed successfully!")
    print("=" * 60)
    print()
    print("Firebase is properly configured and ready to use.")
    print()
    print("Next steps:")
    print("1. Start the Streamlit app: streamlit run ui/main.py")
    print("2. Complete Google Cloud setup (SETUP_GOOGLE_CLOUD.md)")
    print("3. Complete Azure setup (SETUP_AZURE.md)")
    print()

    return True


def test_firebase_auth():
    """Test Firebase Authentication token verification."""

    print()
    print("=" * 60)
    print("Firebase Authentication Test (Optional)")
    print("=" * 60)
    print()
    print("To test token verification:")
    print("1. Get a Firebase ID token from your web app")
    print("2. Run: firebase_manager.verify_id_token(token)")
    print()
    print("Skipping automated auth test (requires actual user token)")
    print()


if __name__ == "__main__":
    print()
    print("🔥 Firebase Connection Test Script")
    print()

    # Run main test
    success = test_firebase_connection()

    if success:
        # Optional auth test info
        test_firebase_auth()

        # Exit with success
        sys.exit(0)
    else:
        print()
        print("❌ Tests failed. Please fix issues and try again.")
        print()
        sys.exit(1)
