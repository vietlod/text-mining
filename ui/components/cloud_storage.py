"""
Cloud Storage UI Components.

This module provides UI for Google Drive and OneDrive integration.
"""

import streamlit as st
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


def render_cloud_storage_settings(settings_manager, user_id: str, language: str = 'en'):
    """
    Render cloud storage configuration UI.

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        language: UI language ('en' or 'vi').
    """

    # Translations
    translations = {
        'en': {
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
            'setup_required': 'Cloud storage setup required by administrator',
            'instructions': '''
**Setup Instructions:**

1. Administrator must complete cloud setup
2. See `SETUP_GOOGLE_CLOUD.md` or `SETUP_AZURE.md`
3. Place credentials in `config/` directory
4. Restart application

Once setup is complete, you can connect your cloud storage here.
            '''
        },
        'vi': {
            'title': '☁️ Tích hợp lưu trữ đám mây',
            'subtitle': 'Kết nối với Google Drive hoặc OneDrive',
            'google_drive': 'Google Drive',
            'onedrive': 'OneDrive',
            'connected': 'Đã kết nối',
            'not_connected': 'Chưa kết nối',
            'connect': 'Kết nối',
            'disconnect': 'Ngắt kết nối',
            'select_folder': 'Chọn thư mục',
            'change_folder': 'Thay đổi thư mục',
            'linked_folder': 'Thư mục đã liên kết',
            'guide': 'Hướng dẫn kết nối',
            'google_guide_url': 'https://developers.google.com/drive/api/quickstart/python',
            'onedrive_guide_url': 'https://learn.microsoft.com/en-us/graph/auth-v2-user',
            'disconnect_confirm': 'Bạn có chắc muốn ngắt kết nối?',
            'disconnect_success': 'Đã ngắt kết nối thành công!',
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
    }

    t = translations.get(language, translations['en'])

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
        folder_name = drive_creds.get('folder_name', 'Not selected')
        st.success(f"✅ {t['connected']}")
        st.info(f"📁 {t['linked_folder']}: **{folder_name}**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"📂 {t['change_folder']}", key='drive_change_folder'):
                st.info("Feature coming soon! Select folder functionality.")

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

            if st.button(f"🔗 {t['connect']} Google Drive", key='drive_connect', use_container_width=True):
                # Initiate OAuth flow
                st.info("🔄 OAuth flow will be implemented in production version")
                st.markdown("""
**To connect Google Drive:**

1. Click the button above
2. Sign in with Google
3. Grant permissions
4. Select folder
5. Done!

*Currently showing placeholder. OAuth flow requires production deployment with proper redirect URIs.*
                """)


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


def render_file_source_selector(settings_manager, user_id: str, language: str = 'en') -> str:
    """
    Render file source selector (Local/Drive/OneDrive).

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        language: UI language.

    Returns:
        Selected source ('local', 'google_drive', or 'onedrive').
    """

    translations = {
        'en': {
            'title': 'File source',
            'local': 'Local upload',
            'google_drive': 'Google Drive',
            'onedrive': 'OneDrive',
            'not_connected_warning': 'Not connected. Please connect in Settings first.'
        },
        'vi': {
            'title': 'Nguồn tệp',
            'local': 'Tải lên từ máy',
            'google_drive': 'Google Drive',
            'onedrive': 'OneDrive',
            'not_connected_warning': 'Chưa kết nối. Vui lòng kết nối trong cài đặt trước.'
        }
    }

    t = translations.get(language, translations['en'])

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
