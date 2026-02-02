import os
import time
import random
import requests
import feedparser
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import json

# --- CONFIGURATION: THE DECA-HYDRA (10 KEYS) ---
KEYS = []
if os.environ.get("GEMINI_API_KEY"): KEYS.append(os.environ.get("GEMINI_API_KEY"))
for i in range(2, 11):
    k = os.environ.get(f"GEMINI_API_KEY_{i}")
    if k: KEYS.append(k)

VALID_KEYS = KEYS
CURRENT_KEY_INDEX = 0

LINKEDIN_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_ID = os.environ.get("LINKEDIN_USER_ID")

# --- 0. THE BARE METAL ENGINE (Direct API Calls) ---
def generate_text_bare_metal(prompt):
    global CURRENT_KEY_INDEX
    if not VALID_KEYS: return None

    # List of models to hit directly (URL endpoints)
    models = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash-exp"
    ]

    # Try up to 15 times (Keys * Models)
    for attempt in range(15):
        key = VALID_KEYS[CURRENT_KEY_INDEX]
        
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            try:
                # print(f"   ... Pinging {model} on Key #{CURRENT_KEY_INDEX+1}")
                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                if response.status_code == 200:
                    try:
                        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                    except:
                        continue # Malformed response, try next
                elif response.status_code == 429:
                    print(f"⚠️ Key #{CURRENT_KEY_INDEX+1} Quota Exceeded (429).")
                    break # Break inner loop to rotate key
                else:
                    # print(f"   ... Error {response.status_code}: {response.text[:100]}")
                    continue # Try next model
                    
            except Exception as e:
                continue

        # If we broke out of the model loop, it means we need to rotate keys
        if len(VALID_KEYS) > 1:
            CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(VALID_KEYS)
            print(f"🔄 Switching to API Key #{CURRENT_KEY_INDEX + 1}...")
            time.sleep(1)
            
    return None

# --- 1. DEPARTMENT OF PHILOSOPHY & PSYCHOANALYSIS ---
def get_humanities_intel():
    print("📡 CHANNEL: HIGH HUMANITIES...")
    library = {
        "psychoanalysis": [
            "The Mirror Stage (Jacques Lacan)", "The Shadow & Persona (Carl Jung)", 
            "The Death Drive (Sigmund Freud)", "The Inferiority Complex (Alfred Adler)",
            "The Real vs The Symbolic (Lacan)"
        ],
        "philosophy": [
            "The Master-Slave Dialectic (Hegel)", "Dasein and Authenticity (Heidegger)",
            "The Simulacra (Baudrillard)", "Panopticism (Foucault)", "The Absurd (Camus)",
            "Amor Fati (Nietzsche)", "Epistemological Anarchism (Feyerabend)",
            "Rhizomatic Structures (Deleuze & Guattari)"
        ],
        "political_theory": [
            "Mimetic Desire (René Girard)", "The Sovereign Individual", 
            "Capitalist Realism (Mark Fisher)", "Accelerationism (e/acc)"
        ]
    }
    field = random.choice(list(library.keys()))
    topic = random.choice(library[field])
    return {"title": topic, "source": "Academic Canon"}, field.upper(), "humanities"

# --- 2. DEPARTMENT OF HARD SCIENCE & MATH ---
def get_science_intel():
    print("📡 CHANNEL: DEEP SCIENCE...")
    domains = {
        "quantum_physics": "cat:quant-ph",  "astrophysics": "cat:astro-ph",
        "condensed_matter": "cat:cond-mat", "game_theory": "cat:cs.GT",
        "complexity": "cat:nlin.AO",        "genetics": "cat:q-bio.GN",
        "neuroscience": "cat:q-bio.NC"
    }
    
    domain_name, query_code = random.choice(list(domains.items()))
    print(f"   -> Field: {domain_name.upper()}")

    try:
        url = f'http://export.arxiv.org/api/query?search_query={query_code}&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending'
        feed = feedparser.parse(url)
        entry = random.choice(feed.entries)
        title = entry.title.replace('\n', ' ')
        return {"title": title, "source": f"ArXiv ({domain_name.upper()})"}, domain_name.upper(), "science"
    except: 
        return get_humanities_intel()

# --- 3. DEPARTMENT OF TECH & POWER ---
def get_tech_intel():
    print("📡 CHANNEL: TECH & POWER...")
    intel = {"title": "The Stagnation of Innovation", "source": "Observation"}
    try:
        top = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:20]
        for id in top:
            s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
            if any(k in s.get('title','').lower() for k in ['ai', 'gpu', 'nvidia', 'crypto', 'agi', 'model', 'robot', 'fusion']):
                intel = {"title": s['title'], "source": "Hacker News"}
                break
    except: pass
    return intel, "MARKET FORCES", "tech"

# --- THE ARTIST ---
def generate_chart(mode, sub_mode):
    print("🎨 ARTIST: Visualizing Concept...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    x = np.linspace(0, 10, 300)
    
    if mode == "humanities":
        y = np.sin(x) * np.cos(x*2.5) * np.exp(0.1*x)
        color, glow = '#BD00FF', '#FF0055' 
        label = "CONCEPT"
    elif mode == "science":
        y = np.sin(x**2) + np.random.normal(0, 0.2, 300)
        color, glow = '#00EAFF', '#FFFFFF' 
        label = "DATA"
    else: 
        y = np.exp(0.25*x) + np.sin(x*5)*0.5
        color, glow = '#00FF41', '#FF9900' 
        label = "SIGNAL"

    ax.fill_between(x, y, -5, color=glow, alpha=0.1)
    ax.plot(x, y, color=color, linewidth=3, alpha=0.9)
    ax.plot(x, y, color='#FFFFFF', linewidth=0.5, alpha=0.6)
    ax.text(5, 0, f"{sub_mode} // {label}", fontsize=20, color='white', ha='center', alpha=0.2, fontname='monospace', weight='bold')
    ax.set_xlim(0, 10)
    ax.axis('off')
    filename = "visual.png"
    plt.savefig(filename, dpi=120, bbox_inches='tight', facecolor='#050505')
    plt.close()
    return filename

# --- THE NARRATOR: THE PROFESSOR ---
def generate_post(intel, sub_mode, mode):
    print("🧠 BRAIN: Synthesizing Manifesto...")
    
    base_instructions = """
    Write a DEEP, ACADEMIC, yet VIRAL LinkedIn essay (1500+ chars).
    Style: High-IQ, Polymathic, Visionary.
    Structure:
    1. THE THESIS (Hook): A sophisticated, contrarian definition.
    2. THE ANTITHESIS (Conflict): Why the mainstream view is shallow.
    3. THE SYNTHESIS (Insight): Apply this to modern tech/life.
    4. THE PRAXIS (Lesson): How to win.
    Format: BOLD headers. Precise terminology.
    """
    
    if mode == "humanities":
        prompt = f"""{base_instructions} Role: Philosopher-King. Topic: "{intel['title']}". Context: {sub_mode}. Explain this concept and apply it to the modern crisis of meaning."""
    elif mode == "science":
        prompt = f"""{base_instructions} Role: Director of Deep Science. Paper: "{intel['title']}" ({intel['source']}). Field: {sub_mode}. Explain the breakthrough and its massive implications."""
    else: 
        prompt = f"""{base_instructions} Role: Technocrat VC. News: "{intel['title']}". Context: {sub_mode}. Analyze the second-order effects on power."""

    # USE BARE METAL ENGINE
    return generate_text_bare_metal(prompt)

# --- PUBLISHER ---
def post_to_linkedin(text, image_path):
    if not text: return print("🛑 NO TEXT GENERATED.")
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
    choice = random.choice(["humanities", "science", "tech"])
    if choice == "humanities": intel, sub_mode, mode = get_humanities_intel()
    elif choice == "science": intel, sub_mode, mode = get_science_intel()
    else: intel, sub_mode, mode = get_tech_intel()
    
    chart = generate_chart(mode, sub_mode)
    post = generate_post(intel, sub_mode, mode)
    post_to_linkedin(post, chart)
