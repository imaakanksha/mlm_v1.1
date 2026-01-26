"""
Multilingual Mandi - Price Discovery Service
=============================================
AI-powered price discovery using market data and Gemini AI.
Provides fair price recommendations with confidence scores.

Features:
- Location-based pricing (Mumbai, Delhi, Bangalore, etc.)
- Seasonal adjustments
- Quality-based pricing
- AI-powered market analysis

Author: Hackathon Team
Date: January 2026
"""

import json
import os
from typing import Optional, Dict
from datetime import datetime
import google.generativeai as genai

# Load price data on module import
_price_data = None
_products_data = None


def _load_data():
    """Load market price and product data from JSON files."""
    global _price_data, _products_data
    
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    with open(os.path.join(data_dir, 'price_data.json'), 'r', encoding='utf-8') as f:
        _price_data = json.load(f)
    
    with open(os.path.join(data_dir, 'products.json'), 'r', encoding='utf-8') as f:
        _products_data = json.load(f)


def _get_price_data():
    """Get price data, loading if needed."""
    if _price_data is None:
        _load_data()
    return _price_data


def _get_products_data():
    """Get products data, loading if needed."""
    if _products_data is None:
        _load_data()
    return _products_data


def _get_gemini_model():
    """Get Gemini model for AI analysis."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')


def get_current_month() -> str:
    """Get current month name for seasonal adjustment."""
    return datetime.now().strftime("%B")


def calculate_fair_price(
    product_id: str,
    location: str = "default",
    quality: str = "medium",
    quantity: float = 1.0
) -> dict:
    """
    Calculate fair price for a product based on market data.
    
    Args:
        product_id: Product identifier (e.g., 'tomato', 'onion')
        location: City name (e.g., 'Mumbai', 'Delhi')
        quality: Quality level ('low', 'medium', 'high', 'premium')
        quantity: Quantity in base units
    
    Returns:
        dict: {
            'product_id': str,
            'fair_price': float,
            'price_range': {'min': float, 'max': float},
            'total_amount': float,
            'unit': str,
            'location': str,
            'trend': str,
            'factors': list,
            'confidence': float,
            'success': bool
        }
    """
    price_data = _get_price_data()
    products_data = _get_products_data()
    
    # Find product
    product = None
    for p in products_data.get('products', []):
        if p['id'] == product_id:
            product = p
            break
    
    if not product:
        return {
            'product_id': product_id,
            'success': False,
            'error': f"Product not found: {product_id}"
        }
    
    # Get market price for product and location
    market_prices = price_data.get('market_prices', {})
    product_prices = market_prices.get(product_id, {})
    location_price = product_prices.get(location, product_prices.get('default', {}))
    
    if not location_price:
        # Fallback to product's typical range
        typical = product.get('typical_price_range', {'min': 30, 'max': 60})
        location_price = {
            'current': (typical['min'] + typical['max']) / 2,
            'min': typical['min'],
            'max': typical['max'],
            'trend': 'stable'
        }
    
    # Apply seasonal adjustment
    month = get_current_month()
    seasonal_factors = price_data.get('seasonal_factors', {}).get(month, {})
    category = product.get('category', 'vegetables')
    seasonal_multiplier = seasonal_factors.get(category, 1.0)
    
    # Apply quality adjustment
    quality_factors = price_data.get('quality_factors', {})
    quality_multiplier = quality_factors.get(quality, 1.0)
    
    # Calculate final prices
    base_price = location_price['current']
    adjusted_price = base_price * seasonal_multiplier * quality_multiplier
    
    min_price = location_price['min'] * seasonal_multiplier * quality_multiplier
    max_price = location_price['max'] * seasonal_multiplier * quality_multiplier
    
    # Round to reasonable values
    fair_price = round(adjusted_price, 2)
    min_price = round(min_price, 2)
    max_price = round(max_price, 2)
    total_amount = round(fair_price * quantity, 2)
    
    # Build factors explanation
    factors = []
    
    if seasonal_multiplier != 1.0:
        direction = "higher" if seasonal_multiplier > 1.0 else "lower"
        percent = abs(round((seasonal_multiplier - 1.0) * 100))
        factors.append({
            'name': 'Seasonal',
            'impact': 'positive' if seasonal_multiplier < 1.0 else 'negative',
            'description': f"{month} typically has {percent}% {direction} prices for {category}"
        })
    
    if quality_multiplier != 1.0:
        factors.append({
            'name': 'Quality',
            'impact': 'neutral',
            'description': f"{quality.capitalize()} quality affects price by {round((quality_multiplier - 1.0) * 100)}%"
        })
    
    if location != "default":
        factors.append({
            'name': 'Location',
            'impact': 'neutral',
            'description': f"Prices based on {location} market rates"
        })
    
    return {
        'product_id': product_id,
        'product_name': product.get('name', {}).get('en', product_id),
        'fair_price': fair_price,
        'price_range': {
            'min': min_price,
            'max': max_price
        },
        'total_amount': total_amount,
        'quantity': quantity,
        'unit': product.get('unit', 'kg'),
        'location': location,
        'trend': location_price.get('trend', 'stable'),
        'factors': factors,
        'confidence': 0.85,  # High confidence when using market data
        'success': True
    }


async def get_ai_price_analysis(
    product_name: str,
    location: str,
    quantity: float,
    quality: str = "medium",
    user_lang: str = "en"
) -> dict:
    """
    Get AI-powered price analysis using Gemini.
    Provides detailed market insights and negotiation tips.
    
    Args:
        product_name: Name of the product (any language)
        location: City or region
        quantity: Quantity needed
        quality: Quality level
        user_lang: Language for response
    
    Returns:
        dict with AI analysis including fair price, tips, and market insights
    """
    model = _get_gemini_model()
    
    if not model:
        # Fallback to basic calculation if API not available
        return {
            'success': False,
            'error': 'AI service not configured',
            'fallback': True
        }
    
    try:
        # Language names for prompt
        lang_names = {
            'hi': 'Hindi', 'en': 'English', 'ta': 'Tamil', 'te': 'Telugu',
            'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 
            'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi'
        }
        response_lang = lang_names.get(user_lang, 'English')
        
        prompt = f"""You are a market price expert for Indian local markets (mandis).

Analyze the fair price for:
- Product: {product_name}
- Location: {location}
- Quantity: {quantity} units
- Quality: {quality}
- Current Date: {datetime.now().strftime("%B %Y")}

Provide in {response_lang} language:
1. Estimated fair price per unit (in ₹)
2. Price range (min-max)
3. Key factors affecting price
4. Negotiation tips for buyers
5. Selling tips for vendors

Keep response concise and practical for market vendors."""

        response = model.generate_content(prompt)
        
        return {
            'analysis': response.text,
            'product': product_name,
            'location': location,
            'quantity': quantity,
            'quality': quality,
            'language': user_lang,
            'success': True
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_price_trend(product_id: str, location: str = "default") -> dict:
    """
    Get price trend for a product.
    
    Returns:
        dict: {'trend': 'rising'|'falling'|'stable'|'seasonal', 'description': str}
    """
    price_data = _get_price_data()
    market_prices = price_data.get('market_prices', {})
    product_prices = market_prices.get(product_id, {})
    location_price = product_prices.get(location, product_prices.get('default', {}))
    
    trend = location_price.get('trend', 'stable')
    
    descriptions = {
        'rising': 'Prices are increasing. Consider buying soon.',
        'falling': 'Prices are decreasing. You may get better deals if you wait.',
        'stable': 'Prices are steady. Good time to negotiate.',
        'seasonal': 'Prices vary with season. Check current availability.'
    }
    
    return {
        'trend': trend,
        'description': descriptions.get(trend, 'Price trend unavailable.')
    }


def list_products(category: Optional[str] = None, lang: str = "en") -> list:
    """
    List all available products, optionally filtered by category.
    
    Args:
        category: Filter by category (vegetables, fruits, grains, spices)
        lang: Language code for product names
    
    Returns:
        list of product dicts with id, name, unit, image, category
    """
    products_data = _get_products_data()
    products = products_data.get('products', [])
    
    if category:
        products = [p for p in products if p.get('category') == category]
    
    result = []
    for p in products:
        result.append({
            'id': p['id'],
            'name': p.get('name', {}).get(lang, p.get('name', {}).get('en', p['id'])),
            'unit': p.get('unit', 'kg'),
            'image': p.get('image', '📦'),
            'category': p.get('category', 'other')
        })
    
    return result


def list_categories(lang: str = "en") -> list:
    """
    List all product categories.
    
    Args:
        lang: Language code for category names
    
    Returns:
        list of category dicts with id and name
    """
    products_data = _get_products_data()
    categories = products_data.get('categories', [])
    
    return [
        {
            'id': c['id'],
            'name': c.get('name', {}).get(lang, c.get('name', {}).get('en', c['id']))
        }
        for c in categories
    ]


# TODO: Add historical price tracking
# TODO: Implement demand forecasting
# TODO: Add price alerts feature
