"""
Streamlit Authentication UI components.

This module handles:
- Login page rendering
- Google Sign-in integration
- Authentication flow management
"""

import logging
import json
import os
from typing import Optional, Callable
from pathlib import Path
import streamlit as st
from streamlit.components.v1 import html

from .firebase_manager import FirebaseManager
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class StreamlitAuth:
    """
    Manages authentication UI in Streamlit.

    Provides login page, sign-in flow, and logout functionality.
    """

    def __init__(self, firebase_manager: FirebaseManager):
        """
        Initialize Streamlit Auth.

        Args:
            firebase_manager: FirebaseManager instance.
        """
        self.firebase_manager = firebase_manager

    def render_login_page(self, title: str = "Text-Mining Research Tool",
                         subtitle: str = "Advanced Vietnamese Document Analysis") -> None:
        """
        Render the beautiful landing page with Google Sign-in.

        Args:
            title: Application title.
            subtitle: Application subtitle.
        """
        # Check for token in query params (OAuth callback)
        self._check_oauth_callback()

    def render_login_page(self, title: str = "Text-Mining Research Tool",
                         subtitle: str = "Advanced Vietnamese Document Analysis") -> None:
        """
        Render the beautiful landing page with Google Sign-in.

        Args:
            title: Application title.
            subtitle: Application subtitle.
        """
        # Check for token in query params (OAuth callback)
        self._check_oauth_callback()

    def render_login_page(self, title: str = "Text-Mining Research Tool",
                         subtitle: str = "Advanced Vietnamese Document Analysis") -> None:
        """
        Render the beautiful landing page with Google Sign-in.

        Args:
            title: Application title.
            subtitle: Application subtitle.
        """
        # Check for token in query params (OAuth callback)
        self._check_oauth_callback()

        # Landing page styles
        st.markdown("""
        <style>
        /* Main Container - Professional Gradient */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #111827 100%);
            background-attachment: fixed;
        }
        
        /* Glassmorphism Card Effect - Enhanced Visibility */
        .glass-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-top: 1px solid rgba(255, 255, 255, 0.3);
            border-left: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 24px;
            padding: 2.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08));
        }

        /* Hero Section */
        .hero-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 4rem 1rem 2rem 1rem;
            margin-bottom: 2rem;
            animation: fadeIn 1s ease-out;
            width: 100%;
        }

        .hero-title {
            font-family: 'Inter', sans-serif;
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(120deg, #e2e8f0 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            letter-spacing: -0.02em;
            text-align: center;
            width: 100%;
        }

        .hero-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.25rem;
            color: #cbd5e1;
            font-weight: 300;
            max-width: 800px;
            margin: 0 auto 3rem auto;
            line-height: 1.6;
            text-align: center;
            width: 100%;
            display: block;
        }

        /* Feature Cards */
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            background: rgba(255, 255, 255, 0.1);
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            margin-left: auto;
            margin-right: auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .feature-title {
            color: #f1f5f9;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            text-align: center;
        }

        .feature-desc {
            color: #94a3b8;
            font-size: 0.95rem;
            line-height: 1.6;
            text-align: center;
        }

        /* Sign In Section */
        .signin-wrapper {
            margin-top: 4rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            width: 100%;
        }

        /* Custom Styling for Streamlit Button */
        div.stButton {
            text-align: center;
            display: flex;
            justify-content: center;
        }

        div.stButton > button {
            background: linear-gradient(90deg, #4285f4 0%, #357ae8 100%);
            color: white;
            border: none;
            padding: 0.75rem 2.5rem;
            font-size: 1.2rem;
            font-weight: 600;
            border-radius: 50px;
            box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
            transition: all 0.3s ease;
            width: auto;
            min-width: 300px;
            height: auto;
            margin: 0 auto;
            display: block;
        }

        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(66, 133, 244, 0.4);
            background: linear-gradient(90deg, #357ae8 0%, #2a65c7 100%);
            color: white;
            border: none;
        }

        div.stButton > button:active {
            transform: translateY(0);
            color: white;
        }
        
        div.stButton > button:focus {
            color: white;
            border: none;
            outline: none;
        }

        .security-note {
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 1rem;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            width: 100%;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Hide default streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

        # Hero Section
        st.markdown(f"""
        <div class="hero-container">
            <h1 class="hero-title">{title}</h1>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

        # Features Grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="glass-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Multi-format Processing</div>
                <div class="feature-desc">
                    Seamlessly analyze PDF, DOCX, HTML, and images. Advanced OCR for Vietnamese documents.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="glass-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">AI Intelligence</div>
                <div class="feature-desc">
                    Powered by Google Gemini for deep semantic understanding and precise keyword extraction.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="glass-card">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Investment Insights</div>
                <div class="feature-desc">
                    Generate comprehensive Excel reports with statistical analysis for data-driven decisions.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Sign-in Section (Simplified)
        st.markdown('<div class="signin-wrapper">', unsafe_allow_html=True)
        
        # Render sign-in button
        self._render_signin_options()
            
        st.markdown('</div>', unsafe_allow_html=True)

    def _render_signin_options(self) -> None:
        """Render sign-in options based on available methods."""

        # Check if Firebase is initialized
        if not self.firebase_manager.is_initialized():
            st.error(
                "⚠️ Firebase not configured. Please complete setup first.\n\n"
                "See `SETUP_FIREBASE.md` for instructions."
            )
            return

        # Render Google Sign-in button
        self._render_firebase_web_signin()

    def _render_firebase_web_signin(self) -> None:
        """
        Render Google Sign-in using OAuth redirect flow.

        Uses Google OAuth 2.0 redirect instead of Firebase Web SDK popup
        to avoid iframe restrictions in Streamlit.
        """
        # Get Firebase config for web
        firebase_web_config = self._get_firebase_web_config()

        if not firebase_web_config:
            st.warning(
                "⚠️ Firebase Web configuration not available. "
                "Using alternative sign-in method."
            )
            self._render_alternative_signin()
            return

        # Parse config
        try:
            config_dict = json.loads(firebase_web_config)
        except:
            st.error("Invalid Firebase Web config")
            return

        # TEMPORARY: Firebase Auth is disabled - skip all OAuth callbacks
        # All OAuth callbacks are now assumed to be Drive callbacks
        # This prevents conflicts and allows Drive OAuth to work without authentication
        query_params = st.query_params
        if 'code' in query_params:
            # Skip Firebase Auth handler completely - let Drive handler process it
            logger.info("=" * 60)
            logger.info("FIREBASE AUTH DISABLED - SKIPPING OAUTH CALLBACK")
            logger.info("  All OAuth callbacks are handled by Drive OAuth handler")
            logger.info("=" * 60)
            # Do NOT process the code here - let Drive handler in main_app.py process it
            pass
        # Disabled Firebase Auth OAuth handling - keep code commented for reference
        elif False:
            # Check if user is authenticated - if yes, this is likely a Drive callback
            from app.auth.session_manager import SessionManager
            user = SessionManager.get_current_user()
            is_authenticated = user is not None
            
            # CRITICAL: If user is authenticated, this MUST be a Drive callback
            # Skip Firebase Auth handler completely
            if is_authenticated:
                logger.info("=" * 60)
                logger.info("SKIPPING FIREBASE AUTH CALLBACK")
                logger.info(f"  Reason: User is authenticated (this must be Drive callback)")
                logger.info(f"  User: {user.get('email', 'unknown') if user else 'unknown'}")
                logger.info(f"  Code in URL: {'code' in query_params}")
                logger.info("=" * 60)
                # Don't handle it here - let Drive callback handler in main_app.py process it
                # CRITICAL: Do NOT process the code here to prevent "invalid_grant" error
                pass
            else:
                # User is NOT authenticated - could be Firebase Auth callback
                # But we need to check if this is actually a Drive callback that lost session state
                state = query_params.get('state', '')
                
                # Check Firestore for OAuth state to determine callback type
                oauth_state_from_firestore = None
                if state:
                    try:
                        from app.database.settings_manager import SettingsManager
                        from app.auth.firebase_manager import firebase_manager
                        settings_manager = SettingsManager(firebase_manager.get_firestore_client())
                        # Search by state only (user_id not known before authentication)
                        oauth_state_from_firestore = settings_manager.get_oauth_state('', state)
                        if oauth_state_from_firestore:
                            logger.info(f"Found OAuth state in Firestore: type={oauth_state_from_firestore.get('oauth_type')}")
                    except Exception as e:
                        logger.debug(f"Could not check Firestore OAuth state: {e}")
                
                # Only handle as Firebase Auth callback if:
                # 1. User is NOT authenticated (login flow)
                # 2. AND oauth_type is not 'drive' in session, AND
                # 3. AND Firestore state is not 'drive' (if found)
                session_oauth_type = st.session_state.get('oauth_type')
                firestore_oauth_type = oauth_state_from_firestore.get('oauth_type') if oauth_state_from_firestore else None
                
                is_drive_callback = (
                    session_oauth_type == 'drive' or 
                    firestore_oauth_type == 'drive'
                )
                
                if not is_drive_callback:
                    # This is a Firebase Auth OAuth callback
                    code = query_params.get('code')
                    # Handle callback (state may be empty if session was reset)
                    self._handle_oauth_callback(code, state)
                    return
                else:
                    # This is a Drive callback but user session was lost
                    # Don't handle here - let main_app.py handle it when user re-authenticates
                    logger.info("Detected Drive callback but user not authenticated - skipping Firebase Auth handler")
                    pass

        # TEMPORARY: Firebase Auth sign-in button is disabled
        # Show info message instead
        st.info("""
        🔓 **Direct Access Mode**
        
        Authentication is temporarily disabled. You can use the app directly.
        
        To connect Google Drive, go to **Settings → Cloud Storage Integration**.
        """)
        
        # Disabled sign-in button - keep code commented for reference
        if False:
            # Generate OAuth URL
            auth_url = self._generate_google_oauth_url(config_dict)
            
            if not auth_url:
                st.error("Failed to generate OAuth URL. Please check your configuration.")
                return

            # Center the button and security note together
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🔐 Sign in with Google",
                    use_container_width=True,
                    type="primary",
                    key="google_signin_main"
                ):
                    # Redirect to Google OAuth
                    st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
                    with st.spinner("Redirecting to Google Sign-in..."):
                        st.stop()
                
                # Security note immediately below button, inside the same column
                st.markdown("""
                <div class="security-note">
                    <p style="margin: 0;">🔒 Protected by Enterprise-Grade Security • Firebase Authentication</p>
                </div>
                """, unsafe_allow_html=True)

    def _generate_google_oauth_url(self, firebase_config: dict) -> Optional[str]:
        """
        Generate Google OAuth 2.0 authorization URL for Firebase authentication.

        Args:
            firebase_config: Firebase Web config dictionary.

        Returns:
            OAuth authorization URL, or None if failed.
        """
        try:
            import secrets
            from urllib.parse import urlencode

            # Generate state for CSRF protection
            state = secrets.token_urlsafe(32)
            # Store state in session (may be lost on redirect, but we'll handle it)
            st.session_state['oauth_state'] = state
            st.session_state['oauth_type'] = 'firebase'  # Flag to distinguish from Drive OAuth
            # Also store in a more persistent way - use a timestamp-based key
            import time
            st.session_state[f'oauth_state_{int(time.time())}'] = state

            # Get OAuth credentials
            oauth_creds_path = Path(__file__).parent.parent.parent / 'config' / 'google_oauth_credentials.json'
            if not oauth_creds_path.exists():
                logger.error("Google OAuth credentials not found")
                return None

            with open(oauth_creds_path, 'r') as f:
                oauth_creds = json.load(f)

            client_id = oauth_creds.get('web', {}).get('client_id')
            if not client_id:
                logger.error("Client ID not found in OAuth credentials")
                return None

            # Get current URL for redirect
            # Streamlit runs on localhost:8501 by default
            # In production, this should be the actual domain
            try:
                # Try to get from environment or use default
                import socket
                hostname = socket.gethostname()
                # For local development
                redirect_uri = os.getenv('STREAMLIT_REDIRECT_URI', 'http://localhost:8501')
            except:
                redirect_uri = 'http://localhost:8501'

            # Build OAuth URL
            # Using Google Identity Services scope for Firebase
            scopes = [
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ]

            params = {
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': ' '.join(scopes),
                'state': state,
                'access_type': 'offline',
                'prompt': 'consent'
            }

            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
            return auth_url

        except Exception as e:
            logger.error(f"Error generating OAuth URL: {e}")
            return None

    def _handle_oauth_callback(self, code: str, state: str) -> None:
        """
        Handle OAuth callback and exchange code for Firebase ID token.

        Args:
            code: Authorization code from OAuth callback.
            state: State parameter for CSRF protection.
        """
        try:
            # Verify state (more lenient for Streamlit session issues)
            expected_state = st.session_state.get('oauth_state')
            
            # In Streamlit, session state may be lost on redirect
            # So we make state verification more lenient:
            # - If state exists in session and matches, great
            # - If state doesn't exist but we have a code, still proceed (with warning)
            # - Only reject if state exists but doesn't match (potential CSRF)
            
            # Try to find state in session (including timestamped versions)
            state_found = False
            if expected_state:
                if state == expected_state:
                    state_found = True
                    # State matches, clear it
                    del st.session_state['oauth_state']
                else:
                    # State exists but doesn't match - potential CSRF attack
                    st.error("❌ Invalid OAuth state. Possible security issue. Please try again.")
                    logger.warning(f"OAuth state mismatch: expected {expected_state[:10]}..., got {state[:10]}...")
                    return
            
            # If state not found, try to find in timestamped keys (within last 5 minutes)
            if not state_found:
                import time
                current_time = int(time.time())
                for i in range(300):  # Check last 5 minutes (300 seconds)
                    timestamp_key = f'oauth_state_{current_time - i}'
                    if timestamp_key in st.session_state:
                        if st.session_state[timestamp_key] == state:
                            state_found = True
                            del st.session_state[timestamp_key]
                            break
                
                if not state_found:
                    # State not found - common in Streamlit after redirect
                    # Log warning but proceed - the code itself provides some security
                    # Authorization codes are single-use and short-lived
                    logger.warning("OAuth state not found in session (likely due to Streamlit redirect). Proceeding with code verification.")
                    st.info("ℹ️ Verifying authentication...")

            # Exchange code for token (hidden spinner - user already sees "Verifying authentication...")
            id_token = self._exchange_code_for_firebase_token(code)
            
            if id_token:
                self._handle_token_verification(id_token)
            else:
                st.error("❌ Failed to get authentication token. Please try again.")

        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            st.error(f"❌ Authentication error: {e}")

    def _exchange_code_for_firebase_token(self, code: str) -> Optional[str]:
        """
        Exchange OAuth code for Firebase ID token using Firebase REST API.

        Args:
            code: Authorization code from OAuth callback.

        Returns:
            Firebase ID token, or None if failed.
        """
        try:
            import requests
            import base64
            import json as json_lib

            # Get OAuth credentials
            oauth_creds_path = Path(__file__).parent.parent.parent / 'config' / 'google_oauth_credentials.json'
            if not oauth_creds_path.exists():
                logger.error("Google OAuth credentials not found")
                return None

            with open(oauth_creds_path, 'r') as f:
                oauth_creds = json.load(f)

            client_id = oauth_creds.get('web', {}).get('client_id')
            client_secret = oauth_creds.get('web', {}).get('client_secret')
            # Get redirect URI (should match the one used in authorization)
            redirect_uri = os.getenv('STREAMLIT_REDIRECT_URI', 'http://localhost:8501')

            if not client_id or not client_secret:
                logger.error("Missing OAuth credentials")
                return None

            # Exchange authorization code for Google ID token
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }

            response = requests.post(token_url, data=token_data)
            if response.status_code != 200:
                logger.error(f"Failed to exchange code: {response.text}")
                return None

            token_response = response.json()
            google_id_token = token_response.get('id_token')
            
            if not google_id_token:
                logger.error("No ID token in response")
                return None

            # Decode Google ID token to get user info
            parts = google_id_token.split('.')
            if len(parts) != 3:
                logger.error("Invalid Google ID token format")
                return None

            # Decode payload
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding

            try:
                user_info = json_lib.loads(base64.urlsafe_b64decode(payload))
            except:
                logger.error("Failed to decode Google ID token")
                return None

            email = user_info.get('email')
            if not email:
                logger.error("No email in Google ID token")
                return None

            # Get Firebase Web config
            firebase_web_config = self._get_firebase_web_config()
            if not firebase_web_config:
                logger.error("Firebase Web config not available")
                return None

            config_dict = json.loads(firebase_web_config)
            api_key = config_dict.get('apiKey')

            # Use Firebase Admin SDK to create/get user and generate custom token
            try:
                from firebase_admin import auth
                
                # Get or create Firebase user
                try:
                    user_record = auth.get_user_by_email(email)
                except auth.UserNotFoundError:
                    # Create new user
                    user_record = auth.create_user(
                        email=email,
                        display_name=user_info.get('name', email.split('@')[0]),
                        photo_url=user_info.get('picture'),
                        email_verified=user_info.get('email_verified', False)
                    )

                # Create custom token
                custom_token = auth.create_custom_token(user_record.uid)

                # Exchange custom token for Firebase ID token using REST API
                firebase_response = requests.post(
                    f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}",
                    json={
                        'token': custom_token.decode('utf-8'),
                        'returnSecureToken': True
                    }
                )

                if firebase_response.status_code == 200:
                    firebase_data = firebase_response.json()
                    return firebase_data.get('idToken')
                else:
                    logger.error(f"Failed to exchange custom token: {firebase_response.text}")
                    return None

            except Exception as e:
                logger.error(f"Error with Firebase Admin SDK: {e}")
                import traceback
                traceback.print_exc()
                return None

        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _render_alternative_signin(self) -> None:
        """Render alternative sign-in method (OAuth URL)."""
        st.markdown("""
        **Alternative Sign-in Method:**

        1. Click the button below to open Google Sign-in
        2. Authorize the application
        3. You'll be redirected back automatically
        """)

        # Generate OAuth URL if possible
        firebase_web_config = self._get_firebase_web_config()
        if firebase_web_config:
            try:
                config_dict = json.loads(firebase_web_config)
                auth_url = self._generate_google_oauth_url(config_dict)
                if auth_url:
                    st.markdown(f'<a href="{auth_url}" target="_blank">🔗 Open Google Sign-in</a>', unsafe_allow_html=True)
                    return
            except:
                pass

        st.info("Please configure Google OAuth credentials to enable this feature.")

    def _check_oauth_callback(self) -> None:
        """Check for OAuth callback with token in query parameters."""
        try:
            query_params = st.query_params

            # Check for firebase_token parameter
            if 'firebase_token' in query_params:
                token = query_params['firebase_token']

                # Clear query params
                st.query_params.clear()

                # Verify token
                self._handle_token_verification(token)

        except Exception as e:
            logger.error(f"Error checking OAuth callback: {e}")

    def _handle_token_verification(self, id_token: str) -> None:
        """
        Verify Firebase ID token and create user session.

        Args:
            id_token: Firebase ID token to verify.
        """
        # Verify token with Firebase Admin SDK (hidden spinner - user already sees "Verifying authentication...")
        user_info = self.firebase_manager.verify_id_token(id_token)

        if user_info:
            # Create/update user profile in Firestore
            self.firebase_manager.create_user_profile(
                uid=user_info['uid'],
                email=user_info['email'],
                display_name=user_info.get('name', user_info['email'].split('@')[0])
            )

            # Set user session
            SessionManager.set_user(user_info, id_token)

            st.success(f"✅ Welcome, {user_info.get('name', 'User')}!")
            st.balloons()

            # Rerun to show main app
            st.rerun()

        else:
            st.error("❌ Invalid or expired token. Please try again.")

    def _get_firebase_web_config(self) -> Optional[str]:
        """
        Get Firebase Web SDK configuration JSON.

        Returns:
            JSON string of Firebase config, or None if not available.
        """
        # Method 1: Try to load from dedicated Firebase Web config file
        web_config_path = Path(__file__).parent.parent.parent / 'config' / 'firebase_web_config.json'
        if web_config_path.exists():
            try:
                with open(web_config_path, 'r') as f:
                    web_config = json.load(f)
                    # Validate required fields
                    required_fields = ['apiKey', 'authDomain', 'projectId']
                    if all(field in web_config for field in required_fields):
                        return json.dumps(web_config)
                    else:
                        logger.warning(f"Firebase Web config missing required fields: {required_fields}")
            except Exception as e:
                logger.error(f"Error loading Firebase Web config: {e}")

        # Method 2: Try to construct from Admin SDK config + environment variable
        # This allows users to just provide the apiKey via environment variable
        try:
            admin_config_path = Path(__file__).parent.parent.parent / 'config' / 'firebase_config.json'
            if admin_config_path.exists():
                with open(admin_config_path, 'r') as f:
                    admin_config = json.load(f)
                
                # Get apiKey from environment variable
                api_key = os.getenv('FIREBASE_WEB_API_KEY')
                
                if api_key and 'project_id' in admin_config:
                    project_id = admin_config['project_id']
                    # Construct Firebase Web config
                    web_config = {
                        'apiKey': api_key,
                        'authDomain': f"{project_id}.firebaseapp.com",
                        'projectId': project_id,
                        'storageBucket': f"{project_id}.appspot.com",
                        'messagingSenderId': admin_config.get('client_id', ''),
                        'appId': os.getenv('FIREBASE_WEB_APP_ID', '')
                    }
                    # Only return if we have minimum required fields
                    if web_config['apiKey'] and web_config['authDomain'] and web_config['projectId']:
                        return json.dumps(web_config)
        except Exception as e:
            logger.debug(f"Could not construct Firebase Web config from Admin SDK: {e}")

        # Method 3: Try environment variable with full config JSON
        env_config = os.getenv('FIREBASE_WEB_CONFIG')
        if env_config:
            try:
                config_dict = json.loads(env_config)
                required_fields = ['apiKey', 'authDomain', 'projectId']
                if all(field in config_dict for field in required_fields):
                    return env_config
            except Exception as e:
                logger.debug(f"Invalid FIREBASE_WEB_CONFIG environment variable: {e}")

        # No config available
        return None

    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated.

        Returns:
            bool: True if authenticated, False otherwise.
        """
        return SessionManager.is_authenticated()

    def logout(self) -> None:
        """Logout current user and clear session."""
        SessionManager.logout()
        st.rerun()

    def require_auth(self, func: Callable) -> Callable:
        """
        Decorator to require authentication for a function.

        Args:
            func: Function to protect.

        Returns:
            Wrapped function that checks authentication.
        """
        def wrapper(*args, **kwargs):
            if not self.is_authenticated():
                self.render_login_page()
                st.stop()
            return func(*args, **kwargs)
        return wrapper


def render_user_menu():
    """Render user menu in sidebar with logout button."""
    if SessionManager.is_authenticated():
        user = SessionManager.get_current_user()

        with st.sidebar:
            st.divider()

            # User profile
            col1, col2 = st.columns([1, 3])
            with col1:
                if user.get('picture'):
                    st.image(user['picture'], width=50)
                else:
                    st.markdown("👤")

            with col2:
                st.markdown(f"**{user.get('name', 'User')}**")
                st.caption(user.get('email', ''))

            # Logout button
            if st.button("🚪 Sign Out", use_container_width=True):
                SessionManager.logout()
                st.rerun()
