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

# --- CONFIGURATION ---
KEYS = []
if os.environ.get("GEMINI_API_KEY"): KEYS.append(os.environ.get("GEMINI_API_KEY"))
for i in range(2, 11):
    k = os.environ.get(f"GEMINI_API_KEY_{i}")
    if k: KEYS.append(k)

if not KEYS:
    print("❌ CRITICAL: No API Keys found.")
    exit()

VALID_KEYS = KEYS
CURRENT_KEY_INDEX = 0

LINKEDIN_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_ID = os.environ.get("LINKEDIN_USER_ID")

# --- 0. THE OMNI-DISCOVERY ENGINE ---
def get_working_model_config(key):
    """
    Scans both v1beta and v1 endpoints to find a working model config.
    Returns a tuple: (version, model_name)
    """
    endpoints = ["v1beta", "v1"]
    
    for version in endpoints:
        url = f"https://generativelanguage.googleapis.com/{version}/models?key={key}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                valid_models = []
                for m in data.get('models', []):
                    if 'generateContent' in m.get('supportedGenerationMethods', []):
                        clean_name = m['name'].replace('models/', '')
                        valid_models.append(clean_name)
                
                if valid_models:
                    print(f"   ✅ Found Models in {version}: {valid_models[:3]}...")
                    # Priority Selection (Newer models first)
                    for m in valid_models: 
                        if '2.5' in m: return version, m # Catch the new Gemini 2.5
                    for m in valid_models: 
                        if 'flash' in m and '1.5' in m: return version, m
                    for m in valid_models: 
                        if 'pro' in m and '1.5' in m: return version, m
                    return version, valid_models[0]
        except:
            continue

    return "v1beta", "gemini-1.5-flash"

def generate_text_bare_metal(prompt):
    global CURRENT_KEY_INDEX
    
    for attempt in range(10):
        key = VALID_KEYS[CURRENT_KEY_INDEX]
        
        # STEP 1: Auto-Discover correct Version AND Model
        print(f"🔧 Diagnosing Key #{CURRENT_KEY_INDEX+1}...")
        version, model_name = get_working_model_config(key)
        print(f"   -> Selected: {version}/{model_name}")

        # STEP 2: Generate
        url = f"https://generativelanguage.googleapis.com/{version}/models/{model_name}:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
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
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                try:
                    raw_text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                    # --- SAFETY RAZOR (TRUNCATION) ---
                    # 1. Remove "Here is a post" filler if present
                    if "Here is" in raw_text[:20]:
                        raw_text = raw_text.split("\n", 1)[-1].strip()
                    
                    # 2. Hard limit to 2800 chars (LinkedIn limit is 3000)
                    if len(raw_text) > 2800:
                        print("   ⚠️ Trimming text to 2800 chars...")
                        raw_text = raw_text[:2800] + "..."
                    
                    return raw_text
                except:
                    print("   ⚠️ 200 OK but JSON malformed.")
                    continue
            elif response.status_code == 429:
                print(f"   ⚠️ Quota Exceeded (429). Rotating Key.")
                if len(VALID_KEYS) > 1:
                    CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(VALID_KEYS)
                else:
                    time.sleep(10)
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
                if len(VALID_KEYS) > 1:
                    CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(VALID_KEYS)

        except Exception as e:
            print(f"   ⚠️ Request Failed: {e}")

    return None

# --- INTELLIGENCE ---
def get_intel():
    print("📡 CHANNEL: TECH POWER...")
    return {"title": "The Stagnation of Software", "source": "Observation"}, "SYSTEMS", "tech"

# --- ARTIST ---
def generate_chart(mode, sub_mode, text_content):
    print("🎨 ARTIST: Rendering Chaos...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#050505')
    ax.set_facecolor('#050505')

    n_points = 50000
    t = np.linspace(0, 10, n_points)
    x = np.sin(t*-1.4) * np.cos(t*1.6) * t
    y = np.sin(t*1.0) * np.sin(t*0.7) * t
    
    ax.plot(x, y, ',', color='#00FF41', alpha=0.3) 
    
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

# --- NARRATOR (STRICT MODE) ---
def generate_post(intel, sub_mode, mode):
    print("🧠 BRAIN: Calculating...")
    
    # STRICT INSTRUCTIONS TO PREVENT "OPTIONS"
    base_instructions = """
    Write EXACTLY ONE LinkedIn essay (max 2000 chars).
    DO NOT provide options (Option 1, Option 2).
    DO NOT write intro text like "Here is a post".
    Start directly with the Hook/Title.
    
    Style: High-IQ, Polymathic, Visionary.
    Structure:
    1. THE THESIS (Hook)
    2. THE ANTITHESIS (Conflict)
    3. THE SYNTHESIS (Insight)
    4. THE PRAXIS (Lesson)
    """
    
    prompt = f"""{base_instructions} Role: Intellectual Titan. Topic: "{intel['title']}". Context: {sub_mode}."""
    
    return generate_text_bare_metal(prompt)

# --- PUBLISHER ---
def post_to_linkedin(text, image_path):
    if not text: return print("🛑 NO TEXT GENERATED.")
    print("🚀 PUBLISHER: Broadcasting...")
    
    if not LINKEDIN_TOKEN: return print("❌ No LinkedIn Token.")

    headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}", "Content-Type": "application/json"}
    
    try:
        if not LINKEDIN_ID:
            r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
            if r.status_code == 200: urn = f"urn:li:person:{r.json()['sub']}"
            else: urn = f"urn:li:person:{requests.get('https://api.linkedin.com/v2/me', headers=headers).json()['id']}"
        else:
            urn = LINKEDIN_ID
    except: return print("❌ Auth Failed")

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
        print("❌ System Failure.")
