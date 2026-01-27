"""
Multilingual Mandi - Translation Service
=========================================
AI-powered translation service using Google Gemini API (NEW SDK).
Supports 10 Indian languages with caching for efficiency.

Languages Supported:
- Hindi (hi), English (en), Tamil (ta), Telugu (te), Bengali (bn)
- Marathi (mr), Gujarati (gu), Kannada (kn), Malayalam (ml), Punjabi (pa)

Author: Hackathon Team
Date: January 2026
"""

from google import genai
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

# Gemini client (initialized lazily)
_client = None


def _get_cache_key(text: str, source_lang: str, target_lang: str) -> str:
    """Generate a unique cache key for a translation request."""
    content = f"{text}|{source_lang}|{target_lang}"
    return hashlib.md5(content.encode()).hexdigest()


def _get_client():
    """Get or create Gemini client using new SDK."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client


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
        dict with translated_text, source_lang, target_lang, cached, success, error
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
        client = _get_client()
        
        source_name = SUPPORTED_LANGUAGES[source_lang]
        target_name = SUPPORTED_LANGUAGES[target_lang]
        
        # Optimized prompt for Indian language translation
        prompt = f"""You are a professional translator specializing in Indian languages.

Translate the following text from {source_name} to {target_name}.

RULES:
1. Output ONLY the translation, nothing else
2. Preserve the meaning, tone and intent
3. Use natural, conversational language appropriate for local Indian markets
4. Keep numbers, brand names and product names as-is
5. For market/mandi context, use commonly understood terms

Text to translate:
"{text}"

Translation:"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        translated = response.text.strip()
        
        # Remove quotes if present
        if translated.startswith('"') and translated.endswith('"'):
            translated = translated[1:-1]
        
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
        return {
            'translated_text': text,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'cached': False,
            'success': False,
            'error': str(e)
        }


async def detect_language(text: str) -> dict:
    """Detect the language of the input text using Gemini."""
    try:
        client = _get_client()
        
        lang_codes = ", ".join(SUPPORTED_LANGUAGES.keys())
        prompt = f"""Detect the language of the following text.
Respond with ONLY the language code from this list: {lang_codes}

Text: "{text}"

Language code:"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        detected = response.text.strip().lower()
        
        # Validate detected language
        if detected in SUPPORTED_LANGUAGES:
            return {
                'detected_lang': detected,
                'confidence': 0.9,
                'success': True
            }
        else:
            return {
                'detected_lang': 'hi',
                'confidence': 0.5,
                'success': False
            }
            
    except Exception as e:
        return {
            'detected_lang': 'en',
            'confidence': 0.0,
            'success': False,
            'error': str(e)
        }


def get_supported_languages() -> dict:
    """Get list of all supported languages with their native labels."""
    return {
        code: {
            'name': SUPPORTED_LANGUAGES[code],
            'native': LANGUAGE_LABELS[code]
        }
        for code in SUPPORTED_LANGUAGES
    }


def clear_cache():
    """Clear the translation cache."""
    global _translation_cache
    _translation_cache = {}
