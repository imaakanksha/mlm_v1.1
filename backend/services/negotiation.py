"""
Multilingual Mandi - Negotiation Assistant
==========================================
AI-powered negotiation assistance using Gemini (NEW SDK).
Provides culturally-aware bargaining suggestions.

Author: Hackathon Team
Date: January 2026
"""

from google import genai
import os
from typing import Optional, List

# Gemini client
_client = None


def _get_client():
    """Get Gemini client using new SDK."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            _client = genai.Client(api_key=api_key)
    return _client


# Language names mapping
LANG_NAMES = {
    'hi': 'Hindi', 'en': 'English', 'ta': 'Tamil', 'te': 'Telugu',
    'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 
    'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi'
}


async def analyze_quote(
    offered_price: float,
    fair_price: float,
    price_range: dict,
    product_name: str,
    offered_by: str,
    user_type: str,
    user_lang: str = "en"
) -> dict:
    """Analyze a price quote and provide negotiation advice."""
    
    # Calculate fairness
    if fair_price > 0:
        deviation = abs(offered_price - fair_price) / fair_price
        fairness_score = max(0, 1 - deviation)
    else:
        fairness_score = 0.5
    
    min_price = price_range.get('min', fair_price * 0.7)
    max_price = price_range.get('max', fair_price * 1.3)
    
    # Try AI-powered analysis
    client = _get_client()
    
    if client:
        try:
            response_lang = LANG_NAMES.get(user_lang, 'English')
            
            prompt = f"""You are a negotiation expert for Indian local markets (mandis).

Situation:
- Product: {product_name}
- Fair market price: ₹{fair_price}
- Price range: ₹{min_price} - ₹{max_price}
- Offered price: ₹{offered_price}
- Offer made by: {offered_by}
- Advice needed for: {user_type}

Provide advice in {response_lang} language:
1. Should they ACCEPT, COUNTER, or REJECT? (one word)
2. Brief reasoning (1 sentence)
3. If counter, suggest a price
4. A polite phrase to say in response

Format your response as:
RECOMMENDATION: [accept/counter/reject]
REASON: [your reasoning]
COUNTER_PRICE: [price or "N/A"]
PHRASE: [what to say]"""

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Parse response
            text = response.text
            lines = text.strip().split('\n')
            
            recommendation = 'counter'
            reasoning = ''
            suggested_counter = None
            phrase = ''
            
            for line in lines:
                line = line.strip()
                if line.upper().startswith('RECOMMENDATION:'):
                    rec = line.split(':', 1)[1].strip().lower()
                    if 'accept' in rec:
                        recommendation = 'accept'
                    elif 'reject' in rec:
                        recommendation = 'reject'
                    else:
                        recommendation = 'counter'
                elif line.upper().startswith('REASON:'):
                    reasoning = line.split(':', 1)[1].strip()
                elif line.upper().startswith('COUNTER_PRICE:'):
                    price_str = line.split(':', 1)[1].strip()
                    try:
                        suggested_counter = float(price_str.replace('₹', '').replace(',', '').strip())
                    except:
                        suggested_counter = None
                elif line.upper().startswith('PHRASE:'):
                    phrase = line.split(':', 1)[1].strip()
            
            return {
                'recommendation': recommendation,
                'reasoning': reasoning or f"Based on fair price of ₹{fair_price}",
                'suggested_response': phrase or "Let's negotiate further.",
                'suggested_counter': suggested_counter,
                'fairness_score': round(fairness_score, 2),
                'offered_price': offered_price,
                'fair_price': fair_price,
                'ai_powered': True,
                'success': True
            }
            
        except Exception as e:
            pass  # Fall through to rule-based logic
    
    # Fallback: Rule-based recommendation
    if user_type == 'buyer':
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
        if offered_price >= fair_price:
            recommendation = 'accept'
            reasoning = f"This offer is at or above the fair market price."
        elif offered_price >= min_price:
            recommendation = 'counter'
            reasoning = f"This offer is below fair value. Try negotiating up to ₹{fair_price}."
        else:
            recommendation = 'reject'
            reasoning = f"This offer is too low. The minimum acceptable should be around ₹{min_price}."
    
    suggested_counter = round((offered_price + fair_price) / 2, 2) if recommendation == 'counter' else None
    
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
        'ai_powered': False,
        'success': True
    }


async def get_negotiation_tips(
    product_name: str,
    user_type: str,
    location: str,
    user_lang: str = "en"
) -> dict:
    """Get AI-powered negotiation tips."""
    client = _get_client()
    
    if client:
        try:
            response_lang = LANG_NAMES.get(user_lang, 'English')
            
            prompt = f"""You are an expert in Indian market (mandi) negotiations.

Provide 5 practical negotiation tips for a {user_type} buying/selling {product_name} in {location}, India.

Write tips in {response_lang} language.
Keep each tip brief (1 sentence) and actionable.
Consider local cultural norms and market practices.
Format as a numbered list (1. 2. 3. 4. 5.)"""

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Parse tips
            tips = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering/bullets
                    tip = line.lstrip('0123456789.-•) ').strip()
                    if tip:
                        tips.append(tip)
            
            if tips:
                return {
                    'tips': tips[:5],
                    'product': product_name,
                    'user_type': user_type,
                    'location': location,
                    'success': True,
                    'ai_generated': True
                }
        except Exception as e:
            pass
    
    # Fallback tips
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


async def suggest_compromise(
    current_offer: float,
    counter_offer: float,
    fair_price: float,
    rounds: int,
    user_lang: str = "en"
) -> dict:
    """Suggest a compromise price for stalled negotiations."""
    midpoint = (current_offer + counter_offer) / 2
    
    if rounds >= 3:
        suggested = fair_price
        reasoning = "After several rounds, the fair market price is a good compromise."
    else:
        weight = 0.7
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
    action: str,
    amount: Optional[float],
    product_name: str,
    user_type: str,
    user_lang: str = "en"
) -> dict:
    """Generate a polite phrase for negotiation response."""
    client = _get_client()
    
    if client:
        try:
            response_lang = LANG_NAMES.get(user_lang, 'English')
            
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

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            return {
                'phrase': response.text.strip(),
                'action': action,
                'success': True,
                'ai_generated': True
            }
            
        except Exception as e:
            pass
    
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
    
    phrase = fallback_phrases.get(action, {}).get(user_lang, 
             fallback_phrases.get(action, {}).get('en', ""))
    
    return {
        'phrase': phrase,
        'success': True,
        'ai_generated': False
    }
