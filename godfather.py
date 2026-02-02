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

# --- CHANNEL 1: TECH & MARKETS ---
def get_tech_intel():
    print("📡 CHANNEL: TECH...")
    intel = {"title": "The Stagnation of Software", "source": "Observation"}
    try:
        top = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:10]
        for id in top:
            s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
            if any(k in s.get('title','').lower() for k in ['ai','gpu','nvidia','crypto','startup']):
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

# --- CHANNEL 2: PHILOSOPHY & PSYCHOLOGY ---
def get_mind_intel():
    print("📡 CHANNEL: MIND...")
    topics = [
        "Jungian Shadow in AI", "Stoicism for Founders", "Vedantic Non-Dualism", 
        "Nietzsche's Will to Power", "The Lacanian Mirror Stage", "Baudrillard's Hyperreality",
        "Camus and The Absurd", "Girard's Mimetic Desire", "The Psychology of Flow", "Biocentrism"
    ]
    topic = random.choice(topics)
    return {"title": topic, "source": "Internal Library"}, "Concept", "mind"

# --- CHANNEL 3: UNIVERSAL SCIENCE (Genetics, Neuro, CS, AI) ---
def get_science_intel():
    print("📡 CHANNEL: SCIENCE...")
    
    # 🎲 THE ACADEMIC ROULETTE 🎲
    domains = {
        "genetics": "cat:q-bio.GN",       # Genomics
        "neuro": "cat:q-bio.NC",          # Neuroscience
        "ai": "cat:cs.AI",                # Artificial Intelligence
        "ml": "cat:cs.LG",                # Machine Learning
        "niche": "cat:cs.CY"              # Computers and Society (Viral/Niche)
    }
    
    domain_name, query_code = random.choice(list(domains.items()))
    print(f"   -> Domain Selected: {domain_name.upper()}")

    try:
        # Fetch latest paper from ArXiv
        url = f'http://export.arxiv.org/api/query?search_query={query_code}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending'
        feed = feedparser.parse(url)
        entry = random.choice(feed.entries)
        
        # Clean title
        title = entry.title.replace('\n', ' ')
        return {"title": title, "source": f"ArXiv ({domain_name.upper()})"}, domain_name, "science"
    except:
        return get_mind_intel() # Fallback

# --- THE ARTIST (Adaptive Visuals) ---
def generate_chart(mode, sub_mode):
    print("🎨 ARTIST: Painting...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
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
            color = '#ff0055' # DNA Red
            y = np.sin(x*3) + np.cos(x*3) # Double Helix-ish
        elif sub_mode == "neuro":
            color = '#00d0ff' # Electric Blue
            y = np.random.normal(0, 0.5, 100) # Neural Spikes
        else: # AI / CS
            color = '#ff9900' # Amber Terminal
            y = np.exp(0.3 * x) # Exponential Growth
            
    ax.plot(x, y, color=color, linewidth=8, alpha=0.3) # Glow
    ax.plot(x, y, color=color, linewidth=2) # Core
    
    label = sub_mode if mode == "science" else "ANALYSIS"
    ax.set_title(f"// SYSTEM OUTPUT: {label.upper()} //", color='white', fontname='monospace')
    ax.axis('off')
    
    filename = "visual.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight', facecolor='#050505')
    plt.close()
    return filename

# --- THE NARRATOR ---
def generate_post(intel, sub_mode, mode):
    print("🧠 BRAIN: Thinking...")
    model = get_model()
    
    if mode == "tech":
        prompt = f"""
        Role: Cynical Tech Godfather.
        Topic: "{intel['title']}" from {intel['source']}.
        Context: Market is {sub_mode}.
        Task: Write a LinkedIn post (max 500 chars). Connect news to power/money.
        """
    elif mode == "mind":
        prompt = f"""
        Role: Modern Philosopher.
        Topic: "{intel['title']}".
        Task: Write a LinkedIn post (max 500 chars). Apply this deep concept to modern work/life.
        Tone: Mystical but actionable.
        """
    else: # SCIENCE
        prompt = f"""
        Role: R&D Director.
        Paper: "{intel['title']}" (Source: {intel['source']}).
        Field: {sub_mode.upper()}.
        Task: Write a LinkedIn post (max 500 chars). 
        - If Genetics: Discuss modifying the source code of life.
        - If Neuro: Discuss the hardware of the mind.
        - If AI/ML: Discuss the optimization of intelligence.
        Tone: Visionary, slightly dangerous excitement.
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
    upload_url = reg.json()['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset_urn = reg.json()['value']['asset']
    
    with open(image_path, 'rb') as f: requests.put(upload_url, headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"}, data=f)

    requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json={
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": text},
            "shareMediaCategory": "IMAGE",
            "media": [{"status": "READY", "media": asset_urn, "title": {"text": "Insight"}}]
        }},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    })
    print("✅ GODFATHER HAS SPOKEN.")

# --- MAIN LOOP ---
if __name__ == "__main__":
    # 40% Chance Tech, 40% Chance Science, 20% Chance Philosophy
    choice = random.choices(["tech", "science", "mind"], weights=[40, 40, 20], k=1)[0]
    
    if choice == "tech": intel, extra, mode = get_tech_intel()
    elif choice == "mind": intel, extra, mode = get_mind_intel()
    else: intel, extra, mode = get_science_intel()
    
    chart = generate_chart(mode, extra)
    post = generate_post(intel, extra, mode)
    post_to_linkedin(post, chart)
