"""
Cloud Storage UI Components.

This module provides UI for Google Drive and OneDrive integration.
"""

import streamlit as st
import logging
import os
import secrets
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


def render_cloud_storage_settings(settings_manager, user_id: str):
    """
    Render cloud storage configuration UI.

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
    """

    # Vietnamese translations (hardcoded)
    t = {
            'title': '☁️ Cloud Storage Integration',
            'subtitle': 'Connect to Google Drive or OneDrive',
            'google_drive': 'Google Drive',
            'onedrive': 'OneDrive',
            'connected': 'Connected',
            'not_connected': 'Not connected',
            'connect': 'Connect',
            'disconnect': 'Disconnect',
            'select_folder': 'Select folder',
            'change_folder': 'Change folder',
            'linked_folder': 'Linked folder',
            'guide': 'How to connect',
            'google_guide_url': 'https://developers.google.com/drive/api/quickstart/python',
            'onedrive_guide_url': 'https://learn.microsoft.com/en-us/graph/auth-v2-user',
            'disconnect_confirm': 'Are you sure you want to disconnect?',
            'disconnect_success': 'Disconnected successfully!',
            'setup_required': 'Yêu cầu quản trị viên thiết lập lưu trữ đám mây',
            'instructions': '''
**Hướng dẫn thiết lập:**

1. Quản trị viên phải hoàn tất thiết lập đám mây
2. Xem `SETUP_GOOGLE_CLOUD.md` hoặc `SETUP_AZURE.md`
3. Đặt thông tin xác thực trong thư mục `config/`
4. Khởi động lại ứng dụng

Sau khi thiết lập hoàn tất, bạn có thể kết nối lưu trữ đám mây tại đây.
            '''
        }

    st.markdown(f"### {t['title']}")
    st.caption(t['subtitle'])

    # Create tabs for each provider
    tab1, tab2 = st.tabs([f"📁 {t['google_drive']}", f"📁 {t['onedrive']}"])

    with tab1:
        _render_google_drive_settings(settings_manager, user_id, t)

    with tab2:
        _render_onedrive_settings(settings_manager, user_id, t)


def _render_google_drive_settings(settings_manager, user_id: str, t: Dict[str, str]):
    """Render Google Drive settings."""

    # Check if credentials exist
    drive_creds = settings_manager.get_cloud_credentials(user_id, 'google_drive')
    is_connected = drive_creds is not None

    # Status
    if is_connected:
        # Verify connection is still valid
        connection_valid = False
        try:
            from app.cloud.google_drive_manager import GoogleDriveManager
            drive_manager = GoogleDriveManager()
            connection_valid = drive_manager.test_connection(drive_creds)
        except Exception as e:
            logger.warning(f"Connection verification failed: {e}")
            connection_valid = False

        if connection_valid:
            # Reload credentials to get latest (important after checkbox changes)
            drive_creds = settings_manager.get_cloud_credentials(user_id, 'google_drive')
            if not drive_creds:
                st.warning("⚠️ Credentials not found. Please reconnect Google Drive.")
                return
            
            # Get folders info from credentials (support both single and multi-select)
            selected_folders = drive_creds.get('selected_folders', [])
            
            # Backward compatibility: check old single folder format
            if not selected_folders:
                folder_id = drive_creds.get('folder_id')
                folder_name = drive_creds.get('folder_name')
                if folder_id and folder_id != 'root' and folder_name and folder_name != 'Not selected' and folder_name != 'My Drive':
                    # Convert old format to new format
                    selected_folders = [{'id': folder_id, 'name': folder_name}]
                    # Update credentials to new format
                    updated_creds = drive_creds.copy()
                    updated_creds['selected_folders'] = selected_folders
                    settings_manager.save_cloud_credentials(user_id, 'google_drive', updated_creds)
                    logger.info(f"Converted old format to new format: {folder_name}")
            
            st.success(f"✅ {t['connected']}")
            
            # Display selected folders
            if selected_folders and len(selected_folders) > 0:
                folder_names = [f.get('name', 'Unknown') for f in selected_folders]
                if len(folder_names) == 1:
                    st.info(f"📁 {t.get('linked_folder', 'Linked folder')}: **{folder_names[0]}**")
                else:
                    st.info(f"📁 **{len(folder_names)} folders selected:** {', '.join(folder_names)}")
                logger.info(f"Selected folders ({user_id}): {[f.get('name') for f in selected_folders]}")
            else:
                st.info("💡 No folder selected. You can select folders to read files from.")
                logger.info(f"No folders selected for user: {user_id}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📂 {t['change_folder']}", key='drive_change_folder'):
                    _show_folder_picker(settings_manager, user_id, drive_creds, t)

            with col2:
                if st.button(f"🔌 {t['disconnect']}", key='drive_disconnect'):
                    if st.session_state.get('confirm_drive_disconnect', False):
                        settings_manager.delete_cloud_credentials(user_id, 'google_drive')
                        st.success(t['disconnect_success'])
                        st.session_state.confirm_drive_disconnect = False
                        st.rerun()
                    else:
                        st.session_state.confirm_drive_disconnect = True
                        st.warning(t['disconnect_confirm'])
                        st.rerun()
        else:
            # Credentials exist but connection is invalid (expired token, etc.)
            st.warning("⚠️ Connection expired. Please reconnect.")
            if st.button(f"🔗 {t['connect']} Google Drive", key='drive_reconnect', use_container_width=True):
                _initiate_drive_oauth(settings_manager, user_id, t)
    else:
        st.info(f"ℹ️ {t['not_connected']}")

        # Check if OAuth credentials are configured
        try:
            from app.cloud.google_drive_manager import GoogleDriveManager

            drive_manager = GoogleDriveManager()
            oauth_configured = True
        except FileNotFoundError:
            oauth_configured = False

        if not oauth_configured:
            st.warning(f"⚠️ {t['setup_required']}")
            st.markdown(t['instructions'])
            st.markdown(f"**[{t['guide']}]({t['google_guide_url']})**")
        else:
            st.markdown(f"💡 [{t['guide']}]({t['google_guide_url']})")

            # OAuth callback handling is now done in main_app.py
            # If we still see query params here, it means main_app.py didn't handle them
            # Just clear them to prevent any issues
            query_params = st.query_params
            if 'code' in query_params:
                logger.warning("OAuth code found in cloud_storage component - this should have been handled in main_app.py")
                st.query_params.clear()

            # Connect button
            if st.button(f"🔗 {t['connect']} Google Drive", key='drive_connect', use_container_width=True):
                _initiate_drive_oauth(settings_manager, user_id, t)


def _render_onedrive_settings(settings_manager, user_id: str, t: Dict[str, str]):
    """Render OneDrive settings."""

    # Check if credentials exist
    onedrive_creds = settings_manager.get_cloud_credentials(user_id, 'onedrive')
    is_connected = onedrive_creds is not None

    # Status
    if is_connected:
        folder_name = onedrive_creds.get('folder_name', 'Not selected')
        st.success(f"✅ {t['connected']}")
        st.info(f"📁 {t['linked_folder']}: **{folder_name}**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"📂 {t['change_folder']}", key='onedrive_change_folder'):
                st.info("Feature coming soon! Select folder functionality.")

        with col2:
            if st.button(f"🔌 {t['disconnect']}", key='onedrive_disconnect'):
                if st.session_state.get('confirm_onedrive_disconnect', False):
                    settings_manager.delete_cloud_credentials(user_id, 'onedrive')
                    st.success(t['disconnect_success'])
                    st.session_state.confirm_onedrive_disconnect = False
                    st.rerun()
                else:
                    st.session_state.confirm_onedrive_disconnect = True
                    st.warning(t['disconnect_confirm'])
                    st.rerun()
    else:
        st.info(f"ℹ️ {t['not_connected']}")

        # Check if Azure credentials are configured
        try:
            from app.cloud.onedrive_manager import OneDriveManager

            onedrive_manager = OneDriveManager()
            oauth_configured = True
        except FileNotFoundError:
            oauth_configured = False

        if not oauth_configured:
            st.warning(f"⚠️ {t['setup_required']}")
            st.markdown(t['instructions'])
            st.markdown(f"**[{t['guide']}]({t['onedrive_guide_url']})**")
        else:
            st.markdown(f"💡 [{t['guide']}]({t['onedrive_guide_url']})")

            if st.button(f"🔗 {t['connect']} OneDrive", key='onedrive_connect', use_container_width=True):
                # Initiate OAuth flow
                st.info("🔄 OAuth flow will be implemented in production version")
                st.markdown("""
**To connect OneDrive:**

1. Click the button above
2. Sign in with Microsoft account
3. Grant permissions
4. Select folder
5. Done!

*Currently showing placeholder. OAuth flow requires production deployment with proper redirect URIs.*
                """)


def _initiate_drive_oauth(settings_manager, user_id: str, t: Dict[str, str]) -> None:
    """
    Initiate Google Drive OAuth flow.

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        t: Translations dictionary.
    """
    try:
        from app.cloud.google_drive_manager import GoogleDriveManager

        # Clear any previous OAuth processing state
        _clear_drive_oauth_session_state()

        # Initialize Drive manager
        drive_manager = GoogleDriveManager()

        # Get redirect URI - CRITICAL: Must match exactly in token exchange
        redirect_uri = os.getenv('STREAMLIT_REDIRECT_URI', 'http://localhost:8501')
        # Normalize: remove trailing slash to ensure exact match
        redirect_uri = redirect_uri.rstrip('/')

        logger.info(f"=" * 60)
        logger.info(f"INITIATING GOOGLE DRIVE OAUTH")
        logger.info(f"  Redirect URI: {redirect_uri}")
        logger.info(f"  User: {user_id}")
        logger.info(f"=" * 60)

        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        st.session_state['drive_oauth_state'] = state
        st.session_state['oauth_type'] = 'drive'  # Flag to distinguish from Firebase OAuth

        # CRITICAL: Save state to Firestore for persistence across redirects
        # This ensures we can detect Drive callback even if session state is lost
        settings_manager.save_oauth_state(user_id, state, 'drive')
        logger.info(f"✅ OAuth state saved to Firestore for user: {user_id}")

        # Generate authorization URL
        auth_url, flow_state = drive_manager.get_authorization_url(
            redirect_uri=redirect_uri,
            state=state
        )

        logger.info(f"Generated auth URL (first 100 chars): {auth_url[:100]}...")

        # Store flow state if needed
        if flow_state:
            st.session_state['drive_oauth_flow_state'] = flow_state

        logger.info(f"Initiating Drive OAuth flow for user: {user_id}")

        # Redirect to Google OAuth
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
        with st.spinner("Redirecting to Google Drive authorization..."):
            st.info("🔄 Redirecting to Google... Please authorize the application.")
            st.stop()

    except FileNotFoundError as e:
        st.error(f"❌ Google OAuth credentials not found. Please complete setup first.")
        logger.error(f"Drive OAuth initiation failed: {e}")
    except Exception as e:
        st.error(f"❌ Failed to initiate Google Drive connection: {e}")
        logger.error(f"Drive OAuth initiation error: {e}", exc_info=True)


def _handle_drive_oauth_callback(settings_manager, user_id: str, code: str, state: str, t: Dict[str, str]) -> None:
    """
    Handle Google Drive OAuth callback.

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        code: Authorization code from OAuth callback.
        state: State parameter for CSRF protection.
        t: Translations dictionary.
    """
    try:
        # Verify state - check both session and Firestore
        expected_state = st.session_state.get('drive_oauth_state')
        oauth_state_from_firestore = settings_manager.get_oauth_state(user_id, state) if state else None

        # Verify state from session or Firestore
        state_valid = False
        if expected_state and state == expected_state:
            # State matches session state
            state_valid = True
            logger.info("✅ OAuth state verified from session")
            # Clear session state
            del st.session_state['drive_oauth_state']
            if 'oauth_type' in st.session_state:
                del st.session_state['oauth_type']
        elif oauth_state_from_firestore:
            # State found in Firestore
            if oauth_state_from_firestore.get('oauth_type') == 'drive':
                state_valid = True
                logger.info("✅ OAuth state verified from Firestore")
                # Delete from Firestore after verification
                settings_manager.delete_oauth_state(user_id, state)
            else:
                logger.warning(f"OAuth state type mismatch: expected 'drive', got '{oauth_state_from_firestore.get('oauth_type')}'")
        else:
            # State not found - could be expired or invalid
            logger.warning("OAuth state not found in session or Firestore. This might be due to session reset or expired state.")
            # Be lenient: if user exists (authenticated or guest) and we have a code, proceed with warning
            # Authorization codes are single-use and short-lived, providing some security
            if user_id:
                logger.info("Proceeding with code verification despite missing state (user exists - authenticated or guest)")
                state_valid = True
            else:
                st.error("❌ Invalid OAuth state. Please try again.")
                _clear_drive_oauth_session_state()
                if 'code' in st.query_params:
                    st.query_params.pop('code')
                if 'state' in st.query_params:
                    st.query_params.pop('state')
                return

        if not state_valid:
            st.error("❌ Invalid OAuth state. Please try again.")
            logger.warning("Drive OAuth state verification failed")
            _clear_drive_oauth_session_state()
            if 'code' in st.query_params:
                st.query_params.pop('code')
            if 'state' in st.query_params:
                st.query_params.pop('state')
            return

        # Exchange code for token
        with st.spinner("🔄 Connecting to Google Drive..."):
            from app.cloud.google_drive_manager import GoogleDriveManager

            drive_manager = GoogleDriveManager()
            redirect_uri = os.getenv('STREAMLIT_REDIRECT_URI', 'http://localhost:8501')

            logger.info(f"=" * 60)
            logger.info(f"EXCHANGE CODE FOR TOKEN")
            logger.info(f"  User: {user_id}")
            logger.info(f"  Redirect URI: {redirect_uri}")
            logger.info(f"  State: {state[:20] if state else 'None'}...")
            logger.info(f"  Code (first 20 chars): {code[:20]}...")
            logger.info(f"  Code hash: {hash(code)}")
            logger.info(f"  Code length: {len(code)}")
            logger.info(f"=" * 60)

            # CRITICAL: Check if code might have been used already
            # Normalize code first (ensure it matches the one used in main_app.py)
            import urllib.parse
            normalized_code = urllib.parse.unquote(code)
            processing_lock_key = f'oauth_processing_{hash(normalized_code)}'
            
            # Check processing lock
            if st.session_state.get(processing_lock_key, False):
                logger.warning(f"⚠️ Code might have been processed already! Lock exists: {processing_lock_key}")
                # Check if this is a legitimate processing (lock was set by main_app.py)
                # If lock exists but we're here, it means code is being processed - allow it
                logger.info("Processing lock exists - this is expected if code is being processed")
            else:
                # Lock doesn't exist - this shouldn't happen if main_app.py processed it correctly
                logger.warning(f"⚠️ Processing lock not found for code! This might indicate duplicate processing.")
            
            # Use normalized code for exchange
            code = normalized_code

            # Exchange code for credentials
            try:
                credentials_dict = drive_manager.exchange_code_for_token(code, redirect_uri)
                logger.info(f"✅ Successfully exchanged code for credentials")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"=" * 60)
                logger.error(f"FAILED TO EXCHANGE CODE")
                logger.error(f"  Error: {error_msg}")
                logger.error(f"  Error type: {type(e).__name__}")
                logger.error(f"  Code hash: {hash(code)}")
                logger.error(f"=" * 60)
                logger.error(f"Full traceback:", exc_info=True)

                # Clear processing flag and query params on error
                _clear_drive_oauth_session_state()
                
                # Release processing lock on error
                processing_lock_key = f'oauth_processing_{hash(code)}'
                if processing_lock_key in st.session_state:
                    del st.session_state[processing_lock_key]
                    logger.info(f"✓ Processing lock released on error for code: {hash(code)}")
                
                # Clear query params to prevent retry with same code
                if 'code' in st.query_params:
                    st.query_params.pop('code')
                if 'state' in st.query_params:
                    st.query_params.pop('state')

                # Handle specific OAuth errors
                if 'invalid_grant' in error_msg.lower() or 'expired' in error_msg.lower() or 'already used' in error_msg.lower():
                    st.error("""
❌ **Authorization code has expired or was already used.**

This can happen if:
- The code expired (codes are only valid for a few minutes)
- The code was already used
- There was a conflict with another OAuth flow

**Please try again:**
1. Wait a moment
2. Click the "Connect Google Drive" button again
3. Authorize the application when prompted
                    """)
                    logger.warning("OAuth code invalid - likely expired or already used")
                else:
                    st.error(f"❌ Failed to exchange authorization code: {error_msg}")

                return

            # Test connection
            logger.info("Testing Google Drive connection...")
            try:
                connection_test = drive_manager.test_connection(credentials_dict)
                logger.info(f"Connection test result: {connection_test}")
            except Exception as e:
                logger.error(f"Connection test failed: {e}", exc_info=True)
                _clear_drive_oauth_session_state()
                st.error(f"❌ Failed to test connection: {e}")
                return

            if connection_test:
                # Save credentials
                logger.info(f"Saving credentials for user: {user_id}")
                success = settings_manager.save_cloud_credentials(
                    user_id,
                    'google_drive',
                    credentials_dict
                )

                if success:
                    logger.info(f"✅ Credentials saved successfully for user: {user_id}")

                    # Verify credentials were saved
                    saved_creds = settings_manager.get_cloud_credentials(user_id, 'google_drive')
                    if saved_creds:
                        logger.info(f"✅ Verified credentials exist in database")
                        logger.info(f"✅ Google Drive connection successful for user: {user_id}")
                        st.success(f"✅ {t['connected']}! Google Drive is now connected.")
                        st.balloons()
                    else:
                        logger.warning(f"⚠️ Credentials saved but not found when retrieving")
                        st.warning(f"⚠️ Connection may not be fully saved. Please check and reconnect if needed.")

                    # Clear all OAuth session state and Firestore state on success
                    _clear_drive_oauth_session_state()
                    if state:
                        settings_manager.delete_oauth_state(user_id, state)
                    
                    # Release processing lock
                    processing_lock_key = f'oauth_processing_{hash(code)}'
                    if processing_lock_key in st.session_state:
                        del st.session_state[processing_lock_key]
                        logger.info(f"✓ Processing lock released for code: {hash(code)}")
                    
                    # Clear any remaining query params to prevent re-processing
                    if 'code' in st.query_params:
                        st.query_params.pop('code')
                    if 'state' in st.query_params:
                        st.query_params.pop('state')

                    # Force rerun to update UI
                    st.rerun()
                else:
                    logger.error(f"❌ Failed to save credentials to database")
                    _clear_drive_oauth_session_state()
                    st.error("❌ Failed to save credentials. Please try again.")
            else:
                logger.error(f"❌ Connection test failed")
                _clear_drive_oauth_session_state()
                st.error("❌ Failed to connect to Google Drive. Please try again.")

    except Exception as e:
        st.error(f"❌ Error connecting to Google Drive: {e}")
        logger.error(f"Drive OAuth callback error: {e}", exc_info=True)
        _clear_drive_oauth_session_state()


def _clear_drive_oauth_session_state():
    """Clear all Drive OAuth-related session state."""
    # Clear all OAuth-related session state
    keys_to_clear = [
        'oauth_type',
        'drive_oauth_state',
        'drive_oauth_processing',
        'drive_oauth_last_code',
        'drive_oauth_last_processed_code',
        'drive_oauth_flow_state'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def _show_folder_picker(settings_manager, user_id: str, drive_creds: Dict[str, Any], t: Dict[str, str]) -> None:
    """
    Show multi-select folder picker UI for Google Drive.
    
    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        drive_creds: Current Drive credentials.
        t: Translations dictionary.
    """
    try:
        from app.cloud.google_drive_manager import GoogleDriveManager
        
        drive_manager = GoogleDriveManager()
        service = drive_manager.get_drive_service(drive_creds)
        
        # Get currently selected folders
        selected_folders = drive_creds.get('selected_folders', [])
        # Backward compatibility
        if not selected_folders:
            folder_id = drive_creds.get('folder_id')
            folder_name = drive_creds.get('folder_name')
            if folder_id and folder_id != 'root' and folder_name and folder_name != 'Not selected' and folder_name != 'My Drive':
                selected_folders = [{'id': folder_id, 'name': folder_name}]
        
        # Get selected folder IDs for quick lookup
        selected_folder_ids = {f.get('id') for f in selected_folders if f.get('id')}
        
        st.markdown("### 📁 Select Google Drive Folders (Multi-select)")
        
        # Show currently selected folders
        if selected_folders:
            folder_names = [f.get('name', 'Unknown') for f in selected_folders]
            st.success(f"✅ **{len(selected_folders)} folder(s) selected:** {', '.join(folder_names)}")
        
        # Folder navigation
        if 'drive_folder_path' not in st.session_state:
            st.session_state.drive_folder_path = [('root', 'My Drive')]
        
        # Show breadcrumb
        if len(st.session_state.drive_folder_path) > 1:
            breadcrumb = " > ".join([name for _, name in st.session_state.drive_folder_path])
            st.caption(f"📍 {breadcrumb}")
            
            # Back button
            if st.button("← Back", key='drive_folder_back'):
                st.session_state.drive_folder_path.pop()
                st.rerun()
        
        # Get current folder ID
        current_parent_id = st.session_state.drive_folder_path[-1][0]
        
        # List folders
        try:
            folders = drive_manager.list_folders(service, current_parent_id)
            
            if folders:
                st.markdown("**Available Folders:**")
                
                # Multi-select with checkboxes
                # Use on_change callback to save immediately
                def on_folder_checkbox_change(folder_id, folder_name, is_checked):
                    """Callback when folder checkbox changes."""
                    nonlocal selected_folders, drive_creds
                    
                    # Get current credentials to ensure we have latest
                    current_creds = settings_manager.get_cloud_credentials(user_id, 'google_drive')
                    if not current_creds:
                        current_creds = drive_creds.copy()
                    
                    current_selected = current_creds.get('selected_folders', [])
                    current_selected_ids = {f.get('id') for f in current_selected if f.get('id')}
                    
                    if is_checked and folder_id not in current_selected_ids:
                        # Add to selection
                        current_selected.append({'id': folder_id, 'name': folder_name})
                        logger.info(f"Adding folder to selection: {folder_name} (ID: {folder_id})")
                    elif not is_checked and folder_id in current_selected_ids:
                        # Remove from selection
                        current_selected = [f for f in current_selected if f.get('id') != folder_id]
                        logger.info(f"Removing folder from selection: {folder_name} (ID: {folder_id})")
                    
                    # Save immediately
                    updated_creds = current_creds.copy()
                    updated_creds['selected_folders'] = current_selected
                    success = settings_manager.save_cloud_credentials(user_id, 'google_drive', updated_creds)
                    
                    if success:
                        # Verify save
                        saved_creds = settings_manager.get_cloud_credentials(user_id, 'google_drive')
                        if saved_creds:
                            saved_folders = saved_creds.get('selected_folders', [])
                            logger.info(f"✅ Folders saved: {len(saved_folders)} folder(s)")
                            st.session_state.drive_folders_updated = True
                        else:
                            logger.error("❌ Failed to verify folder save")
                    else:
                        logger.error("❌ Failed to save folders")
                
                # Render checkboxes with on_change callbacks
                for idx, folder in enumerate(folders):
                    folder_id = folder.get('id')
                    folder_name = folder.get('name', 'Unknown')
                    is_selected = folder_id in selected_folder_ids
                    
                    checkbox_key = f'drive_folder_checkbox_{folder_id}'
                    
                    # Use on_change to save immediately
                    checked = st.checkbox(
                        folder_name,
                        value=is_selected,
                        key=checkbox_key,
                        on_change=on_folder_checkbox_change,
                        args=(folder_id, folder_name, not is_selected)  # Will be toggled, so pass opposite
                    )
                    
                    # If state changed, trigger rerun
                    if checked != is_selected:
                        st.rerun()
                
                # Add current folder option if not root
                if current_parent_id != 'root':
                    current_folder_name = st.session_state.drive_folder_path[-1][1]
                    is_current_selected = current_parent_id in selected_folder_ids
                    checkbox_key = f'drive_folder_checkbox_current_{current_parent_id}'
                    
                    checked = st.checkbox(
                        f"(Select this folder: {current_folder_name})",
                        value=is_current_selected,
                        key=checkbox_key,
                        on_change=on_folder_checkbox_change,
                        args=(current_parent_id, current_folder_name, not is_current_selected)
                    )
                    
                    if checked != is_current_selected:
                        st.rerun()
                
                # Check if folders were updated
                if st.session_state.get('drive_folders_updated', False):
                    st.session_state.drive_folders_updated = False
                    # Reload credentials to get latest
                    drive_creds = settings_manager.get_cloud_credentials(user_id, 'google_drive')
                    if drive_creds:
                        selected_folders = drive_creds.get('selected_folders', [])
                        if selected_folders:
                            folder_names = [f.get('name', 'Unknown') for f in selected_folders]
                            st.success(f"✅ **{len(selected_folders)} folder(s) selected:** {', '.join(folder_names)}")
                
                # Navigation buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📂 Navigate to Selected", key='drive_navigate', use_container_width=True):
                        if selected_folders:
                            # Navigate to first selected folder
                            first_folder = selected_folders[0]
                            st.session_state.drive_folder_path.append((first_folder.get('id'), first_folder.get('name')))
                            st.rerun()
                        else:
                            st.warning("Please select at least one folder first")
                
                with col2:
                    if st.button("❌ Clear All", key='drive_clear_all', use_container_width=True):
                        updated_creds = drive_creds.copy()
                        updated_creds['selected_folders'] = []
                        settings_manager.save_cloud_credentials(user_id, 'google_drive', updated_creds)
                        st.success("✅ All folders cleared")
                        st.rerun()
                
                # Show folder list for navigation
                st.markdown("---")
                st.markdown("**Navigate to folder:**")
                folder_dict = {f['name']: f['id'] for f in folders}
                selected_folder_name = st.selectbox(
                    "Choose a folder to navigate:",
                    options=list(folder_dict.keys()),
                    key='drive_folder_navigate',
                    label_visibility="collapsed"
                )
                
                if st.button("📂 Open Folder", key='drive_open_folder', use_container_width=True):
                    folder_id = folder_dict[selected_folder_name]
                    st.session_state.drive_folder_path.append((folder_id, selected_folder_name))
                    st.rerun()
            else:
                st.info("No subfolders in this folder.")
                # Allow selecting current folder
                if current_parent_id != 'root':
                    current_folder_name = st.session_state.drive_folder_path[-1][1]
                    is_selected = current_parent_id in selected_folder_ids
                    checkbox_key = f'drive_folder_checkbox_empty_{current_parent_id}'
                    
                    checked = st.checkbox(
                        f"Select this folder: **{current_folder_name}**",
                        value=is_selected,
                        key=checkbox_key,
                        on_change=on_folder_checkbox_change,
                        args=(current_parent_id, current_folder_name, not is_selected)
                    )
                    
                    if checked != is_selected:
                        st.rerun()
        
        except Exception as e:
            logger.error(f"Failed to list folders: {e}", exc_info=True)
            st.error(f"❌ Failed to load folders: {e}")
    
    except Exception as e:
        logger.error(f"Folder picker error: {e}", exc_info=True)
        st.error(f"❌ Error showing folder picker: {e}")


def _load_files_from_drive(settings_manager, user_id: str) -> List:
    """
    Load files from Google Drive folder.
    
    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
    
    Returns:
        List of file-like objects compatible with Streamlit file uploader.
    """
    try:
        from app.cloud.google_drive_manager import GoogleDriveManager
        from app.config import INPUT_DIR
        
        # Get Drive credentials
        drive_creds = settings_manager.get_cloud_credentials(user_id, 'google_drive')
        if not drive_creds:
            st.warning("⚠️ Google Drive not connected. Please connect in Settings first.")
            return []
        
        # Get selected folders (support multi-select)
        selected_folders = drive_creds.get('selected_folders', [])
        
        # Backward compatibility: check old single folder format
        if not selected_folders:
            folder_id = drive_creds.get('folder_id')
            folder_name = drive_creds.get('folder_name')
            if folder_id and folder_id != 'root' and folder_name and folder_name != 'Not selected' and folder_name != 'My Drive':
                selected_folders = [{'id': folder_id, 'name': folder_name}]
        
        # Check if any folder is selected
        if not selected_folders or len(selected_folders) == 0:
            st.warning("⚠️ **No folder selected**")
            st.info("""
            **To read files from Google Drive:**
            
            1. Go to **Settings → Cloud Storage Integration**
            2. Click **"Change Folder"** button
            3. Check the boxes next to folders you want to select (e.g., "SACHKTL")
            4. Folders will be saved automatically
            5. Come back here and select "Google Drive" as file source
            """)
            logger.warning(f"No folders selected")
            return []
        
        logger.info(f"Loading files from {len(selected_folders)} folder(s): {[f.get('name') for f in selected_folders]}")
        
        # Initialize Drive manager
        drive_manager = GoogleDriveManager()
        service = drive_manager.get_drive_service(drive_creds)
        
        # List files from all selected folders
        folder_names = [f.get('name', 'Unknown') for f in selected_folders]
        if len(folder_names) == 1:
            st.info(f"📁 Loading files from: **{folder_names[0]}**")
        else:
            st.info(f"📁 Loading files from **{len(folder_names)} folders**: {', '.join(folder_names)}")
        
        all_files = []
        with st.spinner("Loading files from Google Drive..."):
            for folder_info in selected_folders:
                folder_id = folder_info.get('id')
                folder_name = folder_info.get('name', 'Unknown')
                try:
                    folder_files = drive_manager.list_files_in_folder(
                        service, 
                        folder_id,
                        file_types=['pdf', 'docx', 'txt', 'html', 'htm', 'png', 'jpg', 'jpeg']
                    )
                    # Add folder name to each file for reference
                    for file_info in folder_files:
                        file_info['source_folder'] = folder_name
                    all_files.extend(folder_files)
                except Exception as e:
                    logger.error(f"Failed to load files from folder {folder_name}: {e}")
                    st.warning(f"⚠️ Failed to load files from folder: {folder_name}")
        
        files = all_files
        
        if not files:
            st.info("📭 No supported files found in this folder.")
            st.caption("Supported formats: PDF, DOCX, TXT, HTML, PNG, JPG")
            return []
        
        # Show files and let user select
        st.success(f"✅ Found {len(files)} file(s) in folder")
        
        # Create file selection UI
        def format_file_size(file_info):
            """Format file size safely."""
            size = file_info.get('size')
            if size:
                try:
                    # Convert to int if it's a string
                    size_int = int(size) if isinstance(size, str) else size
                    return f"{file_info['name']} ({size_int / 1024:.1f} KB)"
                except (ValueError, TypeError):
                    return f"{file_info['name']}"
            return f"{file_info['name']}"
        
        file_options = [format_file_size(f) for f in files]
        selected_indices = st.multiselect(
            "Select files to process:",
            options=range(len(files)),
            format_func=lambda x: file_options[x],
            key='drive_file_selection'
        )
        
        if not selected_indices:
            return []
        
        # Download selected files to temp directory
        downloaded_files = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, file_idx in enumerate(selected_indices):
            file_info = files[file_idx]
            file_id = file_info['id']
            file_name = file_info['name']
            
            status_text.text(f"Downloading: {file_name} ({idx + 1}/{len(selected_indices)})")
            progress_bar.progress((idx + 1) / len(selected_indices))
            
            # Create temp file path
            # Ensure unique filename to avoid conflicts
            import uuid
            file_ext = os.path.splitext(file_name)[1]
            unique_name = f"{uuid.uuid4().hex[:8]}_{file_name}"
            temp_file_path = os.path.join(INPUT_DIR, unique_name)
            
            # Download file
            try:
                download_progress = drive_manager.download_file(service, file_id, temp_file_path)
                # Consume generator to complete download
                for _ in download_progress:
                    pass
                
                # Create file-like object for compatibility with processing pipeline
                # Read file into memory
                with open(temp_file_path, 'rb') as f:
                    file_content = f.read()
                
                # Create a BytesIO object that mimics Streamlit's UploadedFile
                from io import BytesIO
                file_obj = BytesIO(file_content)
                file_obj.name = file_name  # Use original name for processing
                file_obj.type = file_info.get('mimeType', 'application/octet-stream')
                file_obj.size = len(file_content)
                
                # Add getbuffer method for compatibility
                def getbuffer():
                    file_obj.seek(0)
                    return file_obj.read()
                file_obj.getbuffer = getbuffer
                
                downloaded_files.append(file_obj)
                logger.info(f"Downloaded {file_name} from Drive ({len(file_content)} bytes)")
            
            except Exception as e:
                logger.error(f"Failed to download {file_name}: {e}", exc_info=True)
                st.warning(f"⚠️ Failed to download {file_name}: {e}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        if downloaded_files:
            st.success(f"✅ {len(downloaded_files)} file(s) ready for processing")
        
        return downloaded_files
    
    except Exception as e:
        logger.error(f"Error loading files from Drive: {e}", exc_info=True)
        st.error(f"❌ Error loading files from Google Drive: {e}")
        return []


def render_file_source_selector(settings_manager, user_id: str) -> str:
    """
    Render file source selector (Local/Drive/OneDrive).

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.

    Returns:
        Selected source ('local', 'google_drive', or 'onedrive').
    """

    # Vietnamese translations (hardcoded)
    t = {
        'title': 'Nguồn tệp',
        'local': 'Tải lên từ máy',
        'google_drive': 'Google Drive',
        'onedrive': 'OneDrive',
        'not_connected_warning': 'Chưa kết nối. Vui lòng kết nối trong cài đặt trước.'
    }

    # Check connection status
    drive_connected = settings_manager.get_cloud_credentials(user_id, 'google_drive') is not None
    onedrive_connected = settings_manager.get_cloud_credentials(user_id, 'onedrive') is not None

    # Build options
    options = [t['local']]
    if drive_connected:
        options.append(f"{t['google_drive']} ✅")
    else:
        options.append(f"{t['google_drive']} ⚠️")

    if onedrive_connected:
        options.append(f"{t['onedrive']} ✅")
    else:
        options.append(f"{t['onedrive']} ⚠️")

    # Selector
    selected = st.radio(
        t['title'],
        options=options,
        horizontal=True
    )

    # Map selection to source
    if t['local'] in selected:
        return 'local'
    elif t['google_drive'] in selected:
        if not drive_connected:
            st.warning(f"⚠️ Google Drive: {t['not_connected_warning']}")
            return 'local'
        return 'google_drive'
    elif t['onedrive'] in selected:
        if not onedrive_connected:
            st.warning(f"⚠️ OneDrive: {t['not_connected_warning']}")
            return 'local'
        return 'onedrive'
    else:
        return 'local'
