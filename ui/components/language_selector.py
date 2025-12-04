"""
Language Selector UI Component.

This module provides UI for language selection and switching.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def render_language_selector(settings_manager, user_id: str, translator, compact: bool = False):
    """
    Render language selector UI.

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        translator: Translator instance.
        compact: If True, render compact version. If False, render full version.
    """
    if compact:
        _render_compact_language_selector(settings_manager, user_id, translator)
    else:
        _render_full_language_selector(settings_manager, user_id, translator)


def _render_full_language_selector(settings_manager, user_id: str, translator):
    """
    Render full language selector with cards.

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        translator: Translator instance.
    """
    # Get current language
    current_language = translator.get_current_language()

    # Section header
    st.markdown(f"### {translator.t('settings.language.title')}")
    st.caption(translator.t('settings.language.subtitle'))

    # Language options
    available_languages = translator.get_available_languages()

    # Create columns for language cards
    cols = st.columns(len(available_languages))

    for col, (lang_code, lang_name) in zip(cols, available_languages.items()):
        with col:
            # Check if this is the current language
            is_selected = (current_language == lang_code)

            # Card styling
            if is_selected:
                st.markdown(f"""
                <div style="
                    padding: 1rem;
                    border: 2px solid #FF4B4B;
                    border-radius: 0.5rem;
                    background-color: rgba(255, 75, 75, 0.1);
                    text-align: center;
                    cursor: pointer;
                ">
                    <h4 style="margin: 0;">{lang_name}</h4>
                    <p style="font-size: 0.8rem; margin: 0.5rem 0;">✓ {translator.t('settings.language.current')}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    padding: 1rem;
                    border: 1px solid #E0E0E0;
                    border-radius: 0.5rem;
                    text-align: center;
                    cursor: pointer;
                ">
                    <h4 style="margin: 0;">{lang_name}</h4>
                    <p style="font-size: 0.8rem; margin: 0.5rem 0; color: #888;">{translator.t('settings.language.select_this')}</p>
                </div>
                """, unsafe_allow_html=True)

            # Button to select language
            button_text = f"✓ {lang_name}" if is_selected else lang_name

            if st.button(
                button_text,
                key=f'lang_btn_{lang_code}',
                use_container_width=True,
                disabled=is_selected
            ):
                # Save language preference
                success = settings_manager.save_language_preference(user_id, lang_code)

                if success:
                    # Update translator
                    translator.switch_language(lang_code)

                    # Update session state
                    st.session_state['language'] = lang_code

                    st.success(translator.t('settings.language.apply_success'))
                    st.rerun()
                else:
                    st.error("Failed to save language preference")

    st.markdown("---")

    # Language preview (optional)
    with st.expander(f"🌐 {translator.t('settings.language.preview_title')}"):
        _render_language_preview(translator)


def _render_compact_language_selector(settings_manager, user_id: str, translator):
    """
    Render compact language selector for sidebar.

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        translator: Translator instance.
    """
    # Get current language
    current_language = translator.get_current_language()

    # Get available languages
    available_languages = translator.get_available_languages()

    # Compact selector
    st.markdown(f"**{translator.t('settings.language.language')}**")

    # Create language options list
    language_options = list(available_languages.values())
    language_codes = list(available_languages.keys())

    # Map current language to index
    current_index = language_codes.index(current_language) if current_language in language_codes else 0

    # Radio buttons
    selected = st.radio(
        translator.t('settings.language.language'),
        options=language_options,
        index=current_index,
        horizontal=True,
        label_visibility='collapsed',
        key='compact_language_selector'
    )

    # Map selection back to language code
    selected_index = language_options.index(selected)
    selected_language = language_codes[selected_index]

    # Update if changed
    if selected_language != current_language:
        success = settings_manager.save_language_preference(user_id, selected_language)

        if success:
            # Update translator
            translator.switch_language(selected_language)

            # Update session state
            st.session_state['language'] = selected_language

            st.rerun()


def _render_language_preview(translator):
    """
    Render a preview of the current language.

    Args:
        translator: Translator instance.
    """
    current_language = translator.get_current_language()
    language_name = translator.get_language_name()

    st.markdown(f"**{translator.t('settings.language.preview_title')}: {language_name}**")

    # Sample translations
    col1, col2 = st.columns(2)

    with col1:
        st.info(translator.t('common.welcome'))
        st.success(translator.t('common.success'))

    with col2:
        st.warning(translator.t('common.warning'))
        st.error(translator.t('common.error'))

    st.caption(translator.t('settings.language.preview_desc'))


def get_language_flag(language: str) -> str:
    """
    Get emoji flag for language.

    Args:
        language: Language code.

    Returns:
        Emoji flag string.
    """
    flags = {
        'en': '🇬🇧',
        'vi': '🇻🇳'
    }

    return flags.get(language, '🌐')


def render_language_switcher_button(settings_manager, user_id: str, translator):
    """
    Render a compact language switcher button (toggle between languages).

    Args:
        settings_manager: SettingsManager instance.
        user_id: Current user ID.
        translator: Translator instance.
    """
    current_language = translator.get_current_language()
    available_languages = translator.get_available_languages()

    # Get next language in cycle
    language_codes = list(available_languages.keys())
    current_index = language_codes.index(current_language)
    next_index = (current_index + 1) % len(language_codes)
    next_language = language_codes[next_index]
    next_language_name = available_languages[next_language]

    # Flag for current language
    flag = get_language_flag(current_language)

    # Button to switch
    if st.button(
        f"{flag} {translator.get_language_name()}",
        key='language_switcher_btn',
        help=f"Switch to {next_language_name}"
    ):
        # Save language preference
        success = settings_manager.save_language_preference(user_id, next_language)

        if success:
            # Update translator
            translator.switch_language(next_language)

            # Update session state
            st.session_state['language'] = next_language

            st.rerun()
