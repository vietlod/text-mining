"""
Streamlit Authentication UI components.

This module handles:
- Login page rendering
- Google Sign-in integration
- Authentication flow management
"""

import logging
from typing import Optional, Callable
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
        Render the login page with Google Sign-in.

        Args:
            title: Application title.
            subtitle: Application subtitle.
        """
        # Center content
        st.markdown("""
        <style>
        .login-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
            text-align: center;
        }
        .login-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #1f1f1f;
        }
        .login-subtitle {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 3rem;
        }
        .signin-button {
            display: inline-block;
            padding: 12px 24px;
            background: #4285f4;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            transition: background 0.3s;
            cursor: pointer;
            border: none;
            font-size: 16px;
        }
        .signin-button:hover {
            background: #357ae8;
        }
        .info-box {
            margin-top: 2rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            color: #666;
        }
        </style>
        """, unsafe_allow_html=True)

        # Login container
        st.markdown(f"""
        <div class="login-container">
            <h1 class="login-title">🔍 {title}</h1>
            <p class="login-subtitle">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### Welcome! Please sign in to continue")

            # Check for token in query params (OAuth callback)
            self._check_oauth_callback()

            # Render sign-in options
            self._render_signin_options()

            # Information box
            st.info(
                "ℹ️ This application requires Google Sign-in for access. "
                "Your data is secured with Firebase Authentication."
            )

            # Setup instructions
            with st.expander("🔧 First time setup?"):
                st.markdown("""
                **For administrators:**

                1. Complete Firebase setup (see `SETUP_FIREBASE.md`)
                2. Place `firebase_config.json` in `config/` directory
                3. Configure Firebase Authentication with Google provider
                4. Deploy with proper credentials

                **For users:**

                Simply click "Sign in with Google" above!
                """)

    def _render_signin_options(self) -> None:
        """Render sign-in options based on available methods."""

        # Check if Firebase is initialized
        if not self.firebase_manager.is_initialized():
            st.error(
                "⚠️ Firebase not configured. Please complete setup first.\n\n"
                "See `SETUP_FIREBASE.md` for instructions."
            )
            return

        # Method 1: Firebase Web SDK with custom HTML/JS (Recommended)
        self._render_firebase_web_signin()

        st.markdown("---")

        # Method 2: Manual token input (for development/testing)
        with st.expander("🔧 Developer: Manual token input"):
            st.markdown("""
            For testing purposes, you can manually input a Firebase ID token.

            **How to get a token:**
            1. Visit [Firebase Auth Test](https://firebase.google.com/docs/auth/web/start)
            2. Sign in with your test account
            3. Open browser console
            4. Run: `firebase.auth().currentUser.getIdToken().then(token => console.log(token))`
            5. Copy the token and paste below
            """)

            token_input = st.text_input(
                "Firebase ID Token",
                type="password",
                help="Paste your Firebase ID token here"
            )

            if st.button("🔐 Verify Token", use_container_width=True):
                if token_input:
                    self._handle_token_verification(token_input)
                else:
                    st.warning("Please enter a token")

    def _render_firebase_web_signin(self) -> None:
        """
        Render Firebase Web SDK sign-in button.

        Uses Firebase Web SDK to handle Google Sign-in in browser,
        then passes ID token back to Streamlit for verification.
        """
        st.markdown("### Sign in with your Google account")

        # Get Firebase config for web
        firebase_web_config = self._get_firebase_web_config()

        if not firebase_web_config:
            st.warning(
                "⚠️ Firebase Web configuration not available. "
                "Using alternative sign-in method."
            )
            self._render_alternative_signin()
            return

        # Render Firebase Web SDK sign-in
        firebase_auth_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js"></script>
            <script src="https://www.gstatic.com/firebasejs/9.22.0/firebase-auth-compat.js"></script>
        </head>
        <body>
            <div style="text-align: center; padding: 20px;">
                <button id="google-signin-btn" style="
                    padding: 12px 24px;
                    background: #4285f4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    font-weight: 500;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 10px;
                ">
                    <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg">
                        <g fill="none" fill-rule="evenodd">
                            <path d="M17.6 9.2l-.1-1.8H9v3.4h4.8C13.6 12 13 13 12 13.6v2.2h3a8.8 8.8 0 0 0 2.6-6.6z" fill="#4285F4"/>
                            <path d="M9 18c2.4 0 4.5-.8 6-2.2l-3-2.2a5.4 5.4 0 0 1-8-2.9H1V13a9 9 0 0 0 8 5z" fill="#34A853"/>
                            <path d="M4 10.7a5.4 5.4 0 0 1 0-3.4V5H1a9 9 0 0 0 0 8l3-2.3z" fill="#FBBC05"/>
                            <path d="M9 3.6c1.3 0 2.5.4 3.4 1.3L15 2.3A9 9 0 0 0 1 5l3 2.4a5.4 5.4 0 0 1 5-3.7z" fill="#EA4335"/>
                        </g>
                    </svg>
                    Sign in with Google
                </button>
                <div id="status" style="margin-top: 20px; color: #666;"></div>
            </div>

            <script>
                // Firebase configuration
                const firebaseConfig = {firebase_web_config};

                // Initialize Firebase
                firebase.initializeApp(firebaseConfig);
                const auth = firebase.auth();
                const provider = new firebase.auth.GoogleAuthProvider();

                // Sign in button
                document.getElementById('google-signin-btn').addEventListener('click', async () => {{
                    const statusDiv = document.getElementById('status');
                    statusDiv.textContent = 'Signing in...';

                    try {{
                        const result = await auth.signInWithPopup(provider);
                        const user = result.user;
                        const idToken = await user.getIdToken();

                        statusDiv.textContent = 'Success! Verifying...';

                        // Pass token to Streamlit
                        window.parent.postMessage({{
                            type: 'firebase-auth',
                            idToken: idToken
                        }}, '*');

                        // Alternative: Redirect with token in query params
                        const url = new URL(window.location.href);
                        url.searchParams.set('firebase_token', idToken);
                        window.top.location.href = url.toString();

                    }} catch (error) {{
                        statusDiv.textContent = 'Error: ' + error.message;
                        statusDiv.style.color = '#d32f2f';
                    }}
                }});

                // Listen for messages from Streamlit
                window.addEventListener('message', (event) => {{
                    if (event.data.type === 'streamlit:render') {{
                        // Streamlit is ready
                    }}
                }});
            </script>
        </body>
        </html>
        """

        # Render the component
        html(firebase_auth_html, height=150)

        # Check for token in session (passed via postMessage or query params)
        if 'pending_token' in st.session_state:
            token = st.session_state.pop('pending_token')
            self._handle_token_verification(token)

    def _render_alternative_signin(self) -> None:
        """Render alternative sign-in method (OAuth URL)."""
        st.markdown("""
        **Alternative Sign-in Method:**

        1. Click the button below to open Google Sign-in
        2. Authorize the application
        3. Copy the token from the success page
        4. Paste it in the developer token input above
        """)

        # This would generate an OAuth URL if we had OAuth configured
        st.button("🔗 Open Google Sign-in", use_container_width=True)

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
        with st.spinner("Verifying credentials..."):
            # Verify token with Firebase Admin SDK
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
        # In production, this should come from environment or config file
        # For now, return None to use alternative method
        # TODO: Implement Firebase Web config retrieval
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
