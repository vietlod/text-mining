"""
Main application entry point with authentication.

This is the new main file that includes:
- Firebase authentication
- Session management
- User authentication guard
- Main app rendering
"""

import streamlit as st
import os
import sys
import logging

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.auth.firebase_manager import firebase_manager
from app.auth.session_manager import SessionManager
from app.auth.streamlit_auth import StreamlitAuth, render_user_menu

logger = logging.getLogger(__name__)

# Page Config (must be first Streamlit command)
st.set_page_config(
    page_title="Text-Mining Research Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_firebase():
    """
    Initialize Firebase on first run.

    Returns:
        bool: True if successful or already initialized, False otherwise.
    """
    if SessionManager.is_firebase_initialized():
        return True

    try:
        # Try to initialize Firebase
        success = firebase_manager.initialize_app()

        if success:
            SessionManager.set_firebase_initialized(True)
            return True
        else:
            return False

    except Exception as e:
        st.error(f"Firebase initialization error: {e}")
        return False


def render_setup_warning():
    """Display setup warning when Firebase is not configured."""
    st.error("⚠️ Firebase not configured")

    st.markdown("""
    ### First-time Setup Required

    Please complete the following steps to enable authentication:

    1. **Create Firebase Project**
       - Visit [Firebase Console](https://console.firebase.google.com/)
       - Create a new project
       - Enable Authentication with Google provider
       - Enable Cloud Firestore

    2. **Download Credentials**
       - Go to Project Settings → Service Accounts
       - Click "Generate new private key"
       - Save as `config/firebase_config.json`

    3. **Detailed Instructions**
       - See `SETUP_FIREBASE.md` in project root for step-by-step guide

    ---

    **For Development/Testing:** The app can run without authentication by modifying the code,
    but all user-specific features will be disabled.
    """)

    st.stop()


def main():
    """Main application entry point."""

    # Initialize session
    SessionManager.initialize_session()

    # Initialize Firebase (for Drive credentials storage, not for authentication)
    firebase_ready = initialize_firebase()

    if not firebase_ready:
        # If Firebase not available, still allow access but warn about Drive features
        st.warning("⚠️ Firebase not configured. Google Drive connection will not be available.")
        # Still render app without authentication
        render_app_without_auth()
        return

    # TEMPORARY: Bypass authentication - allow direct access
    # Google Drive OAuth will work with guest user
    logger.info("Authentication bypassed - allowing direct access to app")
    
    # Check for Drive OAuth callback
    query_params = st.query_params
    if 'code' in query_params:
        # This is likely a Drive OAuth callback
        logger.info("OAuth callback detected - processing Drive connection")
        render_app_without_auth()
        return

    # Render app without authentication requirement
    render_app_without_auth()


def render_authenticated_app():
    """Render the main application for authenticated users."""

    # Import main app logic (to avoid circular imports)
    from ui.main_app import render_main_app

    # Render user menu in sidebar
    render_user_menu()

    # Render main application
    render_main_app()


def render_app_without_auth():
    """Render the main application without authentication requirement."""
    
    # Import main app logic (to avoid circular imports)
    from ui.main_app import render_main_app

    # Create a guest user session for Drive credentials storage
    # Use unique session ID for each browser session to isolate credentials
    if 'guest_session_id' not in st.session_state:
        import uuid
        st.session_state.guest_session_id = str(uuid.uuid4())[:8]
        logger.info(f"Generated unique guest session ID: {st.session_state.guest_session_id}")
    
    guest_user_id = f'guest_{st.session_state.guest_session_id}'
    
    # Set guest user in session if not already set or if user_id changed
    current_user = SessionManager.get_current_user()
    if not SessionManager.is_authenticated() or (current_user and current_user.get('uid') != guest_user_id):
        guest_user = {
            'uid': guest_user_id,
            'email': f'guest_{st.session_state.guest_session_id}@local.app',
            'name': f'Guest User ({st.session_state.guest_session_id})',
            'email_verified': False
        }
        SessionManager.set_user(guest_user, None)
        logger.info(f"Guest user session created: {guest_user_id}")

    # Render main application
    render_main_app()


if __name__ == "__main__":
    main()
