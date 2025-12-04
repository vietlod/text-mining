"""
Translator for Multi-language Support.

This module provides i18n (internationalization) functionality for the application.
Supports dynamic language switching with translations loaded from JSON files.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Translator:
    """
    Manages translations and provides i18n functionality.

    Supports:
    - Loading translations from JSON files
    - Nested key access (e.g., 'sidebar.upload_files')
    - Parameter formatting (e.g., 'welcome {name}')
    - Fallback to English if translation missing
    """

    # Cache for loaded translations
    _translations_cache: Dict[str, Dict[str, Any]] = {}

    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'vi': 'Tiếng Việt'
    }

    def __init__(self, language: str = 'en', locales_dir: Optional[str] = None):
        """
        Initialize Translator.

        Args:
            language: Language code ('en' or 'vi').
            locales_dir: Directory containing translation JSON files.
                        If None, uses default 'locales/' directory.
        """
        self.language = language if language in self.SUPPORTED_LANGUAGES else 'en'
        self.locales_dir = locales_dir or self._get_default_locales_dir()

        # Load translations
        self.translations = self._load_translations(self.language)

        # Load English as fallback
        if self.language != 'en':
            self.fallback_translations = self._load_translations('en')
        else:
            self.fallback_translations = self.translations

    def _get_default_locales_dir(self) -> str:
        """Get default locales directory path."""
        # Get path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        locales_dir = os.path.join(project_root, 'locales')

        return locales_dir

    def _load_translations(self, language: str) -> Dict[str, Any]:
        """
        Load translations from JSON file.

        Args:
            language: Language code to load.

        Returns:
            Dictionary with translations.
        """
        # Check cache first
        if language in self._translations_cache:
            logger.debug(f"Using cached translations for {language}")
            return self._translations_cache[language]

        # Load from file
        file_path = os.path.join(self.locales_dir, f'{language}.json')

        try:
            if not os.path.exists(file_path):
                logger.warning(f"Translation file not found: {file_path}")
                return {}

            with open(file_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)

            # Cache the loaded translations
            self._translations_cache[language] = translations

            logger.info(f"Loaded translations for {language} from {file_path}")
            return translations

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in translation file {file_path}: {e}")
            return {}

        except Exception as e:
            logger.error(f"Failed to load translations for {language}: {e}")
            return {}

    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key to current language.

        Supports nested keys using dot notation:
        - 'sidebar.upload_files' -> translations['sidebar']['upload_files']

        Supports parameter formatting:
        - t('welcome', name='John') -> 'Welcome, John!'

        Args:
            key: Translation key (supports dot notation for nesting).
            **kwargs: Parameters for string formatting.

        Returns:
            Translated string. Returns key itself if translation not found.
        """
        # Split nested keys
        keys = key.split('.')

        # Try to get translation from current language
        value = self._get_nested_value(self.translations, keys)

        # Fallback to English if not found
        if value is None:
            value = self._get_nested_value(self.fallback_translations, keys)

            if value is None:
                logger.warning(f"Translation not found for key: {key}")
                return key  # Return the key itself as fallback

        # Format with parameters if provided
        if kwargs:
            try:
                return value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing parameter {e} for key: {key}")
                return value
            except Exception as e:
                logger.error(f"Error formatting translation for key {key}: {e}")
                return value

        return value

    def _get_nested_value(self, data: Dict[str, Any], keys: list) -> Optional[str]:
        """
        Get nested value from dictionary using list of keys.

        Args:
            data: Dictionary to search in.
            keys: List of keys for nested access.

        Returns:
            Value if found, None otherwise.
        """
        try:
            value = data
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return None

            return value if isinstance(value, str) else None

        except Exception as e:
            logger.debug(f"Error getting nested value for keys {keys}: {e}")
            return None

    def switch_language(self, language: str) -> bool:
        """
        Switch to a different language.

        Args:
            language: Language code to switch to.

        Returns:
            bool: True if successful, False otherwise.
        """
        if language not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language: {language}")
            return False

        self.language = language
        self.translations = self._load_translations(language)

        # Update fallback if needed
        if language != 'en':
            self.fallback_translations = self._load_translations('en')
        else:
            self.fallback_translations = self.translations

        logger.info(f"Switched language to: {language}")
        return True

    def get_current_language(self) -> str:
        """
        Get current language code.

        Returns:
            Language code ('en' or 'vi').
        """
        return self.language

    def get_language_name(self, language: Optional[str] = None) -> str:
        """
        Get human-readable language name.

        Args:
            language: Language code. If None, uses current language.

        Returns:
            Language name (e.g., 'English', 'Tiếng Việt').
        """
        lang = language or self.language
        return self.SUPPORTED_LANGUAGES.get(lang, lang)

    def get_available_languages(self) -> Dict[str, str]:
        """
        Get dictionary of available languages.

        Returns:
            Dictionary of {code: name} for all supported languages.
        """
        return self.SUPPORTED_LANGUAGES.copy()

    @staticmethod
    def clear_cache():
        """Clear the translations cache."""
        Translator._translations_cache.clear()
        logger.info("Cleared translations cache")


# Convenience function for global translator instance
_global_translator: Optional[Translator] = None


def get_translator(language: str = 'en') -> Translator:
    """
    Get or create global Translator instance.

    Args:
        language: Language code.

    Returns:
        Translator instance.
    """
    global _global_translator

    if _global_translator is None or _global_translator.language != language:
        _global_translator = Translator(language)

    return _global_translator


def t(key: str, language: str = 'en', **kwargs) -> str:
    """
    Quick translation function.

    Args:
        key: Translation key.
        language: Language code.
        **kwargs: Parameters for formatting.

    Returns:
        Translated string.
    """
    translator = get_translator(language)
    return translator.t(key, **kwargs)
