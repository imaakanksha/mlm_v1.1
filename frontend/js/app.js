/**
 * Multilingual Mandi - Main Application JavaScript
 * ==================================================
 * Handles all frontend logic including:
 * - Tab navigation
 * - Translation with Gemini API
 * - Voice input using Web Speech API
 * - Price discovery
 * - Negotiation assistance
 * 
 * Author: Hackathon Team
 * Date: January 2026
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_BASE_URL = window.location.origin;

// Language configuration
const LANGUAGES = {
    hi: { name: 'Hindi', native: 'हिंदी' },
    en: { name: 'English', native: 'English' },
    ta: { name: 'Tamil', native: 'தமிழ்' },
    te: { name: 'Telugu', native: 'తెలుగు' },
    bn: { name: 'Bengali', native: 'বাংলা' },
    mr: { name: 'Marathi', native: 'मराठी' },
    gu: { name: 'Gujarati', native: 'ગુજરાતી' },
    kn: { name: 'Kannada', native: 'ಕನ್ನಡ' },
    ml: { name: 'Malayalam', native: 'മലയാളം' },
    pa: { name: 'Punjabi', native: 'ਪੰਜਾਬੀ' }
};

// Application state
const state = {
    currentLang: 'en',
    currentTab: 'translate',
    userType: 'buyer',
    products: [],
    isRecording: false,
    recognition: null
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Make API request with error handling
 */
async function apiRequest(endpoint, options = {}) {
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    // Remove after animation
    setTimeout(() => toast.remove(), 3000);
}

/**
 * Debounce function for input handling
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================

function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const sections = document.querySelectorAll('.section');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            // Update buttons
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update sections
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById(`${tabId}Section`).classList.add('active');

            state.currentTab = tabId;

            // Load data for specific tabs
            if (tabId === 'products' && state.products.length === 0) {
                loadProducts();
            }
        });
    });
}

// ============================================================================
// TRANSLATION FUNCTIONALITY
// ============================================================================

async function translateText() {
    const sourceText = document.getElementById('sourceText').value.trim();
    const sourceLang = document.getElementById('sourceLang').value;
    const targetLang = document.getElementById('targetLang').value;
    const outputEl = document.getElementById('translatedText');
    const statusEl = document.getElementById('translationStatus');

    if (!sourceText) {
        showToast('Please enter text to translate', 'error');
        return;
    }

    // Show loading state
    outputEl.innerHTML = '<span class="placeholder-text">Translating...</span>';
    statusEl.textContent = '';
    statusEl.className = 'translation-status';

    try {
        const result = await apiRequest('/api/translate', {
            method: 'POST',
            body: JSON.stringify({
                text: sourceText,
                source_lang: sourceLang,
                target_lang: targetLang
            })
        });

        if (result.success) {
            outputEl.textContent = result.translated_text;
            statusEl.textContent = result.cached ? '⚡ From cache' : '✓ Translated';
            statusEl.classList.add('success');
        } else {
            outputEl.textContent = result.translated_text;
            statusEl.textContent = `⚠ ${result.error || 'Translation failed'}`;
            statusEl.classList.add('error');
        }
    } catch (error) {
        outputEl.innerHTML = '<span class="placeholder-text">Translation failed. Check your connection.</span>';
        statusEl.textContent = '❌ Error connecting to server';
        statusEl.classList.add('error');
        showToast('Translation failed', 'error');
    }
}

function initTranslation() {
    // Translate button
    document.getElementById('translateBtn').addEventListener('click', translateText);

    // Swap languages
    document.getElementById('swapLangs').addEventListener('click', () => {
        const sourceLang = document.getElementById('sourceLang');
        const targetLang = document.getElementById('targetLang');
        const temp = sourceLang.value;
        sourceLang.value = targetLang.value;
        targetLang.value = temp;
    });

    // Copy button
    document.getElementById('copyBtn').addEventListener('click', () => {
        const text = document.getElementById('translatedText').textContent;
        if (text && !text.includes('Translation will appear')) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('Copied to clipboard!', 'success');
            });
        }
    });

    // Quick phrases
    document.querySelectorAll('.phrase-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.getElementById('sourceText').value = chip.dataset.phrase;
            translateText();
        });
    });

    // Enter key to translate
    document.getElementById('sourceText').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            translateText();
        }
    });
}

// ============================================================================
// VOICE INPUT (Web Speech API)
// ============================================================================

function initVoiceInput() {
    const voiceBtn = document.getElementById('voiceInputBtn');

    // Check for browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        voiceBtn.disabled = true;
        voiceBtn.innerHTML = '🎤 <span>Not supported</span>';
        return;
    }

    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    state.recognition = new SpeechRecognition();
    state.recognition.continuous = false;
    state.recognition.interimResults = true;

    // Map language codes to BCP-47 format
    const langMap = {
        hi: 'hi-IN',
        en: 'en-IN',
        ta: 'ta-IN',
        te: 'te-IN',
        bn: 'bn-IN',
        mr: 'mr-IN',
        gu: 'gu-IN',
        kn: 'kn-IN',
        ml: 'ml-IN',
        pa: 'pa-IN'
    };

    voiceBtn.addEventListener('click', () => {
        if (state.isRecording) {
            state.recognition.stop();
            return;
        }

        // Set language
        const sourceLang = document.getElementById('sourceLang').value;
        state.recognition.lang = langMap[sourceLang] || 'en-IN';

        state.recognition.start();
    });

    state.recognition.onstart = () => {
        state.isRecording = true;
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = '⏹ <span>Stop</span>';
        showToast('Listening...', 'info');
    };

    state.recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        const sourceTextEl = document.getElementById('sourceText');
        if (finalTranscript) {
            sourceTextEl.value = finalTranscript;
        } else if (interimTranscript) {
            sourceTextEl.value = interimTranscript;
        }
    };

    state.recognition.onend = () => {
        state.isRecording = false;
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '🎤 <span>Speak</span>';

        // Auto-translate after voice input
        const sourceText = document.getElementById('sourceText').value;
        if (sourceText.trim()) {
            translateText();
        }
    };

    state.recognition.onerror = (event) => {
        state.isRecording = false;
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '🎤 <span>Speak</span>';

        if (event.error === 'no-speech') {
            showToast('No speech detected. Try again.', 'error');
        } else {
            showToast(`Voice error: ${event.error}`, 'error');
        }
    };
}

// ============================================================================
// PRODUCTS FUNCTIONALITY
// ============================================================================

async function loadProducts(category = null) {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = '<div class="loading-spinner">Loading products...</div>';

    try {
        const lang = state.currentLang;
        let endpoint = `/api/products?lang=${lang}`;
        if (category && category !== 'all') {
            endpoint += `&category=${category}`;
        }

        const result = await apiRequest(endpoint);
        state.products = result.products;

        renderProducts(state.products);
    } catch (error) {
        grid.innerHTML = '<div class="loading-spinner">Failed to load products. Is the server running?</div>';
    }
}

function renderProducts(products) {
    const grid = document.getElementById('productsGrid');

    if (!products || products.length === 0) {
        grid.innerHTML = '<div class="loading-spinner">No products found</div>';
        return;
    }

    grid.innerHTML = products.map(product => `
        <div class="product-card" data-id="${product.id}">
            <span class="product-emoji">${product.image || '📦'}</span>
            <div class="product-name">${product.name}</div>
            <div class="product-unit">per ${product.unit}</div>
        </div>
    `).join('');

    // Add click handlers
    grid.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', () => {
            const productId = card.dataset.id;
            selectProductForPricing(productId);
        });
    });
}

function selectProductForPricing(productId) {
    // Switch to pricing tab
    document.querySelector('[data-tab="pricing"]').click();

    // Select product in dropdown
    const priceProductEl = document.getElementById('priceProduct');
    priceProductEl.value = productId;
}

function initProducts() {
    // Category filter
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadProducts(btn.dataset.category);
        });
    });
}

// ============================================================================
// PRICING FUNCTIONALITY
// ============================================================================

async function populatePriceProducts() {
    try {
        const result = await apiRequest(`/api/products?lang=${state.currentLang}`);
        const select = document.getElementById('priceProduct');

        select.innerHTML = '<option value="">Select a product...</option>';
        result.products.forEach(product => {
            select.innerHTML += `<option value="${product.id}">${product.image} ${product.name}</option>`;
        });
    } catch (error) {
        console.error('Failed to load products for pricing:', error);
    }
}

async function getPrice() {
    const productId = document.getElementById('priceProduct').value;
    const quantity = parseFloat(document.getElementById('priceQuantity').value) || 1;
    const quality = document.getElementById('priceQuality').value;
    const location = document.getElementById('priceLocation').value;

    if (!productId) {
        showToast('Please select a product', 'error');
        return;
    }

    try {
        const result = await apiRequest('/api/pricing', {
            method: 'POST',
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity,
                quality: quality,
                location: location
            })
        });

        displayPriceResult(result);
    } catch (error) {
        showToast('Failed to get price', 'error');
    }
}

function displayPriceResult(result) {
    const resultEl = document.getElementById('priceResult');
    resultEl.classList.remove('hidden');

    // Find product emoji
    const product = state.products.find(p => p.id === result.product_id);
    document.getElementById('resultEmoji').textContent = product?.image || '📦';
    document.getElementById('resultProductName').textContent = result.product_name || result.product_id;
    document.getElementById('resultQuantity').textContent = `${result.quantity} ${result.unit}`;

    // Prices
    document.getElementById('resultFairPrice').textContent = `₹${result.fair_price}`;
    document.getElementById('resultMinPrice').textContent = `₹${result.price_range.min}`;
    document.getElementById('resultMaxPrice').textContent = `₹${result.price_range.max}`;
    document.getElementById('resultTotal').textContent = `₹${result.total_amount}`;

    // Trend
    const trendEl = document.getElementById('resultTrend');
    const trendIcons = {
        rising: '📈 Rising',
        falling: '📉 Falling',
        stable: '● Stable',
        seasonal: '🌸 Seasonal'
    };
    trendEl.innerHTML = `<span class="trend-indicator ${result.trend}">${trendIcons[result.trend] || result.trend}</span>`;

    // Factors
    const factorsEl = document.getElementById('resultFactors');
    if (result.factors && result.factors.length > 0) {
        factorsEl.innerHTML = result.factors.map(f => `
            <div class="factor-item">
                <span class="factor-icon ${f.impact}">
                    ${f.impact === 'positive' ? '↓' : f.impact === 'negative' ? '↑' : '→'}
                </span>
                <span>${f.description}</span>
            </div>
        `).join('');
    } else {
        factorsEl.innerHTML = '';
    }

    // Scroll to result
    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function initPricing() {
    document.getElementById('getPriceBtn').addEventListener('click', getPrice);
    populatePriceProducts();
}

// ============================================================================
// NEGOTIATION FUNCTIONALITY
// ============================================================================

function initNegotiation() {
    // User type toggle
    document.querySelectorAll('.user-type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.user-type-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.userType = btn.dataset.type;
        });
    });

    // Analyze quote button
    document.getElementById('analyzeQuoteBtn').addEventListener('click', analyzeQuote);

    // Get tips button
    document.getElementById('getTipsBtn').addEventListener('click', getNegotiationTips);
}

async function analyzeQuote() {
    const product = document.getElementById('negProduct').value.trim();
    const offeredPrice = parseFloat(document.getElementById('negOfferedPrice').value);
    const fairPrice = parseFloat(document.getElementById('negFairPrice').value);

    if (!product || isNaN(offeredPrice) || isNaN(fairPrice)) {
        showToast('Please fill all fields', 'error');
        return;
    }

    try {
        const result = await apiRequest('/api/negotiate/analyze', {
            method: 'POST',
            body: JSON.stringify({
                offered_price: offeredPrice,
                fair_price: fairPrice,
                price_range_min: fairPrice * 0.7,
                price_range_max: fairPrice * 1.3,
                product_name: product,
                offered_by: state.userType === 'buyer' ? 'vendor' : 'buyer',
                user_type: state.userType,
                user_lang: state.currentLang
            })
        });

        displayNegotiationResult(result);
    } catch (error) {
        showToast('Failed to analyze quote', 'error');
    }
}

function displayNegotiationResult(result) {
    const resultEl = document.getElementById('negotiateResult');
    resultEl.classList.remove('hidden');

    // Recommendation badge
    const recEl = document.getElementById('negRecommendation');
    const recIcons = {
        accept: '✅',
        counter: '💬',
        reject: '❌'
    };
    recEl.innerHTML = `<span class="rec-badge ${result.recommendation}">
        ${recIcons[result.recommendation]} ${result.recommendation.toUpperCase()}
    </span>`;

    // Reasoning
    document.getElementById('negReasoning').textContent = result.reasoning;

    // Suggestion
    const suggEl = document.getElementById('negSuggestion');
    if (result.suggested_counter) {
        suggEl.innerHTML = `<strong>Suggested counter:</strong> ₹${result.suggested_counter}<br>${result.suggested_response}`;
    } else {
        suggEl.textContent = result.suggested_response;
    }

    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function getNegotiationTips() {
    const product = document.getElementById('negProduct').value.trim() || 'vegetables';
    const tipsContainer = document.getElementById('negTips');

    tipsContainer.innerHTML = '<div class="loading-spinner">Loading tips...</div>';

    try {
        const result = await apiRequest(`/api/negotiate/tips?product_name=${encodeURIComponent(product)}&user_type=${state.userType}&location=India&user_lang=${state.currentLang}`);

        if (result.tips && result.tips.length > 0) {
            tipsContainer.innerHTML = result.tips.map((tip, i) => `
                <div class="tip-item">
                    <span class="tip-number">${i + 1}</span>
                    <span>${tip}</span>
                </div>
            `).join('');
        } else {
            tipsContainer.innerHTML = '<p>No tips available</p>';
        }
    } catch (error) {
        tipsContainer.innerHTML = '<button id="getTipsBtn" class="secondary-btn">Retry</button>';
        document.getElementById('getTipsBtn').addEventListener('click', getNegotiationTips);
    }
}

// ============================================================================
// LANGUAGE SWITCHING
// ============================================================================

function initLanguageSwitch() {
    const currentLangEl = document.getElementById('currentLang');

    currentLangEl.addEventListener('change', (e) => {
        state.currentLang = e.target.value;

        // Reload products with new language
        if (state.products.length > 0) {
            loadProducts();
        }

        // Refresh price products dropdown
        populatePriceProducts();

        showToast(`Language changed to ${LANGUAGES[state.currentLang].native}`, 'success');
    });
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🏪 Multilingual Mandi - Initializing...');

    // Initialize all modules
    initTabs();
    initTranslation();
    initVoiceInput();
    initProducts();
    initPricing();
    initNegotiation();
    initLanguageSwitch();

    console.log('✅ Multilingual Mandi - Ready!');

    // Check API connectivity
    fetch(`${API_BASE_URL}/health`)
        .then(r => r.json())
        .then(data => {
            if (data.status === 'healthy') {
                console.log('✅ API connected:', data);
                if (!data.gemini_configured) {
                    showToast('⚠️ Gemini API key not configured', 'error');
                }
            }
        })
        .catch(err => {
            console.error('❌ API not reachable:', err);
            showToast('Server not running. Start the backend first.', 'error');
        });
});

// ============================================================================
// SERVICE WORKER REGISTRATION (PWA)
// ============================================================================

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Service worker for offline support can be added here
        // navigator.serviceWorker.register('/sw.js');
    });
}
