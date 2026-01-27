"""
Multilingual Mandi - Price Discovery Service
=============================================
AI-powered price discovery using market data and Gemini AI (NEW SDK).
Provides fair price recommendations with confidence scores.

Author: Hackathon Team
Date: January 2026
"""

from google import genai
import json
import os
from typing import Optional, Dict
from datetime import datetime

# Load price data on module import
_price_data = None
_products_data = None
_client = None


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


def _get_client():
    """Get Gemini client using new SDK."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            _client = genai.Client(api_key=api_key)
    return _client


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
        'confidence': 0.85,
        'success': True
    }


async def get_ai_price_analysis(
    product_name: str,
    location: str,
    quantity: float,
    quality: str = "medium",
    user_lang: str = "en"
) -> dict:
    """Get AI-powered price analysis using Gemini."""
    client = _get_client()
    
    if not client:
        return {
            'success': False,
            'error': 'Gemini API not configured',
            'fallback': True
        }
    
    try:
        lang_names = {
            'hi': 'Hindi', 'en': 'English', 'ta': 'Tamil', 'te': 'Telugu',
            'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 
            'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi'
        }
        response_lang = lang_names.get(user_lang, 'English')
        
        prompt = f"""You are a market price expert for Indian local markets (mandis).

Analyze the fair price for:
- Product: {product_name}
- Location: {location}, India
- Quantity: {quantity} units
- Quality: {quality}
- Current Date: {datetime.now().strftime("%B %Y")}

Provide your response in {response_lang} language with:
1. Estimated fair price per unit (in ₹)
2. Price range (min-max in ₹)
3. 2-3 key factors affecting price right now
4. One negotiation tip for buyers
5. One tip for vendors

Keep response concise and practical. Use bullet points."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
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
    """Get price trend for a product."""
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
    """List all available products, optionally filtered by category."""
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
    """List all product categories."""
    products_data = _get_products_data()
    categories = products_data.get('categories', [])
    
    return [
        {
            'id': c['id'],
            'name': c.get('name', {}).get(lang, c.get('name', {}).get('en', c['id']))
        }
        for c in categories
    ]
