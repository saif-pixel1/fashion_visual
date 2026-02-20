import streamlit as st
import anthropic
import base64
import json
import re
from PIL import Image
import io

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FITLAB — AI Fashion Visualizer",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --ink:     #0e0c0a;
    --paper:   #f5f0e8;
    --cream:   #ede7d9;
    --blush:   #d4a49a;
    --rose:    #b5706a;
    --slate:   #6b6560;
    --gold:    #c9a84c;
    --muted:   #9e9790;
    --white:   #fdfcfa;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: var(--paper) !important;
    color: var(--ink) !important;
    font-family: 'Syne', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── HEADER ── */
.fitlab-header {
    background: var(--ink);
    padding: 1.25rem 3rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #2a2620;
}
.fitlab-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.5rem;
    color: var(--paper);
    letter-spacing: 0.15em;
}
.fitlab-logo span { color: var(--blush); }
.fitlab-tagline {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    color: var(--muted);
    font-size: 0.95rem;
    letter-spacing: 0.05em;
}

/* ── LAYOUT ── */
.main-grid {
    display: grid;
    grid-template-columns: 360px 1fr;
    min-height: calc(100vh - 64px);
}
.panel-left {
    background: var(--white);
    border-right: 1px solid var(--cream);
    padding: 2rem 1.75rem;
    overflow-y: auto;
}
.panel-right {
    background: var(--paper);
    padding: 2.5rem 3rem;
    overflow-y: auto;
}

/* ── SECTION LABELS ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--cream);
}

/* ── UPLOAD ZONE ── */
.upload-zone {
    border: 1.5px dashed var(--blush);
    border-radius: 4px;
    padding: 2.5rem 1rem;
    text-align: center;
    cursor: pointer;
    background: linear-gradient(135deg, #fdf9f5 0%, #f8f2ea 100%);
    transition: all 0.2s;
    margin-bottom: 1.5rem;
}
.upload-zone:hover {
    border-color: var(--rose);
    background: linear-gradient(135deg, #fef5f3 0%, #f9ece9 100%);
}
.upload-icon { font-size: 2.5rem; margin-bottom: 0.5rem; opacity: 0.5; }
.upload-text { font-size: 0.8rem; color: var(--muted); line-height: 1.5; }

/* ── STYLE TAGS ── */
.style-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}
.style-tag {
    padding: 0.35rem 0.85rem;
    border-radius: 2px;
    border: 1px solid var(--cream);
    background: var(--white);
    font-size: 0.78rem;
    color: var(--slate);
    cursor: pointer;
    transition: all 0.15s;
    letter-spacing: 0.03em;
}
.style-tag:hover { border-color: var(--blush); color: var(--rose); }
.style-tag.active { background: var(--ink); color: var(--paper); border-color: var(--ink); }

/* ── CTA BUTTON ── */
div[data-testid="stButton"] > button {
    background: var(--ink) !important;
    color: var(--paper) !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 0.85rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--rose) !important;
}

/* ── STREAMLIT WIDGET OVERRIDES ── */
label[data-testid="stWidgetLabel"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div,
[data-testid="stTextArea"] textarea {
    background: var(--white) !important;
    border: 1px solid var(--cream) !important;
    border-radius: 2px !important;
    color: var(--ink) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
}
[data-testid="stFileUploader"] {
    border: 1.5px dashed var(--blush) !important;
    border-radius: 4px !important;
    background: linear-gradient(135deg, #fdf9f5 0%, #f8f2ea 100%) !important;
    padding: 0.5rem !important;
}
[data-testid="stFileUploader"] label { display: none !important; }

/* ── RESULT CARDS ── */
.result-hero {
    background: var(--white);
    border: 1px solid var(--cream);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 2rem;
    position: relative;
}
.result-hero-img {
    width: 100%;
    max-height: 500px;
    object-fit: cover;
}
.result-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: var(--ink);
    color: var(--paper);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.35rem 0.75rem;
}

.outfit-card {
    background: var(--white);
    border: 1px solid var(--cream);
    border-radius: 4px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.outfit-card:hover { border-color: var(--blush); }
.outfit-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 0.25rem;
}
.outfit-occasion {
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--rose);
    margin-bottom: 0.75rem;
}
.outfit-desc {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    color: var(--slate);
    line-height: 1.7;
    margin-bottom: 1rem;
}
.piece-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}
.piece-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.82rem;
    color: var(--slate);
    padding: 0.4rem 0;
    border-bottom: 1px solid var(--cream);
}
.piece-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--blush);
    flex-shrink: 0;
}
.piece-type {
    font-weight: 600;
    color: var(--ink);
    min-width: 80px;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Color chips */
.palette-row {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
    flex-wrap: wrap;
    align-items: center;
}
.color-chip {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 2px solid var(--cream);
    flex-shrink: 0;
}

/* Analysis box */
.analysis-box {
    background: var(--ink);
    color: var(--paper);
    padding: 1.5rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}
.analysis-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.1em;
    color: var(--blush);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    font-size: 0.7rem;
}
.analysis-text {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1.05rem;
    line-height: 1.8;
    color: #d5cfc4;
}

/* Tips */
.tip-row {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--cream);
    font-size: 0.85rem;
    color: var(--slate);
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem;
    line-height: 1.5;
}
.tip-num {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.65rem;
    color: var(--rose);
    min-width: 20px;
    margin-top: 3px;
}

/* Placeholder */
.placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
    opacity: 0.4;
}
.placeholder-icon { font-size: 4rem; margin-bottom: 1rem; }
.placeholder-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem;
    color: var(--ink);
    margin-bottom: 0.5rem;
}
.placeholder-sub { font-size: 0.85rem; color: var(--slate); }

/* Streamlit image */
[data-testid="stImage"] { border-radius: 4px; }

/* Info strip */
.info-strip {
    display: flex;
    gap: 0;
    border: 1px solid var(--cream);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.info-cell {
    flex: 1;
    padding: 0.75rem 1rem;
    border-right: 1px solid var(--cream);
    text-align: center;
}
.info-cell:last-child { border-right: none; }
.info-val {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--ink);
}
.info-lbl {
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
}

div[data-testid="stSpinner"] p { font-family: 'Syne', sans-serif; font-size: 0.8rem; letter-spacing: 0.1em; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="fitlab-header">
    <div class="fitlab-logo">FIT<span>LAB</span></div>
    <div class="fitlab-tagline">AI-Powered Virtual Try-On & Style Advisor</div>
    <div style="font-size:0.7rem; color:#4a4540; letter-spacing:0.1em;">POWERED BY CLAUDE</div>
</div>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def img_to_b64(image_bytes: bytes) -> str:
    return base64.standard_b64encode(image_bytes).decode("utf-8")

def get_image_b64_from_upload(uploaded_file) -> str:
    return img_to_b64(uploaded_file.getvalue())

STYLES = [
    "Streetwear", "Minimalist", "Business Casual", "Boho", "Y2K",
    "Old Money", "Grunge", "Cottagecore", "Athleisure", "Avant-Garde",
    "Coastal", "Dark Academia", "Preppy", "Maximalist", "Androgynous"
]

OCCASIONS = ["Everyday", "Work", "Date Night", "Party", "Outdoor", "Formal", "Festival", "Travel"]
SEASONS   = ["Spring", "Summer", "Autumn", "Winter", "All-Season"]
BUDGETS   = ["Under ₹2K", "₹2K–5K", "₹5K–10K", "₹10K–20K", "Luxury"]

# ── Session State ─────────────────────────────────────────────────────────────
if "selected_styles" not in st.session_state:
    st.session_state.selected_styles = ["Minimalist"]
if "result" not in st.session_state:
    st.session_state.result = None
if "user_photo_b64" not in st.session_state:
    st.session_state.user_photo_b64 = None
if "user_photo_mime" not in st.session_state:
    st.session_state.user_photo_mime = "image/jpeg"

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1.1, 2.2], gap="small")

# ════════════════════════════════════════════════════════════════════
# LEFT PANEL
# ════════════════════════════════════════════════════════════════════
with left:
    st.markdown('<div class="section-label">📸 Your Photo</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        help="Upload a full-body or half-body photo for best results"
    )

    if uploaded:
        st.session_state.user_photo_b64   = get_image_b64_from_upload(uploaded)
        st.session_state.user_photo_mime  = uploaded.type
        img = Image.open(uploaded)
        st.image(img, use_container_width=True, caption="Your photo")
    else:
        st.markdown("""
        <div class="upload-zone">
            <div class="upload-icon">🧍</div>
            <div class="upload-text">Upload a full-body photo<br>JPG · PNG · WEBP</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label" style="margin-top:1.25rem;">✦ Style Vibes</div>', unsafe_allow_html=True)
    st.caption("Select up to 3 styles")
    
    # Style selector using multiselect for simplicity + visual display
    chosen = st.multiselect(
        "Styles",
        STYLES,
        default=st.session_state.selected_styles,
        max_selections=3,
        label_visibility="collapsed",
    )
    st.session_state.selected_styles = chosen if chosen else ["Minimalist"]

    st.markdown('<div class="section-label" style="margin-top:1.25rem;">⚙️ Preferences</div>', unsafe_allow_html=True)

    occasion = st.selectbox("Occasion", OCCASIONS)
    season   = st.selectbox("Season",   SEASONS)
    budget   = st.selectbox("Budget",   BUDGETS)

    body_notes = st.text_input(
        "Body type / fit preferences (optional)",
        placeholder="e.g. petite, prefer loose fits, hide midsection…"
    )
    extra = st.text_area(
        "Special requests (optional)",
        placeholder="e.g. I love earthy tones, avoid synthetic fabric…",
        height=70,
    )

    st.markdown("---")
    generate = st.button("✦  GENERATE OUTFIT LOOKS")

# ════════════════════════════════════════════════════════════════════
# RIGHT PANEL
# ════════════════════════════════════════════════════════════════════
with right:

    if generate:
        if not st.session_state.user_photo_b64:
            st.warning("Please upload a photo first.")
            st.stop()

        styles_str = ", ".join(st.session_state.selected_styles)

        system_prompt = """You are FITLAB's elite AI fashion stylist — part visionary creative director, part personal shopper. 
You analyze the user's photo to understand body proportions, skin tone, current outfit, and personal aesthetic cues.
You then craft 3 complete, wearable outfit concepts that flatter them specifically.
Always respond in valid JSON only — no markdown, no preamble."""

        user_prompt = f"""Analyze the person in this photo and create 3 distinct outfit concepts for them.

Style preferences: {styles_str}
Occasion: {occasion}
Season: {season}
Budget range: {budget}
Body/fit notes: {body_notes if body_notes else 'Not specified'}
Special requests: {extra if extra else 'None'}

Respond ONLY with a JSON object in exactly this structure:
{{
  "person_analysis": {{
    "skin_tone": "describe undertone briefly",
    "body_silhouette": "describe shape/proportions briefly",
    "current_style_cue": "what their current look suggests",
    "style_persona": "2-3 word style archetype e.g. 'Quiet Luxe Minimalist'"
  }},
  "outfits": [
    {{
      "name": "Outfit name (evocative, 2-4 words)",
      "occasion_fit": "Best for...",
      "vibe": "One sentence mood/vibe",
      "description": "2-3 sentences describing how this outfit looks on them specifically, referencing their features",
      "pieces": [
        {{"type": "Top", "item": "specific item with color/material", "why": "why it flatters them"}},
        {{"type": "Bottom", "item": "specific item with color/material", "why": "why it works"}},
        {{"type": "Shoes", "item": "specific footwear", "why": "completes the look"}},
        {{"type": "Bag", "item": "bag/accessory", "why": "ties it together"}},
        {{"type": "Accessory", "item": "jewelry/belt/hat etc", "why": "adds personality"}}
      ],
      "color_palette": ["#hex1", "#hex2", "#hex3", "#hex4"],
      "palette_names": ["Color 1 name", "Color 2 name", "Color 3 name", "Color 4 name"],
      "styling_tip": "One specific tip for wearing this outfit best",
      "budget_breakdown": "Approximate total cost breakdown"
    }}
  ],
  "universal_tips": [
    "Personalized tip 1 based on their features",
    "Personalized tip 2",
    "Personalized tip 3"
  ],
  "signature_piece": "The one statement piece that would transform their wardrobe",
  "avoid": "What styles/cuts to generally avoid and why"
}}"""

        with st.spinner("Analyzing your photo & crafting looks…"):
            try:
                client = anthropic.Anthropic()
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=3000,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": st.session_state.user_photo_mime,
                                    "data": st.session_state.user_photo_b64,
                                }
                            },
                            {"type": "text", "text": user_prompt}
                        ]
                    }]
                )

                raw = response.content[0].text.strip()
                raw = re.sub(r'^```json\s*', '', raw)
                raw = re.sub(r'^```\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)
                st.session_state.result = json.loads(raw)

            except json.JSONDecodeError as e:
                st.error(f"Parsing error: {e}")
                st.stop()
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

    # ── RENDER RESULTS ────────────────────────────────────────────────
    if st.session_state.result:
        data = st.session_state.result
        pa   = data.get("person_analysis", {})

        # Analysis Box
        st.markdown(f"""
        <div class="analysis-box">
            <div class="analysis-title">✦ Style Profile Analysis</div>
            <div class="analysis-text">
                You carry a <strong style="color:#e8c9a0;">{pa.get('style_persona','')}</strong> energy — 
                {pa.get('skin_tone','')} with {pa.get('body_silhouette','')}. 
                Your current look signals <em>{pa.get('current_style_cue','')}</em>. 
                These three looks are curated to elevate exactly that.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Info Strip
        styles_disp = " · ".join(st.session_state.selected_styles)
        st.markdown(f"""
        <div class="info-strip">
            <div class="info-cell"><div class="info-val">{len(data.get('outfits',[]))}</div><div class="info-lbl">Looks</div></div>
            <div class="info-cell"><div class="info-val">{occasion}</div><div class="info-lbl">Occasion</div></div>
            <div class="info-cell"><div class="info-val">{season}</div><div class="info-lbl">Season</div></div>
            <div class="info-cell"><div class="info-val">{budget}</div><div class="info-lbl">Budget</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Outfits ────────────────────────────────────────────────
        for i, outfit in enumerate(data.get("outfits", []), 1):
            pieces  = outfit.get("pieces", [])
            palette = outfit.get("color_palette", [])
            pnames  = outfit.get("palette_names", [])

            # Header
            st.markdown(f"""
            <div class="outfit-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-size:0.62rem; letter-spacing:0.15em; text-transform:uppercase; 
                                    color:var(--muted); margin-bottom:0.2rem;">LOOK {i:02d}</div>
                        <div class="outfit-name">{outfit.get('name','')}</div>
                        <div class="outfit-occasion">{outfit.get('occasion_fit','')}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.7rem; color:var(--muted); font-style:italic; 
                                    font-family:'Cormorant Garamond',serif;">
                            {outfit.get('vibe','')}
                        </div>
                    </div>
                </div>
                <div class="outfit-desc">{outfit.get('description','')}</div>
            """, unsafe_allow_html=True)

            # Pieces
            st.markdown('<div class="piece-list">', unsafe_allow_html=True)
            for piece in pieces:
                st.markdown(f"""
                <div class="piece-item">
                    <div class="piece-dot"></div>
                    <div class="piece-type">{piece.get('type','')}</div>
                    <div style="flex:1;">{piece.get('item','')}</div>
                    <div style="font-size:0.75rem; color:var(--muted); font-family:'Cormorant Garamond',serif; 
                                font-style:italic; max-width:140px; text-align:right;">
                        {piece.get('why','')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Palette
            if palette:
                chips = "".join([
                    f'<div title="{pnames[j] if j < len(pnames) else ""}" class="color-chip" style="background:{c};"></div>'
                    for j, c in enumerate(palette)
                ])
                pname_str = " · ".join(pnames) if pnames else ""
                st.markdown(f"""
                <div class="palette-row">
                    <span style="font-size:0.65rem; letter-spacing:0.1em; text-transform:uppercase; 
                                 color:var(--muted);">PALETTE</span>
                    {chips}
                    <span style="font-size:0.78rem; color:var(--slate); font-family:'Cormorant Garamond',serif;">
                        {pname_str}
                    </span>
                </div>
                """, unsafe_allow_html=True)

            # Styling Tip + Budget
            tip_txt    = outfit.get('styling_tip','')
            budget_txt = outfit.get('budget_breakdown','')
            st.markdown(f"""
                <div style="margin-top:1rem; padding:0.85rem; background:var(--cream); border-radius:3px;
                            display:flex; gap:1.5rem; flex-wrap:wrap;">
                    <div style="flex:1; min-width:200px;">
                        <div style="font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; 
                                    color:var(--rose); margin-bottom:0.25rem;">✦ Styling Tip</div>
                        <div style="font-family:'Cormorant Garamond',serif; font-size:0.95rem; 
                                    color:var(--slate);">{tip_txt}</div>
                    </div>
                    <div style="min-width:140px; text-align:right;">
                        <div style="font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; 
                                    color:var(--muted); margin-bottom:0.25rem;">BUDGET</div>
                        <div style="font-family:'Cormorant Garamond',serif; font-size:0.9rem; 
                                    color:var(--slate);">{budget_txt}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Universal Tips ─────────────────────────────────────────
        tips = data.get("universal_tips", [])
        if tips:
            st.markdown("""
            <div style="margin-top:1.5rem;">
                <div class="section-label">✦ Personalized Style Tips</div>
            """, unsafe_allow_html=True)
            for idx, tip in enumerate(tips, 1):
                st.markdown(f"""
                <div class="tip-row">
                    <div class="tip-num">0{idx}</div>
                    <div>{tip}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Signature Piece + Avoid ────────────────────────────────
        sig = data.get("signature_piece", "")
        avoid = data.get("avoid", "")
        if sig or avoid:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="outfit-card" style="border-left: 3px solid var(--gold);">
                    <div style="font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; 
                                color:var(--gold); margin-bottom:0.5rem;">✦ Signature Statement Piece</div>
                    <div style="font-family:'Cormorant Garamond',serif; font-size:1.05rem; 
                                line-height:1.6; color:var(--ink);">{sig}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="outfit-card" style="border-left: 3px solid var(--rose);">
                    <div style="font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; 
                                color:var(--rose); margin-bottom:0.5rem;">✦ What to Avoid</div>
                    <div style="font-family:'Cormorant Garamond',serif; font-size:1.05rem; 
                                line-height:1.6; color:var(--ink);">{avoid}</div>
                </div>""", unsafe_allow_html=True)

    elif not generate:
        st.markdown("""
        <div class="placeholder">
            <div class="placeholder-icon">👗</div>
            <div class="placeholder-title">Your Looks Await</div>
            <div class="placeholder-sub">
                Upload your photo · Choose your styles · Hit Generate<br>
                Get 3 personalised outfit concepts crafted by AI
            </div>
        </div>
        """, unsafe_allow_html=True)
