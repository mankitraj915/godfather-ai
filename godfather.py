import os
import random
import requests
import feedparser
import yfinance as yf
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION ---
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
LINKEDIN_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_ID = os.environ.get("LINKEDIN_USER_ID")

genai.configure(api_key=GEMINI_KEY)

# --- 0. THE BRAIN STEM ---
def get_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name: return genai.GenerativeModel(m.name)
    except: pass
    return genai.GenerativeModel('gemini-1.5-flash')

# --- CHANNEL 1: TECH & POWER ---
def get_tech_intel():
    print("📡 CHANNEL: TECH & POWER...")
    intel = {"title": "The Stagnation of Software", "source": "Observation"}
    try:
        top = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:15]
        for id in top:
            s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
            # Expanded Keywords for Power & Tech
            if any(k in s.get('title','').lower() for k in ['ai', 'gpu', 'nvidia', 'crypto', 'saas', 'startup', 'funding', 'silicon', 'china', 'chip']):
                intel = {"title": s['title'], "source": "Hacker News"}
                break
    except: pass
    
    market = "Flat"
    try:
        tick = yf.Ticker("NVDA")
        hist = tick.history(period="1d")
        if not hist.empty:
            chg = ((hist['Close'].iloc[0]-hist['Open'].iloc[0])/hist['Open'].iloc[0])*100
            market = f"NVDA {'UP' if chg>0 else 'DOWN'} {abs(chg):.2f}%"
    except: pass
    return intel, market, "tech"

# --- CHANNEL 2: THE PHILOSOPHICAL SPECTRUM ---
def get_mind_intel():
    print("📡 CHANNEL: OMNISCIENT MIND...")
    topics = [
        # Power & Leadership
        "The Shadow Self in Leadership (Jung)", "The Trap of Mimetic Desire (Girard)", 
        "The Master-Slave Dialectic (Hegel)", "Machiavellian Virtue in Startups",
        "The Sovereign Individual Thesis",
        
        # Reality & Existence
        "The Simulation Hypothesis: Are We NPCs?", "Entropy: Why Order Always Fails",
        "The Fermi Paradox: The Great Filter is Ahead of Us", "Determinism vs. Free Will",
        "Panpsychism: Is the Universe Conscious?",
        
        # The Future
        "Transhumanism: The End of Biological Evolution", 
        "Accelerationism (e/acc) vs. Deceleration", "The Psychology of AGI Alignment"
    ]
    topic = random.choice(topics)
    return {"title": topic, "source": "The Universal Library"}, "Concept", "mind"

# --- CHANNEL 3: THE HARD SCIENCE FRONTIER ---
def get_science_intel():
    print("📡 CHANNEL: DEEP SCIENCE...")
    
    # 🎲 THE EXPANDED ROSETTA STONE 🎲
    domains = {
        # Biology & Life (The Immortality Pillar)
        "genetics": "cat:q-bio.GN",       # Genomics / CRISPR
        "neuro": "cat:q-bio.NC",          # Neuroscience / BCI
        
        # Intelligence (The God Pillar)
        "ai": "cat:cs.AI",                # Artificial Intelligence
        "ml": "cat:cs.LG",                # Machine Learning
        
        # Physics & Reality (The Truth Pillar)
        "quantum": "cat:quant-ph",        # Quantum Physics
        "complexity": "cat:nlin.AO",      # Complex Systems / Chaos Theory
        
        # Power & Math (The Control Pillar)
        "game_theory": "cat:cs.GT",       # Computer Science Game Theory
        "crypto": "cat:cs.CR"             # Cryptography / Security
    }
    
    domain_name, query_code = random.choice(list(domains.items()))
    print(f"   -> Domain Selected: {domain_name.upper()}")

    try:
        # Fetch high-impact papers
        url = f'http://export.arxiv.org/api/query?search_query={query_code}&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending'
        feed = feedparser.parse(url)
        entry = random.choice(feed.entries)
        return {"title": entry.title.replace('\n', ' '), "source": f"ArXiv ({domain_name.upper()})"}, domain_name, "science"
    except:
        return get_mind_intel() # Fallback

# --- THE ARTIST (Adaptive "Spectrum" Visuals) ---
def generate_chart(mode, sub_mode):
    print("🎨 ARTIST: Painting...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10)) # Square for Mobile
    x = np.linspace(0, 10, 100)
    
    if mode == "tech":
        # Neon Green Stock Chart
        y = np.sin(x) * np.exp(0.1*x) + np.random.normal(0, 0.1, 100)
        color = '#00ff41'
        
    elif mode == "mind":
        # Purple Haze (Philosophy)
        y = np.sin(x) * np.cos(x*2) * np.exp(0.2*x)
        color = '#bd00ff'
        
    elif mode == "science":
        # Adaptive Science Colors
        if sub_mode == "genetics": 
            color, y = '#ff0055', np.sin(x*3) + np.cos(x*3) # DNA Red
        elif sub_mode == "neuro":
            color, y = '#00d0ff', np.random.normal(0, 0.5, 100) # Electric Blue
        elif sub_mode == "quantum":
            color, y = '#ffffff', np.sin(x**2) # White Interference
        elif sub_mode in ["game_theory", "crypto"]:
            color, y = '#ffff00', np.abs(np.sin(x*4)) # Logic Yellow
        else: # AI / ML / Complexity
            color, y = '#ff9900', np.exp(0.3 * x) # Amber Growth
            
    ax.plot(x, y, color=color, linewidth=8, alpha=0.3) # Glow
    ax.plot(x, y, color=color, linewidth=3) # Core
    
    # Text Overlay
    label = sub_mode.upper() if mode == "science" else sub_mode.upper() if mode == "tech" else "CONCEPT"
    ax.text(5, 5, f"{label}", fontsize=20, color='white', ha='center', alpha=0.15, fontname='monospace', weight='bold')
    ax.set_title(f"// GODFATHER ANALYTICS: {label} //", color='white', fontname='monospace')
    ax.axis('off')
    
    filename = "visual.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight', facecolor='#050505')
    plt.close()
    return filename

# --- THE NARRATOR (TITAN MODE) ---
def generate_post(intel, sub_mode, mode):
    print("🧠 BRAIN: Writing Manifesto...")
    model = get_model()
    
    base_instructions = """
    Write a LONG, high-status LinkedIn essay (1500-2000 chars).
    Formatting: BOLD headers, bullet points, double spacing.
    Tone: Intellectual, Visionary, 'Larger than Life'.
    """

    if mode == "tech":
        prompt = f"""
        {base_instructions}
        Role: Visionary Tech VC.
        Topic: "{intel['title']}" ({intel['source']}).
        Context: Market is {sub_mode}.
        Structure:
        1. THE HOOK: Contrarian take.
        2. THE REALITY: Technical/Financial truth.
        3. THE PREDICTION: 5-year outlook.
        4. THE LESSON: Advice for builders.
        """
    elif mode == "mind":
        prompt = f"""
        {base_instructions}
        Role: Philosopher King.
        Topic: "{intel['title']}".
        Structure:
        1. THE PARADOX: Why this ancient concept explains modern failure.
        2. THE MECHANISM: How it works psychologically.
        3. THE APPLICATION: Apply to coding/leadership.
        4. THE COMMAND: Final philosophical order.
        """
    else: # SCIENCE
        prompt = f"""
        {base_instructions}
        Role: Director of Future R&D.
        Paper: "{intel['title']}" (Source: {intel['source']}).
        Field: {sub_mode.upper()}.
        Structure:
        1. THE BREAKTHROUGH: Explain the discovery simply but profoundly.
        2. THE SHIFT: How this changes Biology/Physics/Compute.
        3. THE FUTURE: Speculate on the massive implications (Utopia or Horror).
        4. THE VERDICT: Hype or Standard?
        """

    return model.generate_content(prompt).text.strip()

# --- PUBLISHER ---
def post_to_linkedin(text, image_path):
    print("🚀 PUBLISHER: Uploading...")
    headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}", "Content-Type": "application/json"}
    
    if not LINKEDIN_ID:
        try:
            r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
            if r.status_code == 200: urn = f"urn:li:person:{r.json()['sub']}"
            else: urn = f"urn:li:person:{requests.get('https://api.linkedin.com/v2/me', headers=headers).json()['id']}"
        except: return print("❌ Auth Failed")
    else: urn = LINKEDIN_ID

    reg = requests.post("https://api.linkedin.com/v2/assets?action=registerUpload", headers=headers, json={
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": urn,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
        }
    })
    
    if reg.status_code != 200: return print(f"❌ Image Error: {reg.text}")
    
    upload_url = reg.json()['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset_urn = reg.json()['value']['asset']
    
    with open(image_path, 'rb') as f: requests.put(upload_url, headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"}, data=f)

    res = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json={
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": text},
            "shareMediaCategory": "IMAGE",
            "media": [{"status": "READY", "media": asset_urn, "title": {"text": "Insight"}}]
        }},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    })
    
    if res.status_code == 201: print("✅ GODFATHER HAS SPOKEN.")
    else: print(f"❌ Post Error: {res.text}")

# --- MAIN LOOP ---
if __name__ == "__main__":
    # Equal weight to ensure diversity across the spectrum
    choice = random.choice(["tech", "mind", "science"])
    
    if choice == "tech": intel, extra, mode = get_tech_intel()
    elif choice == "mind": intel, extra, mode = get_mind_intel()
    else: intel, extra, mode = get_science_intel()
    
    chart = generate_chart(mode, extra)
    post = generate_post(intel, extra, mode)
    post_to_linkedin(post, chart)
