"""
Internationalization (i18n) modules.

This package contains:
- translator.py: Translation service for multi-language support
"""

from .translator import Translator, get_translator, t

__version__ = "1.0.0"
__all__ = ['Translator', 'get_translator', 't']
