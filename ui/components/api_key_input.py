"""
API Key Input UI Component.

This module provides UI for users to configure their Gemini API key.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def validate_gemini_api_key(api_key: str) -> tuple[bool, str]:
    """
    Validate Gemini API key by making a test request.

    Args:
        api_key: Gemini API key to validate.

    Returns:
        Tuple of (is_valid, message).
    """
    try:
        import google.generativeai as genai

        # Configure with test key
        genai.configure(api_key=api_key)

        # Try to list models (lightweight check)
        models = genai.list_models()
        model_list = list(models)

        if model_list:
            logger.info(f"API key validated successfully. Found {len(model_list)} models.")
            return True, f"✅ Valid! Found {len(model_list)} available models."
        else:
            return False, "❌ API key appears invalid. No models found."

    except Exception as e:
        error_msg = str(e)
        logger.error(f"API key validation error: {error_msg}")

        # Provide helpful error messages
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            return False, "❌ Invalid API key. Please check and try again."
        elif "quota" in error_msg.lower():
            return False, "⚠️ API key valid but quota exceeded."
        elif "permission" in error_msg.lower():
            return False, "⚠️ API key valid but permissions insufficient."
        else:
            return False, f"❌ Validation failed: {error_msg[:100]}"


def render_api_key_input(settings_manager, user_id: str):
    """
    Render API key configuration UI.

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
    """

    # Vietnamese translations (hardcoded)
    t = {
            'title': '🔑 Google Gemini API Configuration',
            'subtitle': 'Configure your personal Gemini API key',
            'configured': 'API key configured',
            'not_configured': 'No API key configured',
            'show_key': 'Show API key',
            'hide_key': 'Hide API key',
            'input_label': 'Gemini API Key',
            'input_help': 'Enter your Google Gemini API key',
            'caption': "💡 Don't have an API key?",
            'get_key_link': 'Get your free API key here',
            'save_button': '💾 Save API Key',
            'delete_button': '🗑️ Delete API Key',
            'validating': 'Validating API key...',
            'save_success': 'API key saved successfully!',
            'save_error': 'Failed to save API key. Please try again.',
            'delete_confirm': 'Are you sure you want to delete your API key?',
            'delete_success': 'API key deleted successfully!',
            'delete_error': 'Failed to delete API key.',
            'enter_key_warning': 'Please enter an API key',
            'instructions_title': '📖 How to get your API key',
            'instructions': '''
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Paste it in the field above

**Free tier includes:**
- 15 requests per minute
- 1 million tokens per day
- Sufficient for personal use
            ''',
            'security_note': '🔒 Khóa API của bạn được mã hóa và lưu trữ an toàn trong hồ sơ người dùng.'
        }

    # Section header
    st.markdown(f"### {t['title']}")
    st.caption(t['subtitle'])

    # Check if API key exists
    existing_key = settings_manager.get_api_key(user_id)
    has_key = existing_key is not None

    # Status indicator
    if has_key:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ {t['configured']}")
        with col2:
            # Show/hide key toggle
            if 'show_api_key' not in st.session_state:
                st.session_state.show_api_key = False

            if st.button(
                t['hide_key'] if st.session_state.show_api_key else t['show_key'],
                key='toggle_show_key'
            ):
                st.session_state.show_api_key = not st.session_state.show_api_key

        # Display key if toggled
        if st.session_state.show_api_key and existing_key:
            st.code(existing_key, language=None)
    else:
        st.info(f"ℹ️ {t['not_configured']}")

    st.markdown("---")

    # API Key input
    api_key_input = st.text_input(
        t['input_label'],
        value=existing_key if has_key and st.session_state.get('show_api_key', False) else "",
        type="password" if not st.session_state.get('show_api_key', False) else "default",
        help=t['input_help'],
        key='api_key_input_field'
    )

    # Caption with link
    st.caption(
        f"{t['caption']} "
        f"[{t['get_key_link']}](https://aistudio.google.com/app/apikey)"
    )

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        # Save button
        if st.button(t['save_button'], type="primary", use_container_width=True):
            if api_key_input and api_key_input.strip():
                # Validate API key
                with st.spinner(t['validating']):
                    is_valid, message = validate_gemini_api_key(api_key_input.strip())

                if is_valid:
                    # Save API key
                    success = settings_manager.save_api_key(user_id, api_key_input.strip())

                    if success:
                        st.success(t['save_success'])
                        st.balloons()
                        # Update session state
                        st.session_state['user_api_key'] = api_key_input.strip()
                        st.rerun()
                    else:
                        st.error(t['save_error'])
                else:
                    # Show validation error
                    st.error(message)
            else:
                st.warning(t['enter_key_warning'])

    with col2:
        # Delete button (only if key exists)
        if has_key:
            if st.button(t['delete_button'], use_container_width=True):
                # Confirm deletion
                if st.session_state.get('confirm_delete_api_key', False):
                    success = settings_manager.delete_api_key(user_id)

                    if success:
                        st.success(t['delete_success'])
                        # Clear session state
                        if 'user_api_key' in st.session_state:
                            del st.session_state['user_api_key']
                        st.session_state.confirm_delete_api_key = False
                        st.rerun()
                    else:
                        st.error(t['delete_error'])
                else:
                    st.session_state.confirm_delete_api_key = True
                    st.warning(t['delete_confirm'])
                    st.rerun()

    # Reset confirmation state if not deleting
    if 'confirm_delete_api_key' in st.session_state and not has_key:
        st.session_state.confirm_delete_api_key = False

    # Instructions expander
    with st.expander(t['instructions_title']):
        st.markdown(t['instructions'])

    # Security note
    st.caption(t['security_note'])

    return has_key
