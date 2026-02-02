import os
import time
import random
import requests
import feedparser
import yfinance as yf
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
from google.api_core.exceptions import ResourceExhausted

# --- CONFIGURATION ---
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
LINKEDIN_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_ID = os.environ.get("LINKEDIN_USER_ID")

genai.configure(api_key=GEMINI_KEY)

# --- 0. THE BRAIN STEM ---
def get_model():
    # Priority List of Models to Try
    models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro']
    for m in models:
        try:
            return genai.GenerativeModel(m)
        except: continue
    return genai.GenerativeModel('gemini-1.5-flash')

# --- CHANNEL 1: TECH & POWER ---
def get_tech_intel():
    print("📡 CHANNEL: TECH & POWER...")
    intel = {"title": "The Stagnation of Software", "source": "Observation"}
    try:
        top = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:15]
        for id in top:
            s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
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
        "The Shadow Self in Leadership (Jung)", "The Trap of Mimetic Desire (Girard)", 
        "The Master-Slave Dialectic (Hegel)", "Machiavellian Virtue in Startups",
        "The Sovereign Individual Thesis", "The Simulation Hypothesis", 
        "Entropy: Why Order Always Fails", "The Fermi Paradox", 
        "Determinism vs. Free Will", "Panpsychism",
        "Transhumanism", "Accelerationism (e/acc)"
    ]
    topic = random.choice(topics)
    return {"title": topic, "source": "The Universal Library"}, "Concept", "mind"

# --- CHANNEL 3: THE HARD SCIENCE FRONTIER ---
def get_science_intel():
    print("📡 CHANNEL: DEEP SCIENCE...")
    domains = {
        "genetics": "cat:q-bio.GN", "neuro": "cat:q-bio.NC",
        "ai": "cat:cs.AI", "ml": "cat:cs.LG",
        "quantum": "cat:quant-ph", "complexity": "cat:nlin.AO",
        "game_theory": "cat:cs.GT", "crypto": "cat:cs.CR"
    }
    domain_name, query_code = random.choice(list(domains.items()))
    print(f"   -> Domain Selected: {domain_name.upper()}")

    try:
        url = f'http://export.arxiv.org/api/query?search_query={query_code}&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending'
        feed = feedparser.parse(url)
        entry = random.choice(feed.entries)
        return {"title": entry.title.replace('\n', ' '), "source": f"ArXiv ({domain_name.upper()})"}, domain_name, "science"
    except: return get_mind_intel()

# --- THE ARTIST ---
def generate_chart(mode, sub_mode):
    print("🎨 ARTIST: Painting...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.linspace(0, 10, 100)
    
    if mode == "tech":
        y = np.sin(x) * np.exp(0.1*x) + np.random.normal(0, 0.1, 100)
        color = '#00ff41'
    elif mode == "mind":
        y = np.sin(x) * np.cos(x*2) * np.exp(0.2*x)
        color = '#bd00ff'
    elif mode == "science":
        if sub_mode == "genetics": color, y = '#ff0055', np.sin(x*3) + np.cos(x*3)
        elif sub_mode == "neuro": color, y = '#00d0ff', np.random.normal(0, 0.5, 100)
        elif sub_mode == "quantum": color, y = '#ffffff', np.sin(x**2)
        elif sub_mode in ["game_theory", "crypto"]: color, y = '#ffff00', np.abs(np.sin(x*4))
        else: color, y = '#ff9900', np.exp(0.3 * x)
            
    ax.plot(x, y, color=color, linewidth=8, alpha=0.3)
    ax.plot(x, y, color=color, linewidth=3)
    label = sub_mode.upper() if mode == "science" else sub_mode.upper() if mode == "tech" else "CONCEPT"
    ax.text(5, 5, f"{label}", fontsize=20, color='white', ha='center', alpha=0.15, fontname='monospace', weight='bold')
    ax.set_title(f"// GODFATHER ANALYTICS: {label} //", color='white', fontname='monospace')
    ax.axis('off')
    filename = "visual.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight', facecolor='#050505')
    plt.close()
    return filename

# --- THE NARRATOR (WITH RETRY LOGIC) ---
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
        Role: Visionary Tech VC. Topic: "{intel['title']}" ({intel['source']}). Context: {sub_mode}.
        Structure: 1. HOOK 2. REALITY 3. PREDICTION 4. LESSON.
        """
    elif mode == "mind":
        prompt = f"""
        {base_instructions}
        Role: Philosopher King. Topic: "{intel['title']}".
        Structure: 1. PARADOX 2. MECHANISM 3. APPLICATION 4. COMMAND.
        """
    else: 
        prompt = f"""
        {base_instructions}
        Role: R&D Director. Paper: "{intel['title']}" (Source: {intel['source']}). Field: {sub_mode.upper()}.
        Structure: 1. BREAKTHROUGH 2. SHIFT 3. FUTURE 4. VERDICT.
        """

    # RETRY LOOP FOR 429 ERRORS
    for attempt in range(3):
        try:
            return model.generate_content(prompt).text.strip()
        except ResourceExhausted:
            print(f"⚠️ Quota Hit. Waiting 20 seconds (Attempt {attempt+1}/3)...")
            time.sleep(20)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return "Analysis Failed."
            
    return "System Overload. Try again later."

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
    choice = random.choice(["tech", "mind", "science"])
    if choice == "tech": intel, extra, mode = get_tech_intel()
    elif choice == "mind": intel, extra, mode = get_mind_intel()
    else: intel, extra, mode = get_science_intel()
    
    chart = generate_chart(mode, extra)
    post = generate_post(intel, extra, mode)
    post_to_linkedin(post, chart)
