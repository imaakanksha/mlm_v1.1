"""
Multilingual Mandi - Main API Server
====================================
FastAPI backend for the Multilingual Mandi platform.
Provides APIs for translation, pricing, and negotiation.

Features:
- Real-time translation between 10 Indian languages
- AI-powered price discovery
- Negotiation assistance
- Product catalog management

Run with: uvicorn main:app --reload --port 8000

Author: Hackathon Team
Date: January 2026
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from services.translation import (
    translate_text, 
    detect_language, 
    get_supported_languages,
    LANGUAGE_LABELS
)
from services.pricing import (
    calculate_fair_price,
    get_ai_price_analysis,
    get_price_trend,
    list_products,
    list_categories
)
from services.negotiation import (
    analyze_quote,
    get_negotiation_tips,
    suggest_compromise,
    generate_response_phrase
)

# Initialize FastAPI app
app = FastAPI(
    title="Multilingual Mandi API",
    description="AI-powered marketplace platform breaking language barriers in Indian markets",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware - allow all origins for hackathon demo
# WHY: Need to allow frontend from any origin during development/demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class TranslateRequest(BaseModel):
    """Request model for translation."""
    text: str
    source_lang: str = "en"
    target_lang: str = "hi"


class TranslateResponse(BaseModel):
    """Response model for translation."""
    translated_text: str
    source_lang: str
    target_lang: str
    cached: bool
    success: bool
    error: Optional[str] = None


class PriceRequest(BaseModel):
    """Request model for price discovery."""
    product_id: str
    location: str = "default"
    quality: str = "medium"
    quantity: float = 1.0


class PriceAnalysisRequest(BaseModel):
    """Request model for AI price analysis."""
    product_name: str
    location: str
    quantity: float = 1.0
    quality: str = "medium"
    user_lang: str = "en"


class QuoteAnalysisRequest(BaseModel):
    """Request model for quote analysis."""
    offered_price: float
    fair_price: float
    price_range_min: float
    price_range_max: float
    product_name: str
    offered_by: str  # 'vendor' or 'buyer'
    user_type: str   # 'vendor' or 'buyer'
    user_lang: str = "en"


class CompromiseRequest(BaseModel):
    """Request model for compromise suggestion."""
    current_offer: float
    counter_offer: float
    fair_price: float
    rounds: int = 1
    user_lang: str = "en"


class PhraseRequest(BaseModel):
    """Request model for response phrase generation."""
    action: str  # 'accept', 'counter', 'reject'
    amount: Optional[float] = None
    product_name: str
    user_type: str
    user_lang: str = "en"


# ============================================================================
# Health & Utility Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment verification.
    Returns status and API key configuration status.
    """
    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "healthy",
        "service": "Multilingual Mandi API",
        "version": "1.0.0",
        "gemini_configured": gemini_configured
    }


@app.get("/api/languages")
async def get_languages():
    """
    Get list of supported languages.
    Returns language codes, names, and native script labels.
    """
    return {
        "languages": get_supported_languages(),
        "labels": LANGUAGE_LABELS
    }


# ============================================================================
# Translation Endpoints
# ============================================================================

@app.post("/api/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate text between supported languages.
    
    Supports 10 Indian languages:
    hi (Hindi), en (English), ta (Tamil), te (Telugu), bn (Bengali),
    mr (Marathi), gu (Gujarati), kn (Kannada), ml (Malayalam), pa (Punjabi)
    """
    result = await translate_text(
        text=request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang
    )
    return TranslateResponse(**result)


@app.post("/api/detect-language")
async def detect_lang(text: str = Query(..., description="Text to detect language of")):
    """
    Detect the language of input text.
    Returns detected language code and confidence.
    """
    result = await detect_language(text)
    return result


# ============================================================================
# Pricing Endpoints
# ============================================================================

@app.post("/api/pricing")
async def get_price(request: PriceRequest):
    """
    Get fair price recommendation for a product.
    
    Uses market data, seasonal adjustments, and quality factors
    to calculate the fair price.
    """
    result = calculate_fair_price(
        product_id=request.product_id,
        location=request.location,
        quality=request.quality,
        quantity=request.quantity
    )
    
    if not result.get('success', False):
        raise HTTPException(status_code=404, detail=result.get('error', 'Price calculation failed'))
    
    return result


@app.post("/api/pricing/analyze")
async def analyze_price(request: PriceAnalysisRequest):
    """
    Get AI-powered price analysis with market insights.
    Uses Gemini to provide detailed pricing information and tips.
    """
    result = await get_ai_price_analysis(
        product_name=request.product_name,
        location=request.location,
        quantity=request.quantity,
        quality=request.quality,
        user_lang=request.user_lang
    )
    return result


@app.get("/api/pricing/trend/{product_id}")
async def get_trend(product_id: str, location: str = "default"):
    """
    Get price trend for a product.
    Returns trend direction (rising/falling/stable/seasonal).
    """
    return get_price_trend(product_id, location)


# ============================================================================
# Product Catalog Endpoints
# ============================================================================

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    lang: str = "en"
):
    """
    List all products, optionally filtered by category.
    Returns product names in the specified language.
    """
    return {
        "products": list_products(category=category, lang=lang),
        "language": lang
    }


@app.get("/api/categories")
async def get_categories(lang: str = "en"):
    """
    List all product categories.
    Returns category names in the specified language.
    """
    return {
        "categories": list_categories(lang=lang),
        "language": lang
    }


# ============================================================================
# Negotiation Endpoints
# ============================================================================

@app.post("/api/negotiate/analyze")
async def analyze_negotiation(request: QuoteAnalysisRequest):
    """
    Analyze a price quote and provide negotiation advice.
    Returns recommendation (accept/counter/reject) with reasoning.
    """
    result = await analyze_quote(
        offered_price=request.offered_price,
        fair_price=request.fair_price,
        price_range={'min': request.price_range_min, 'max': request.price_range_max},
        product_name=request.product_name,
        offered_by=request.offered_by,
        user_type=request.user_type,
        user_lang=request.user_lang
    )
    return result


@app.get("/api/negotiate/tips")
async def get_tips(
    product_name: str,
    user_type: str,
    location: str = "India",
    user_lang: str = "en"
):
    """
    Get negotiation tips for a specific product and context.
    Returns culturally-aware advice for Indian markets.
    """
    result = await get_negotiation_tips(
        product_name=product_name,
        user_type=user_type,
        location=location,
        user_lang=user_lang
    )
    return result


@app.post("/api/negotiate/compromise")
async def get_compromise(request: CompromiseRequest):
    """
    Get a suggested compromise price for stalled negotiations.
    Considers both parties' offers and market fair price.
    """
    result = await suggest_compromise(
        current_offer=request.current_offer,
        counter_offer=request.counter_offer,
        fair_price=request.fair_price,
        rounds=request.rounds,
        user_lang=request.user_lang
    )
    return result


@app.post("/api/negotiate/phrase")
async def get_phrase(request: PhraseRequest):
    """
    Generate a polite phrase for negotiation response.
    Returns culturally appropriate phrases in the user's language.
    """
    result = await generate_response_phrase(
        action=request.action,
        amount=request.amount,
        product_name=request.product_name,
        user_type=request.user_type,
        user_lang=request.user_lang
    )
    return result


# ============================================================================
# Static Files & Frontend Serving
# ============================================================================

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the main frontend page."""
        index_path = os.path.join(frontend_path, 'index.html')
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found. Access API at /api/docs"}


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           🏪 MULTILINGUAL MANDI - API SERVER 🏪              ║
╠══════════════════════════════════════════════════════════════╣
║  Breaking language barriers in Indian local markets          ║
║                                                              ║
║  📍 Server: http://localhost:{port}                           ║
║  📚 API Docs: http://localhost:{port}/api/docs                ║
║  🏥 Health: http://localhost:{port}/health                    ║
║                                                              ║
║  Supported Languages: Hindi, English, Tamil, Telugu,         ║
║  Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )


# TODO: Add WebSocket support for real-time messaging
# TODO: Implement request rate limiting
# TODO: Add API key authentication for production
# TODO: Implement request logging and monitoring
