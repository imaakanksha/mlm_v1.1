"""
Multilingual Mandi - Translation Service
=========================================
AI-powered translation service using Google Gemini API.
Supports 10 Indian languages with caching for efficiency.

Languages Supported:
- Hindi (hi), English (en), Tamil (ta), Telugu (te), Bengali (bn)
- Marathi (mr), Gujarati (gu), Kannada (kn), Malayalam (ml), Punjabi (pa)

Author: Hackathon Team
Date: January 2026
"""

import google.generativeai as genai
from typing import Optional, Dict
import hashlib
import os

# Language configuration
SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "en": "English",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi"
}

# Native script labels for UI
LANGUAGE_LABELS = {
    "hi": "हिंदी",
    "en": "English",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "bn": "বাংলা",
    "mr": "मराठी",
    "gu": "ગુજરાતી",
    "kn": "ಕನ್ನಡ",
    "ml": "മലയാളം",
    "pa": "ਪੰਜਾਬੀ"
}

# In-memory cache for translations (reduces API calls)
_translation_cache: Dict[str, str] = {}


def _get_cache_key(text: str, source_lang: str, target_lang: str) -> str:
    """
    Generate a unique cache key for a translation request.
    Uses MD5 hash of text + languages for efficient lookup.
    """
    content = f"{text}|{source_lang}|{target_lang}"
    return hashlib.md5(content.encode()).hexdigest()


def _configure_gemini():
    """
    Configure Gemini API with API key from environment.
    Called once on first translation request.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)


# Gemini model instance (initialized lazily)
_model = None


def _get_model():
    """
    Get or create Gemini model instance.
    Uses gemini-pro for text generation.
    """
    global _model
    if _model is None:
        _configure_gemini()
        _model = genai.GenerativeModel('gemini-pro')
    return _model


async def translate_text(
    text: str,
    source_lang: str,
    target_lang: str
) -> dict:
    """
    Translate text from source language to target language.
    
    Args:
        text: The text to translate
        source_lang: Source language code (e.g., 'hi', 'en')
        target_lang: Target language code (e.g., 'ta', 'te')
    
    Returns:
        dict: {
            'translated_text': str,
            'source_lang': str,
            'target_lang': str,
            'cached': bool,
            'success': bool,
            'error': str or None
        }
    
    Example:
        >>> await translate_text("Hello", "en", "hi")
        {'translated_text': 'नमस्ते', 'source_lang': 'en', 'target_lang': 'hi', 'cached': False, 'success': True}
    """
    # Validate languages
    if source_lang not in SUPPORTED_LANGUAGES:
        return {
            'translated_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'cached': False,
            'success': False,
            'error': f"Unsupported source language: {source_lang}"
        }
    
    if target_lang not in SUPPORTED_LANGUAGES:
        return {
            'translated_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'cached': False,
            'success': False,
            'error': f"Unsupported target language: {target_lang}"
        }
    
    # Same language - no translation needed
    if source_lang == target_lang:
        return {
            'translated_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'cached': True,
            'success': True,
            'error': None
        }
    
    # Check cache first
    cache_key = _get_cache_key(text, source_lang, target_lang)
    if cache_key in _translation_cache:
        return {
            'translated_text': _translation_cache[cache_key],
            'source_lang': source_lang,
            'target_lang': target_lang,
            'cached': True,
            'success': True,
            'error': None
        }
    
    # Call Gemini API for translation
    try:
        model = _get_model()
        
        source_name = SUPPORTED_LANGUAGES[source_lang]
        target_name = SUPPORTED_LANGUAGES[target_lang]
        
        # Prompt optimized for Indian language translation
        # WHY: Gemini works better with explicit context and examples
        prompt = f"""Translate the following text from {source_name} to {target_name}.

Important instructions:
1. Provide ONLY the translation, no explanations
2. Preserve the meaning and tone
3. Use natural, conversational language appropriate for local markets
4. Keep numbers and product names as-is when appropriate

Text to translate:
{text}

Translation:"""

        response = model.generate_content(prompt)
        translated = response.text.strip()
        
        # Cache the result
        _translation_cache[cache_key] = translated
        
        return {
            'translated_text': translated,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'cached': False,
            'success': True,
            'error': None
        }
        
    except Exception as e:
        # Graceful degradation - return original text on error
        # WHY: Platform should never crash on API failures
        return {
            'translated_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'cached': False,
            'success': False,
            'error': str(e)
        }


async def detect_language(text: str) -> dict:
    """
    Detect the language of the input text using Gemini.
    
    Args:
        text: The text to analyze
    
    Returns:
        dict: {
            'detected_lang': str (language code),
            'confidence': float (0-1),
            'success': bool
        }
    """
    try:
        model = _get_model()
        
        lang_codes = ", ".join(SUPPORTED_LANGUAGES.keys())
        prompt = f"""Detect the language of the following text.
Respond with ONLY the language code from this list: {lang_codes}

Text: {text}

Language code:"""

        response = model.generate_content(prompt)
        detected = response.text.strip().lower()
        
        # Validate detected language
        if detected in SUPPORTED_LANGUAGES:
            return {
                'detected_lang': detected,
                'confidence': 0.9,  # Gemini doesn't give confidence scores
                'success': True
            }
        else:
            # Default to Hindi if detection fails
            return {
                'detected_lang': 'hi',
                'confidence': 0.5,
                'success': False
            }
            
    except Exception as e:
        return {
            'detected_lang': 'en',  # Default fallback
            'confidence': 0.0,
            'success': False,
            'error': str(e)
        }


def get_supported_languages() -> dict:
    """
    Get list of all supported languages with their native labels.
    
    Returns:
        dict: {code: {'name': str, 'native': str}}
    """
    return {
        code: {
            'name': SUPPORTED_LANGUAGES[code],
            'native': LANGUAGE_LABELS[code]
        }
        for code in SUPPORTED_LANGUAGES
    }


def clear_cache():
    """
    Clear the translation cache.
    Useful for testing or memory management.
    """
    global _translation_cache
    _translation_cache = {}


# TODO: Add batch translation for efficiency
# TODO: Add translation quality scoring
# TODO: Implement persistent cache (Redis/file-based)
