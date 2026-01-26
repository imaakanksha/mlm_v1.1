"""
Backend Services Package
========================
This package contains the core AI-powered services for Multilingual Mandi.

Services:
- translation: Real-time multilingual translation using Gemini
- pricing: AI-powered price discovery and market analysis
- negotiation: Culturally-aware negotiation assistance
"""

from .translation import translate_text, detect_language, get_supported_languages
from .pricing import calculate_fair_price, list_products, list_categories
from .negotiation import analyze_quote, get_negotiation_tips

__all__ = [
    'translate_text',
    'detect_language', 
    'get_supported_languages',
    'calculate_fair_price',
    'list_products',
    'list_categories',
    'analyze_quote',
    'get_negotiation_tips'
]
