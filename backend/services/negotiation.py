"""
Multilingual Mandi - Negotiation Assistant
==========================================
AI-powered negotiation assistance using Gemini.
Provides culturally-aware bargaining suggestions.

Features:
- Quote analysis against fair prices
- Counteroffer suggestions
- Cultural negotiation tips
- Stalemate resolution

Author: Hackathon Team
Date: January 2026
"""

import os
from typing import Optional, List
import google.generativeai as genai


def _get_gemini_model():
    """Get Gemini model for AI analysis."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')


async def analyze_quote(
    offered_price: float,
    fair_price: float,
    price_range: dict,
    product_name: str,
    offered_by: str,  # 'vendor' or 'buyer'
    user_type: str,   # 'vendor' or 'buyer' - who is asking for advice
    user_lang: str = "en"
) -> dict:
    """
    Analyze a price quote and provide negotiation advice.
    
    Args:
        offered_price: The price being offered
        fair_price: The calculated fair market price
        price_range: {'min': float, 'max': float}
        product_name: Name of the product
        offered_by: Who made the offer ('vendor' or 'buyer')
        user_type: Who is asking for advice
        user_lang: Language for response
    
    Returns:
        dict: {
            'recommendation': 'accept' | 'reject' | 'counter',
            'reasoning': str,
            'suggested_response': str,
            'suggested_counter': float (if counter),
            'fairness_score': float (0-1),
            'success': bool
        }
    """
    # Calculate fairness
    if fair_price > 0:
        deviation = abs(offered_price - fair_price) / fair_price
        fairness_score = max(0, 1 - deviation)
    else:
        fairness_score = 0.5
    
    # Determine if price is in acceptable range
    min_price = price_range.get('min', fair_price * 0.7)
    max_price = price_range.get('max', fair_price * 1.3)
    
    # Basic recommendation logic
    if user_type == 'buyer':
        # Buyer wants low prices
        if offered_price <= fair_price:
            recommendation = 'accept'
            reasoning = f"This price is at or below the fair market price of ₹{fair_price}."
        elif offered_price <= max_price:
            recommendation = 'counter'
            reasoning = f"This price is above fair value. You can negotiate closer to ₹{fair_price}."
        else:
            recommendation = 'reject'
            reasoning = f"This price is too high compared to market rates."
    else:
        # Vendor wants high prices
        if offered_price >= fair_price:
            recommendation = 'accept'
            reasoning = f"This offer is at or above the fair market price."
        elif offered_price >= min_price:
            recommendation = 'counter'
            reasoning = f"This offer is below fair value. Try negotiating up to ₹{fair_price}."
        else:
            recommendation = 'reject'
            reasoning = f"This offer is too low. The minimum acceptable should be around ₹{min_price}."
    
    # Calculate suggested counter
    if recommendation == 'counter':
        if user_type == 'buyer':
            suggested_counter = round((offered_price + fair_price) / 2, 2)
        else:
            suggested_counter = round((offered_price + fair_price) / 2, 2)
    else:
        suggested_counter = None
    
    # Generate response suggestion
    if recommendation == 'accept':
        suggested_response = "This is a fair price. You can proceed with the deal."
    elif recommendation == 'counter':
        suggested_response = f"Consider offering ₹{suggested_counter} as a counter."
    else:
        suggested_response = "This price is not reasonable. Look for other options."
    
    return {
        'recommendation': recommendation,
        'reasoning': reasoning,
        'suggested_response': suggested_response,
        'suggested_counter': suggested_counter,
        'fairness_score': round(fairness_score, 2),
        'offered_price': offered_price,
        'fair_price': fair_price,
        'success': True
    }


async def get_negotiation_tips(
    product_name: str,
    user_type: str,
    location: str,
    user_lang: str = "en"
) -> dict:
    """
    Get AI-powered negotiation tips.
    
    Args:
        product_name: Product being negotiated
        user_type: 'vendor' or 'buyer'
        location: Market location
        user_lang: Language for response
    
    Returns:
        dict with tips and cultural advice
    """
    model = _get_gemini_model()
    
    if not model:
        # Fallback tips if API not available
        if user_type == 'buyer':
            tips = [
                "Start with a lower offer, around 70-80% of the asking price",
                "Be respectful and build rapport with the vendor",
                "Ask about bulk discounts if buying larger quantities",
                "Compare prices with nearby vendors first",
                "Be ready to walk away - it's a powerful negotiation tool"
            ]
        else:
            tips = [
                "Know your minimum acceptable price before starting",
                "Highlight the quality of your products",
                "Offer small discounts for bulk purchases",
                "Be patient - rushing can lead to poor deals",
                "Build relationships for repeat customers"
            ]
        
        return {
            'tips': tips,
            'success': True,
            'ai_generated': False
        }
    
    try:
        lang_names = {
            'hi': 'Hindi', 'en': 'English', 'ta': 'Tamil', 'te': 'Telugu',
            'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 
            'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi'
        }
        response_lang = lang_names.get(user_lang, 'English')
        
        prompt = f"""You are an expert in Indian market (mandi) negotiations.

Provide 5 practical negotiation tips for a {user_type} dealing with {product_name} in {location}.

Consider:
1. Local cultural norms and etiquette
2. Common negotiation patterns in Indian markets
3. Practical strategies that work

Respond in {response_lang} language.
Keep each tip brief and actionable.
Format as a numbered list."""

        response = model.generate_content(prompt)
        
        # Parse tips from response
        tips = response.text.strip().split('\n')
        tips = [tip.strip() for tip in tips if tip.strip()]
        
        return {
            'tips': tips,
            'product': product_name,
            'user_type': user_type,
            'location': location,
            'success': True,
            'ai_generated': True
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def suggest_compromise(
    current_offer: float,
    counter_offer: float,
    fair_price: float,
    rounds: int,
    user_lang: str = "en"
) -> dict:
    """
    Suggest a compromise price when negotiation is stalled.
    
    Args:
        current_offer: Latest offer from one party
        counter_offer: Counter from other party
        fair_price: Market fair price
        rounds: Number of negotiation rounds so far
        user_lang: Language for response
    
    Returns:
        dict with suggested compromise and reasoning
    """
    # Calculate midpoint
    midpoint = (current_offer + counter_offer) / 2
    
    # Adjust towards fair price
    if rounds >= 3:
        # After 3+ rounds, suggest fair price as compromise
        suggested = fair_price
        reasoning = "After several rounds, the fair market price is a good compromise."
    else:
        # Earlier rounds - suggest midpoint adjusted towards fair price
        weight = 0.7  # 70% weight to midpoint, 30% to fair price
        suggested = (midpoint * weight) + (fair_price * (1 - weight))
        reasoning = "This compromise is between both offers, adjusted for fair market value."
    
    suggested = round(suggested, 2)
    
    return {
        'suggested_compromise': suggested,
        'reasoning': reasoning,
        'current_offer': current_offer,
        'counter_offer': counter_offer,
        'fair_price': fair_price,
        'midpoint': round(midpoint, 2),
        'rounds': rounds,
        'success': True
    }


async def generate_response_phrase(
    action: str,  # 'accept', 'counter', 'reject'
    amount: Optional[float],
    product_name: str,
    user_type: str,
    user_lang: str = "en"
) -> dict:
    """
    Generate a polite phrase for negotiation response.
    
    Args:
        action: The action to take
        amount: The amount (for counter offers)
        product_name: Product name
        user_type: 'vendor' or 'buyer'
        user_lang: Language for response
    
    Returns:
        dict with phrase in requested language
    """
    model = _get_gemini_model()
    
    # Fallback phrases
    fallback_phrases = {
        'accept': {
            'en': "That's a fair price. I accept your offer.",
            'hi': "यह उचित दाम है। मुझे मंजूर है।"
        },
        'counter': {
            'en': f"I can offer ₹{amount}. Would that work for you?",
            'hi': f"मैं ₹{amount} दे सकता हूं। क्या यह ठीक है?"
        },
        'reject': {
            'en': "I'm sorry, but this price doesn't work for me.",
            'hi': "माफ़ कीजिए, यह दाम मेरे लिए ठीक नहीं है।"
        }
    }
    
    if not model:
        phrase = fallback_phrases.get(action, {}).get(user_lang, 
                 fallback_phrases.get(action, {}).get('en', ""))
        return {
            'phrase': phrase,
            'success': True,
            'ai_generated': False
        }
    
    try:
        lang_names = {
            'hi': 'Hindi', 'en': 'English', 'ta': 'Tamil', 'te': 'Telugu',
            'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 
            'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi'
        }
        response_lang = lang_names.get(user_lang, 'English')
        
        if action == 'accept':
            context = f"accepting an offer for {product_name}"
        elif action == 'counter':
            context = f"making a counter offer of ₹{amount} for {product_name}"
        else:
            context = f"politely declining an offer for {product_name}"
        
        prompt = f"""Generate a short, polite phrase in {response_lang} for a {user_type} {context} in an Indian local market.

The phrase should be:
1. Respectful and friendly
2. Natural sounding for local market conversations
3. Brief (1-2 sentences max)

Respond with ONLY the phrase, nothing else."""

        response = model.generate_content(prompt)
        
        return {
            'phrase': response.text.strip(),
            'action': action,
            'success': True,
            'ai_generated': True
        }
        
    except Exception as e:
        phrase = fallback_phrases.get(action, {}).get('en', "")
        return {
            'phrase': phrase,
            'success': False,
            'error': str(e),
            'ai_generated': False
        }


# TODO: Add negotiation history tracking
# TODO: Implement learning from successful negotiations
# TODO: Add multi-party negotiation support
