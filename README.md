# 👗 FITLAB — AI Fashion Outfit Visualizer

A virtual try-on and style advisor powered by **Claude Vision AI** and **Streamlit**. Upload your photo, pick your style vibes, and receive 3 fully curated outfit concepts — personalised to your body type, skin tone, occasion, season, and budget.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📸 Photo Analysis | Claude reads your body silhouette, skin tone, and current style cues |
| 👗 3 Outfit Concepts | Each with full piece-by-piece breakdown (top, bottom, shoes, bag, accessory) |
| 🎨 Color Palettes | Per-outfit palette with hex swatches and colour names |
| 💡 Why It Works | Each piece explains *why* it flatters your specific features |
| 🪞 Style Persona | Generates your personal style archetype (e.g. "Quiet Luxe Minimalist") |
| 🛍️ Budget Breakdown | Approximate spend per outfit |
| ✦ Signature Piece | One wardrobe game-changer recommended for you |
| ❌ What to Avoid | Honest advice on cuts/styles to skip |
| 💬 Style Tips | 3 personalised universal tips based on your features |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...

# Windows
set ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run
```bash
streamlit run fashion_visualizer.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 🗂️ Project Structure

```
fitlab/
├── fashion_visualizer.py   # Main app
├── requirements.txt        # Dependencies
└── README.md
```

---

## 🛠️ Tech Stack

| Tool | Role |
|---|---|
| [Streamlit](https://streamlit.io) | UI framework |
| [Anthropic Claude](https://anthropic.com) | Vision AI (photo analysis + outfit generation) |
| [Pillow](https://pillow.readthedocs.io) | Image handling |
| Google Fonts | Typography (Cormorant Garamond + Syne) |

---

## 🎨 Styles Supported

Streetwear · Minimalist · Business Casual · Boho · Y2K · Old Money · Grunge · Cottagecore · Athleisure · Avant-Garde · Coastal · Dark Academia · Preppy · Maximalist · Androgynous

---

## 📋 How It Works

1. User uploads a photo (full-body or half-body works best)
2. User selects up to 3 style vibes + occasion, season, budget
3. App sends the image + structured prompt to `claude-sonnet-4-20250514`
4. Claude performs visual body/tone analysis and returns structured JSON
5. Streamlit renders the editorial-style fashion report

---

## 💡 Tips for Best Results

- Use a **well-lit, full-body photo** against a plain background
- Wear **form-fitting or typical clothes** so Claude can read your silhouette accurately
- Select styles that feel aspirational, not just what you currently wear
- Add body notes (e.g. "petite frame, prefer high-waist") for more precise recommendations

---

## 🔑 Requirements

- Python 3.9+
- Anthropic API key → [console.anthropic.com](https://console.anthropic.com)
- Internet connection (Google Fonts + Anthropic API)
