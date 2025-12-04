# Multi-language Support Guide

This guide explains how to use and extend the multi-language support feature in the Text-mining Research Tool.

## Overview

The application supports multiple languages (currently English and Vietnamese) with:
- Dynamic language switching
- Per-user language preferences
- Automatic persistence across sessions
- Easy-to-extend translation system

## Features

### 1. Language Selection

Users can choose their preferred language from:
- **English (🇬🇧)**
- **Tiếng Việt (🇻🇳)** - Uses Sentence case formatting

Language preference is saved per user and persists across sessions.

### 2. Translation System

The translation system is built on:
- **JSON-based translations**: Easy to read and edit
- **Nested key support**: Organize translations hierarchically
- **Parameter formatting**: Support for dynamic values
- **Fallback mechanism**: Falls back to English if translation missing

## User Guide

### How to Change Language

1. **Open Settings**
   - Click on the "⚙️ Settings" expander in the left sidebar

2. **Select Language**
   - Find the "Language" section
   - Click on your preferred language (English or Tiếng Việt)
   - The interface will immediately switch to the selected language

3. **Automatic Saving**
   - Your language preference is automatically saved
   - The app will use your preferred language next time you log in

## Developer Guide

### File Structure

```
TEXT-MINING/
├── app/
│   └── i18n/
│       ├── __init__.py
│       └── translator.py          # Translation service
├── locales/
│   ├── en.json                    # English translations
│   └── vi.json                    # Vietnamese translations
└── ui/
    └── components/
        └── language_selector.py   # Language selector UI
```

### Using Translations in Code

#### 1. Initialize Translator

```python
from app.i18n.translator import Translator

# Get user's language preference
language = settings_manager.get_language_preference(user_id) or 'en'

# Initialize translator
translator = Translator(language)
```

#### 2. Translate Text

```python
# Simple translation
title = translator.t('settings.title')

# Nested key access
welcome_msg = translator.t('auth.welcome')

# With parameters
greeting = translator.t('common.welcome_user', name=user_name)
```

#### 3. In Streamlit Components

```python
# Use translator in UI
st.markdown(f"### {translator.t('settings.configuration_input')}")
st.info(translator.t('keywords.loaded'))

# In buttons
if st.button(translator.t('buttons.save')):
    # Save action
    pass
```

### Adding New Translations

#### 1. Add to English (en.json)

```json
{
  "new_feature": {
    "title": "New Feature",
    "description": "This is a new feature",
    "action_button": "Click Here"
  }
}
```

#### 2. Add to Vietnamese (vi.json)

```json
{
  "new_feature": {
    "title": "Tính năng mới",
    "description": "Đây là tính năng mới",
    "action_button": "Nhấn vào đây"
  }
}
```

**Vietnamese Translation Guidelines:**
- Use Sentence case (not Title Case)
- First word capitalized, rest lowercase
- Example: "Tính năng mới" ✅ (not "Tính Năng Mới" ❌)

#### 3. Use in Code

```python
# Access nested keys with dot notation
st.markdown(f"## {translator.t('new_feature.title')}")
st.write(translator.t('new_feature.description'))
if st.button(translator.t('new_feature.action_button')):
    # Action
    pass
```

### Translation Key Organization

The translation keys are organized by feature/section:

```
app_title                      # Application title
app_subtitle                   # Application subtitle

auth.*                         # Authentication related
sidebar.*                      # Sidebar elements
settings.*                     # Settings page
keywords.*                     # Keyword management
cloud.*                        # Cloud storage
theme.*                        # Theme options
language.*                     # Language options
processing.*                   # Processing status messages
results.*                      # Results display
extraction_modes.*             # Extraction mode descriptions
common.*                       # Common UI elements
messages.*                     # Status messages
buttons.*                      # Button labels
```

### Adding a New Language

To add support for a new language (e.g., Spanish):

#### 1. Create Translation File

Create `locales/es.json` with all translations:

```json
{
  "app_title": "Herramienta de investigación de minería de texto",
  "app_subtitle": "Análisis avanzado de documentos",
  "auth": {
    "welcome": "¡Bienvenido! Por favor inicie sesión para continuar",
    ...
  },
  ...
}
```

#### 2. Update Translator

Edit `app/i18n/translator.py`:

```python
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'vi': 'Tiếng Việt',
    'es': 'Español'  # Add new language
}
```

#### 3. Add Flag Emoji

Edit `ui/components/language_selector.py`:

```python
def get_language_flag(language: str) -> str:
    flags = {
        'en': '🇬🇧',
        'vi': '🇻🇳',
        'es': '🇪🇸'  # Add flag
    }
    return flags.get(language, '🌐')
```

#### 4. Test

Test all UI elements with the new language to ensure proper translations.

## API Reference

### Translator Class

```python
class Translator:
    def __init__(self, language: str = 'en', locales_dir: Optional[str] = None)
    def t(self, key: str, **kwargs) -> str
    def switch_language(self, language: str) -> bool
    def get_current_language(self) -> str
    def get_language_name(self, language: Optional[str] = None) -> str
    def get_available_languages(self) -> Dict[str, str]

    @staticmethod
    def clear_cache()
```

### Helper Functions

```python
# Get global translator instance
translator = get_translator(language='en')

# Quick translation
text = t(key='settings.title', language='en')
```

## Translation Best Practices

### 1. Key Naming

- Use lowercase with underscores: `api_key_title`
- Use dots for nesting: `settings.api_key_title`
- Be descriptive: `cloud.connect_first` (not `cloud.msg1`)

### 2. Text Content

- Keep translations concise for UI elements
- Maintain consistent terminology across the app
- Use proper punctuation and capitalization

### 3. Parameters

- Use named parameters for clarity:
  ```json
  "welcome_user": "Welcome, {name}!"
  ```

- Use in code:
  ```python
  translator.t('welcome_user', name=user['name'])
  ```

### 4. Fallback

- Always provide English translation
- English is used as fallback for missing translations
- Return the key itself if not found in any language

## Testing

### Test Language Switching

1. Log in to the application
2. Open Settings
3. Switch between English and Vietnamese
4. Verify:
   - UI elements update immediately
   - Preference is saved
   - Language persists after refresh
   - All text is properly translated

### Test Missing Translations

1. Add a new key to English only
2. Switch to Vietnamese
3. Verify fallback to English works
4. Check logs for warning about missing translation

## Troubleshooting

### Issue: Translations Not Loading

**Possible Causes:**
- Invalid JSON syntax in translation files
- Missing translation files
- Incorrect file path

**Solution:**
```python
# Check translator initialization logs
import logging
logging.basicConfig(level=logging.DEBUG)

translator = Translator('vi')
# Check logs for loading errors
```

### Issue: Language Not Persisting

**Possible Causes:**
- User not authenticated
- Firestore connection issue
- Settings not being saved

**Solution:**
```python
# Verify save operation
success = settings_manager.save_language_preference(user_id, 'vi')
if not success:
    # Check Firestore connection
    # Check user_id validity
```

### Issue: Missing Translation Warning

**Possible Causes:**
- Translation key not added to target language
- Typo in translation key
- Nested key structure mismatch

**Solution:**
1. Check the key exists in JSON files
2. Verify nested structure matches between languages
3. Add missing translation
4. Clear translation cache if needed:
   ```python
   Translator.clear_cache()
   ```

## Performance Considerations

### Caching

- Translations are cached after first load
- Cache is shared across all Translator instances
- Clear cache with `Translator.clear_cache()` if needed

### Best Practices

- Initialize Translator once per session
- Reuse the same instance for multiple translations
- Avoid creating new Translator for each translation

```python
# Good ✅
translator = Translator(language)
title = translator.t('settings.title')
subtitle = translator.t('settings.subtitle')

# Bad ❌
title = Translator(language).t('settings.title')
subtitle = Translator(language).t('settings.subtitle')
```

## Future Enhancements

Potential improvements to the language system:

1. **Dynamic Translation Loading**: Load translations from database
2. **Translation Editor**: Admin UI to edit translations
3. **Crowdsourced Translations**: Allow users to contribute translations
4. **Context-aware Translations**: Different translations based on context
5. **Pluralization Support**: Handle singular/plural forms
6. **Date/Time Formatting**: Locale-specific formatting
7. **RTL Language Support**: Right-to-left language support

## Support

For issues or questions about the language system:

1. Check this guide first
2. Review the translation JSON files
3. Check application logs for errors
4. Refer to the implementation in `app/i18n/translator.py`

---

**Last Updated:** Session 6 Implementation
**Version:** 1.0.0
