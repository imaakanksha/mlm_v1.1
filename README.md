# 🏪 Multilingual Mandi

> **Breaking language barriers in Indian local markets with AI-powered translation and fair pricing**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Republic Day Hackathon 2026](https://img.shields.io/badge/Hackathon-Republic%20Day%202026-orange.svg)]()

---

## 🎯 Problem Statement

Language barriers prevent equitable trade in Indian local markets (mandis):
- Vendors and buyers from different regions cannot communicate effectively
- Lack of transparent pricing leads to unfair deals
- Small vendors have limited access to market intelligence

## 💡 Solution

**Multilingual Mandi** is an AI-powered web platform that:

1. **🌐 Real-Time Translation** — Instant translation between 10 Indian languages
2. **💰 Fair Price Discovery** — AI-powered market price recommendations
3. **🤝 Negotiation Assistance** — Culturally-aware bargaining suggestions

---

## ✨ Features

### 🌐 10 Indian Languages Supported
| Language | Native Script |
|----------|---------------|
| Hindi | हिंदी |
| English | English |
| Tamil | தமிழ் |
| Telugu | తెలుగు |
| Bengali | বাংলা |
| Marathi | मराठी |
| Gujarati | ગુજરાતી |
| Kannada | ಕನ್ನಡ |
| Malayalam | മലയാളം |
| Punjabi | ਪੰਜਾਬੀ |

### 🎤 Voice Input
- Speak in any supported language
- Automatic speech-to-text using Web Speech API
- Auto-translation after voice input

### 💰 AI Price Discovery
- Fair price calculation based on market data
- Location-specific pricing (Mumbai, Delhi, Bangalore, etc.)
- Seasonal adjustments
- Quality-based pricing

### 🤝 Negotiation Assistant
- Quote analysis with AI recommendations
- Counter-offer suggestions
- Cultural negotiation tips

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- [Gemini API Key](https://aistudio.google.com/apikey) (FREE)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/multilingual-mandi.git
cd multilingual-mandi
```

### 2. Set Up Environment
```bash
# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
# Copy the example env file
cp ../.env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_key_here
```

### 4. Run the Server
```bash
python main.py
```

### 5. Open in Browser
Visit: **http://localhost:8000**

---

## 📁 Project Structure

```
multilingual-mandi/
├── .kiro/                    # Hackathon specs
│   └── specs/
│       └── multilingual-mandi/
│           ├── MVP_SUMMARY.md
│           ├── design.md
│           ├── requirements.md
│           └── tasks.md
│
├── backend/                   # Python FastAPI backend
│   ├── main.py               # API server entry point
│   ├── services/
│   │   ├── translation.py    # Gemini translation
│   │   ├── pricing.py        # Price discovery
│   │   └── negotiation.py    # Negotiation AI
│   ├── data/
│   │   ├── products.json     # Product catalog
│   │   └── price_data.json   # Market prices
│   └── requirements.txt
│
├── frontend/                  # Static web UI
│   ├── index.html            # Main page
│   ├── css/
│   │   └── style.css         # Premium dark theme
│   └── js/
│       └── app.js            # Application logic
│
├── docs/
│   └── DEMO.md               # Demo script
│
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## 🔌 API Endpoints

### Health Check
```bash
GET /health
```

### Translation
```bash
POST /api/translate
{
  "text": "Hello, how are you?",
  "source_lang": "en",
  "target_lang": "hi"
}
```

### Price Discovery
```bash
POST /api/pricing
{
  "product_id": "tomato",
  "location": "Mumbai",
  "quality": "medium",
  "quantity": 5
}
```

### Products
```bash
GET /api/products?lang=hi&category=vegetables
```

### Negotiation
```bash
POST /api/negotiate/analyze
{
  "offered_price": 50,
  "fair_price": 45,
  "product_name": "Tomatoes",
  "user_type": "buyer"
}
```

Full API documentation: **http://localhost:8000/api/docs**

---

## 🎨 Screenshots

### Translation Interface
- Real-time translation with voice input
- Quick phrase shortcuts
- Clean, mobile-first design

### Price Discovery
- Fair price with confidence indicators
- Price range visualization
- Market trend analysis

### Negotiation Assistant
- AI recommendations (Accept/Counter/Reject)
- Cultural negotiation tips
- Suggested counter-offers

---

## 🌍 Social Impact (Viksit Bharat)

- **Economic Inclusion**: Empowers vendors with limited language skills
- **Fair Trade**: AI-powered pricing ensures transparency
- **Digital India**: Accessible technology for local markets
- **Regional Integration**: Connects markets across linguistic regions

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| Backend | FastAPI (Python) | Fast, async, great for AI |
| AI | Google Gemini API | Free tier, multilingual support |
| Frontend | Vanilla HTML/CSS/JS | Zero build, instant deploy |
| Speech | Web Speech API | Browser-native, free |
| Styling | Custom CSS | Premium dark theme |

---

## 🚀 Deployment

### Render (Recommended)
1. Push to GitHub
2. Connect to [Render](https://render.com)
3. Set environment variable: `GEMINI_API_KEY`
4. Deploy!

### Docker (Coming Soon)
```bash
docker-compose up -d
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful multilingual capabilities
- **Indian Language Communities** for inspiration
- **Viksit Bharat Initiative** for the vision
- **Republic Day Hackathon 2026** organizers

---

**Built with ❤️ for breaking language barriers in Indian markets**

**🇮🇳 For Viksit Bharat**
