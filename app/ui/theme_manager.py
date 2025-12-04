"""
Theme Manager for dynamic theme switching.

This module handles:
- Theme definitions (Light, Dark)
- System theme detection
- Theme preference storage
- CSS injection for theme switching
"""

import logging
from typing import Dict, Optional
import streamlit as st

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    Manages application themes and dynamic switching.

    Supports Light, Dark, and System (auto-detect) themes.
    """

    # Theme definitions with CSS variables
    THEMES = {
        'light': {
            'name': 'Light',
            'css_vars': {
                '--background-color': '#FFFFFF',
                '--secondary-background': '#F0F2F6',
                '--text-color': '#262730',
                '--secondary-text': '#6C757D',
                '--primary-color': '#FF4B4B',
                '--border-color': '#E0E0E0',
                '--success-color': '#28A745',
                '--warning-color': '#FFC107',
                '--error-color': '#DC3545',
                '--info-color': '#17A2B8',
                '--card-background': '#FFFFFF',
                '--card-border': '#E0E0E0',
                '--input-background': '#FFFFFF',
                '--input-border': '#CED4DA',
                '--button-background': '#FF4B4B',
                '--button-text': '#FFFFFF',
                '--sidebar-background': '#F0F2F6',
                '--code-background': '#F8F9FA',
                '--link-color': '#0066CC'
            }
        },
        'dark': {
            'name': 'Dark',
            'css_vars': {
                '--background-color': '#0E1117',
                '--secondary-background': '#262730',
                '--text-color': '#FAFAFA',
                '--secondary-text': '#A0A0A0',
                '--primary-color': '#FF4B4B',
                '--border-color': '#3A3A3A',
                '--success-color': '#28A745',
                '--warning-color': '#FFC107',
                '--error-color': '#DC3545',
                '--info-color': '#17A2B8',
                '--card-background': '#1E1E1E',
                '--card-border': '#3A3A3A',
                '--input-background': '#262730',
                '--input-border': '#3A3A3A',
                '--button-background': '#FF4B4B',
                '--button-text': '#FFFFFF',
                '--sidebar-background': '#262730',
                '--code-background': '#1E1E1E',
                '--link-color': '#4A9EFF'
            }
        }
    }

    def __init__(self, settings_manager, user_id: str):
        """
        Initialize Theme Manager.

        Args:
            settings_manager: SettingsManager instance.
            user_id: Current user ID.
        """
        self.settings_manager = settings_manager
        self.user_id = user_id

    def get_current_theme(self) -> str:
        """
        Get current active theme name.

        Returns:
            Theme name ('light' or 'dark').
        """
        # Get user preference
        preference = self.settings_manager.get_theme_preference(self.user_id)

        if preference == 'system':
            # Detect system theme
            return self._detect_system_theme()
        else:
            return preference or 'light'

    def _detect_system_theme(self) -> str:
        """
        Detect operating system theme preference.

        Returns:
            'light' or 'dark' based on system settings.
        """
        try:
            import darkdetect

            system_theme = darkdetect.theme()  # Returns 'Dark' or 'Light'

            if system_theme:
                theme = system_theme.lower()
                logger.info(f"System theme detected: {theme}")
                return theme
            else:
                logger.warning("Could not detect system theme, defaulting to light")
                return 'light'

        except ImportError:
            logger.warning("darkdetect not installed, defaulting to light theme")
            return 'light'
        except Exception as e:
            logger.error(f"Error detecting system theme: {e}")
            return 'light'

    def set_theme_preference(self, preference: str) -> bool:
        """
        Set user theme preference.

        Args:
            preference: Theme preference ('light', 'dark', or 'system').

        Returns:
            bool: True if successful, False otherwise.
        """
        if preference not in ['light', 'dark', 'system']:
            logger.warning(f"Invalid theme preference: {preference}")
            return False

        success = self.settings_manager.save_theme_preference(self.user_id, preference)

        if success:
            logger.info(f"Theme preference set to: {preference}")

        return success

    def get_theme_css(self, theme_name: str) -> str:
        """
        Generate CSS for specified theme.

        Args:
            theme_name: Theme name ('light' or 'dark').

        Returns:
            CSS string with theme variables and styles.
        """
        if theme_name not in self.THEMES:
            logger.warning(f"Unknown theme: {theme_name}, using light")
            theme_name = 'light'

        theme = self.THEMES[theme_name]
        css_vars = theme['css_vars']

        # Build CSS variables
        css_vars_str = '\n'.join([
            f'    {key}: {value};'
            for key, value in css_vars.items()
        ])

        # Complete CSS with theme-specific styles
        css = f"""
        <style>
        /* Theme: {theme['name']} */
        :root {{
{css_vars_str}
        }}

        /* Global Styles */
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}

        /* Sidebar */
        .css-1d391kg, [data-testid="stSidebar"] {{
            background-color: var(--sidebar-background);
        }}

        .css-1d391kg .element-container, [data-testid="stSidebar"] .element-container {{
            color: var(--text-color);
        }}

        /* Cards and Containers */
        .stAlert, .stExpander, .stTabs {{
            background-color: var(--card-background);
            border: 1px solid var(--card-border);
            color: var(--text-color);
        }}

        /* Inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {{
            background-color: var(--input-background);
            border-color: var(--input-border);
            color: var(--text-color);
        }}

        /* Buttons */
        .stButton > button {{
            background-color: var(--button-background);
            color: var(--button-text);
            border: none;
        }}

        .stButton > button:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
        }}

        /* Primary button */
        .stButton > button[kind="primary"] {{
            background-color: var(--primary-color);
        }}

        /* Secondary button */
        .stButton > button[kind="secondary"] {{
            background-color: var(--secondary-background);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }}

        /* Links */
        a {{
            color: var(--link-color);
        }}

        /* Code blocks */
        code, pre {{
            background-color: var(--code-background);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }}

        /* Metrics */
        .stMetric {{
            background-color: var(--card-background);
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid var(--card-border);
        }}

        .stMetric label {{
            color: var(--secondary-text);
        }}

        .stMetric [data-testid="stMetricValue"] {{
            color: var(--text-color);
        }}

        /* Dataframes and Tables */
        .stDataFrame, .stTable {{
            background-color: var(--card-background);
            color: var(--text-color);
        }}

        /* Progress bar */
        .stProgress > div > div > div {{
            background-color: var(--primary-color);
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: var(--secondary-background);
            color: var(--text-color);
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: var(--card-background);
            border-bottom: 2px solid var(--primary-color);
        }}

        /* File uploader */
        .stFileUploader {{
            background-color: var(--card-background);
            border: 2px dashed var(--border-color);
            border-radius: 0.5rem;
        }}

        /* Radio buttons */
        .stRadio > div {{
            background-color: var(--card-background);
            padding: 0.5rem;
            border-radius: 0.5rem;
        }}

        /* Checkboxes */
        .stCheckbox > label {{
            color: var(--text-color);
        }}

        /* Divider */
        hr {{
            border-color: var(--border-color);
        }}

        /* Tooltips */
        .stTooltipIcon {{
            color: var(--secondary-text);
        }}

        /* Success, Warning, Error, Info messages */
        .stSuccess {{
            background-color: var(--success-color);
            color: white;
        }}

        .stWarning {{
            background-color: var(--warning-color);
            color: #212529;
        }}

        .stError {{
            background-color: var(--error-color);
            color: white;
        }}

        .stInfo {{
            background-color: var(--info-color);
            color: white;
        }}

        /* Markdown headers */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color);
        }}

        /* Paragraph text */
        p {{
            color: var(--text-color);
        }}

        /* Caption text */
        .stCaption {{
            color: var(--secondary-text);
        }}

        /* Custom scrollbar (for webkit browsers) */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--secondary-background);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-color);
        }}
        </style>
        """

        return css

    def apply_theme(self) -> None:
        """
        Apply current theme by injecting CSS.

        Gets current theme preference and injects appropriate CSS.
        """
        current_theme = self.get_current_theme()
        css = self.get_theme_css(current_theme)

        # Inject CSS
        st.markdown(css, unsafe_allow_html=True)

        logger.debug(f"Applied theme: {current_theme}")

    def get_available_themes(self) -> Dict[str, str]:
        """
        Get list of available themes.

        Returns:
            Dictionary of theme_id: theme_name.
        """
        themes = {
            'light': 'Light',
            'dark': 'Dark',
            'system': 'System (Auto)'
        }

        return themes
