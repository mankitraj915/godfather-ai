import os
import time
import random
import requests
import feedparser
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import hashlib
import json

# --- CONFIGURATION: THE DECA-HYDRA (MULTI-KEY SYSTEM) ---
KEYS = []
if os.environ.get("GEMINI_API_KEY"): KEYS.append(os.environ.get("GEMINI_API_KEY"))
for i in range(2, 11):
    k = os.environ.get(f"GEMINI_API_KEY_{i}")
    if k: KEYS.append(k)

VALID_KEYS = KEYS
CURRENT_KEY_INDEX = 0

LINKEDIN_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_ID = os.environ.get("LINKEDIN_USER_ID")

# --- 0. THE BARE METAL ENGINE (Dual-Version) ---
def generate_text_bare_metal(prompt):
    global CURRENT_KEY_INDEX
    if not VALID_KEYS: 
        print("❌ Error: No API Keys found.")
        return None

    # STRATEGY: Try strict versions first, then aliases.
    # We also toggle between 'v1beta' and 'v1' endpoints.
    models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "gemini-pro",
        "gemini-1.0-pro"
    ]
    
    versions = ["v1beta", "v1"]

    # Try up to 30 times (Keys * Versions * Models)
    for attempt in range(30):
        key = VALID_KEYS[CURRENT_KEY_INDEX]
        
        for version in versions:
            for model in models:
                # Construct URL dynamically based on version
                url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={key}"
                headers = {'Content-Type': 'application/json'}
                
                # Safety Settings set to BLOCK_NONE to avoid 400/403 on intellectual topics
                data = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                }
                
                try:
                    # print(f"   ... Trying {version}/{model} on Key #{CURRENT_KEY_INDEX+1}...")
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                    
                    if response.status_code == 200:
                        try:
                            return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                        except:
                            # If 200 OK but parse fails, likely a safety filter triggered silently
                            continue 
                    elif response.status_code == 429:
                        print(f"⚠️ Key #{CURRENT_KEY_INDEX+1} Quota Exceeded.")
                        break # Break model loop to rotate key
                    elif response.status_code == 404:
                        continue # Model not found in this version, try next
                    else:
                        continue # Other error, try next
                        
                except Exception as e:
                    continue

        # Rotate Key if we exhausted models/versions for the current key
        if len(VALID_KEYS) > 1:
            CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(VALID_KEYS)
            print(f"🔄 Switching to API Key #{CURRENT_KEY_INDEX + 1}...")
            time.sleep(1)
            
    return None

# --- 1. INTELLIGENCE ---
def get_intel():
    choice = random.choice(["humanities", "science", "tech"])
    
    if choice == "humanities":
        print("📡 CHANNEL: HIGH PHILOSOPHY...")
        topics = ["The Shadow (Jung)", "Simulacra (Baudrillard)", "Panopticon (Foucault)", "Mimetic Desire (Girard)", "Amor Fati (Nietzsche)", "The Rhizome (Deleuze)"]
        return {"title": random.choice(topics), "source": "Academic Canon"}, "CONCEPT", "humanities"
        
    elif choice == "science":
        print("📡 CHANNEL: HARD SCIENCE...")
        domains = {"quantum": "cat:quant-ph", "neuro": "cat:q-bio.NC", "complexity": "cat:nlin.AO", "ai": "cat:cs.AI"}
        domain_name, query_code = random.choice(list(domains.items()))
        try:
            url = f'http://export.arxiv.org/api/query?search_query={query_code}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending'
            feed = feedparser.parse(url)
            entry = random.choice(feed.entries)
            return {"title": entry.title.replace('\n', ' '), "source": f"ArXiv ({domain_name.upper()})"}, domain_name.upper(), "science"
        except: 
            return {"title": "Entropy & Chaos Systems", "source": "Physics"}, "ENTROPY", "science"

    else:
        print("📡 CHANNEL: TECH POWER...")
        return {"title": "The Stagnation of Software Innovation", "source": "Market Observation"}, "SYSTEMS", "tech"

# --- THE ARTIST: CHAOS THEORY ---
def generate_chart(mode, sub_mode, text_content):
    print("🎨 ARTIST: Rendering Chaos...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#050505')
    ax.set_facecolor('#050505')

    n_points = 50000
    
    if mode == "humanities":
        a, b, c, d = -1.4, 1.6, 1.0, 0.7 
        color_map = 'magma' 
    elif mode == "science":
        a, b, c, d = 1.7, 1.7, 0.6, 1.2
        color_map = 'cyan'
    else: 
        a, b, c, d = -1.8, -2.0, -0.5, -0.9
        color_map = 'spring'

    t = np.linspace(0, 10, n_points)
    x = np.sin(t*a) * np.cos(t*b) * t
    y = np.sin(t*c) * np.sin(t*d) * t
    
    if color_map == 'cyan': color = '#00EAFF'
    elif color_map == 'magma': color = '#FF0055'
    else: color = '#00FF41'
    
    ax.plot(x, y, ',', color=color, alpha=0.3) 
    ax.plot(x[:200], y[:200], '-', color='white', linewidth=0.5, alpha=0.5) 
    
    if text_content:
        post_hash = hashlib.sha256(text_content.encode()).hexdigest()[:16]
    else:
        post_hash = "GEN_ERR"

    font = {'fontname': 'monospace', 'weight': 'bold'}
    ax.text(0.5, 0.95, f"// SYSTEM: {sub_mode} //", transform=ax.transAxes, fontsize=20, color='white', ha='center', alpha=0.8, **font)
    ax.text(0.5, 0.02, f"BLOCK_ID: 0x{post_hash}", transform=ax.transAxes, fontsize=10, color='gray', ha='center', alpha=0.6, **font)
    
    ax.axis('off')
    filename = "visual.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#050505')
    plt.close()
    return filename

# --- THE NARRATOR ---
def generate_post(intel, sub_mode, mode):
    print("🧠 BRAIN: Calculating...")
    
    base_instructions = """
    Write a DEEP, ACADEMIC, yet VIRAL LinkedIn essay (1500+ chars).
    Style: High-IQ, Polymathic, Visionary.
    Structure:
    1. THE THESIS (Hook): A sophisticated, contrarian definition.
    2. THE ANTITHESIS (Conflict): Why the mainstream view is shallow.
    3. THE SYNTHESIS (Insight): Apply this to modern tech/life.
    4. THE PRAXIS (Lesson): How to win.
    Format: BOLD headers. No emojis. Pure signal.
    """
    
    prompt = f"""{base_instructions} Role: Intellectual Titan. Topic: "{intel['title']}". Context: {sub_mode}. Explain this deep concept and apply it to the modern world."""
    
    return generate_text_bare_metal(prompt)

# --- PUBLISHER ---
def post_to_linkedin(text, image_path):
    if not text: return print("🛑 NO TEXT GENERATED.")
    print("🚀 PUBLISHER: Broadcasting...")
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

if __name__ == "__main__":
    intel, sub_mode, mode = get_intel()
    post = generate_post(intel, sub_mode, mode)
    
    if post:
        chart = generate_chart(mode, sub_mode, post)
        post_to_linkedin(post, chart)
    else:
        print("❌ System Failure: All models exhausted.")
