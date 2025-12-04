"""
Theme Selector UI Component.

This module provides UI for theme selection and switching.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def render_theme_selector(theme_manager, language: str = 'en'):
    """
    Render theme selector UI.

    Args:
        theme_manager: ThemeManager instance.
        language: UI language ('en' or 'vi').
    """

    # Translations
    translations = {
        'en': {
            'title': '🎨 Theme',
            'subtitle': 'Choose your preferred theme',
            'light': 'Light',
            'dark': 'Dark',
            'system': 'System (Auto)',
            'current_theme': 'Current theme',
            'system_detected': 'System detected',
            'apply_success': 'Theme applied successfully!',
            'description': {
                'light': 'Bright theme with light colors',
                'dark': 'Dark theme for low-light environments',
                'system': 'Automatically match your system theme'
            }
        },
        'vi': {
            'title': '🎨 Giao diện',
            'subtitle': 'Chọn giao diện ưa thích',
            'light': 'Sáng',
            'dark': 'Tối',
            'system': 'Hệ thống (Tự động)',
            'current_theme': 'Giao diện hiện tại',
            'system_detected': 'Hệ thống phát hiện',
            'apply_success': 'Đã áp dụng giao diện thành công!',
            'description': {
                'light': 'Giao diện sáng với màu sáng',
                'dark': 'Giao diện tối cho môi trường thiếu sáng',
                'system': 'Tự động theo giao diện hệ thống'
            }
        }
    }

    t = translations.get(language, translations['en'])

    # Section header
    st.markdown(f"### {t['title']}")
    st.caption(t['subtitle'])

    # Get current preference and actual theme
    current_preference = theme_manager.settings_manager.get_theme_preference(theme_manager.user_id) or 'system'
    actual_theme = theme_manager.get_current_theme()

    # Theme options
    theme_options = {
        'light': t['light'],
        'dark': t['dark'],
        'system': t['system']
    }

    # Create columns for theme cards
    col1, col2, col3 = st.columns(3)

    columns = [col1, col2, col3]
    theme_keys = ['light', 'dark', 'system']

    for col, theme_key in zip(columns, theme_keys):
        with col:
            # Check if this is the current preference
            is_selected = (current_preference == theme_key)

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
                    <h4 style="margin: 0;">{theme_options[theme_key]}</h4>
                    <p style="font-size: 0.8rem; margin: 0.5rem 0;">✓ {t['current_theme']}</p>
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
                    <h4 style="margin: 0;">{theme_options[theme_key]}</h4>
                    <p style="font-size: 0.8rem; margin: 0.5rem 0; color: #888;">{t['description'][theme_key]}</p>
                </div>
                """, unsafe_allow_html=True)

            # Button to select theme
            if st.button(
                f"Select {theme_options[theme_key]}" if not is_selected else f"✓ {theme_options[theme_key]}",
                key=f'theme_btn_{theme_key}',
                use_container_width=True,
                disabled=is_selected
            ):
                # Set theme preference
                success = theme_manager.set_theme_preference(theme_key)

                if success:
                    st.success(t['apply_success'])
                    st.rerun()
                else:
                    st.error("Failed to save theme preference")

    # Show detected system theme if system mode
    if current_preference == 'system':
        st.info(f"🖥️ {t['system_detected']}: **{actual_theme.capitalize()}**")

    st.markdown("---")

    # Theme preview (optional)
    with st.expander("🎨 Theme Preview"):
        _render_theme_preview(actual_theme, t)


def _render_theme_preview(theme_name: str, translations: dict):
    """
    Render a preview of the current theme.

    Args:
        theme_name: Current theme name.
        translations: Translation dictionary.
    """

    st.markdown(f"**Preview: {theme_name.capitalize()} Theme**")

    # Sample elements
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Sample Metric", "42", "+5")
        st.button("Sample Button", key='preview_btn')

    with col2:
        st.info("Sample Info Message")
        st.success("Sample Success Message")

    st.warning("Sample Warning Message")
    st.error("Sample Error Message")

    st.code("print('Sample code block')", language='python')

    st.caption("Sample caption text")


def render_compact_theme_selector(theme_manager, language: str = 'en'):
    """
    Render compact theme selector for sidebar.

    Args:
        theme_manager: ThemeManager instance.
        language: UI language ('en' or 'vi').
    """

    # Translations
    translations = {
        'en': {
            'theme': 'Theme',
            'light': 'Light',
            'dark': 'Dark',
            'system': 'System'
        },
        'vi': {
            'theme': 'Giao diện',
            'light': 'Sáng',
            'dark': 'Tối',
            'system': 'Hệ thống'
        }
    }

    t = translations.get(language, translations['en'])

    # Get current preference
    current_preference = theme_manager.settings_manager.get_theme_preference(theme_manager.user_id) or 'system'

    # Compact selector
    st.markdown(f"**{t['theme']}**")

    theme_options = [t['light'], t['dark'], t['system']]
    theme_keys = ['light', 'dark', 'system']

    # Map current preference to index
    current_index = theme_keys.index(current_preference) if current_preference in theme_keys else 2

    # Radio buttons
    selected = st.radio(
        t['theme'],
        options=theme_options,
        index=current_index,
        horizontal=True,
        label_visibility='collapsed',
        key='compact_theme_selector'
    )

    # Map selection back to theme key
    selected_index = theme_options.index(selected)
    selected_theme = theme_keys[selected_index]

    # Update if changed
    if selected_theme != current_preference:
        success = theme_manager.set_theme_preference(selected_theme)

        if success:
            st.rerun()
