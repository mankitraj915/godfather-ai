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

# --- HARDCODED DEBUG KEY (DELETE AFTER TESTING) ---
# Paste your fresh key inside the quotes below
DEBUG_KEY = "AIzaSyC89CW13gL537Us5iytNaFhbc8C7cafnMg" 

LINKEDIN_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_ID = os.environ.get("LINKEDIN_USER_ID")

# --- THE UNIVERSAL ENGINE ---
def generate_text_debug(prompt):
    print("🔧 DIAGNOSTIC: Starting Engine...")
    
    # 1. Define the models to test (Mix of old and new)
    models = [
        "gemini-1.5-flash",
        "gemini-pro",
        "gemini-1.0-pro-latest"
    ]
    
    for model in models:
        # Try v1beta first
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={DEBUG_KEY}"
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
            print(f"   ... Testing Model: {model} ...")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS on {model}!")
                try:
                    return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                except:
                    print("   ⚠️ 200 OK but JSON parse failed.")
                    continue
            else:
                print(f"   ❌ Failed {model}: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ⚠️ Network Error: {e}")
            continue

    return None

# --- INTELLIGENCE ---
def get_intel():
    print("📡 FETCHING INTELLIGENCE...")
    return {"title": "The Stagnation of Tech", "source": "Debug Mode"}, "SYSTEMS", "tech"

# --- ARTIST ---
def generate_chart(mode, sub_mode, text_content):
    print("🎨 RENDERING CHART...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#050505')
    ax.set_facecolor('#050505')

    t = np.linspace(0, 10, 50000)
    x = np.sin(t*-1.4) * np.cos(t*1.6) * t
    y = np.sin(t*1.0) * np.sin(t*0.7) * t
    
    ax.plot(x, y, ',', color='#00FF41', alpha=0.3) 
    
    if text_content:
        post_hash = hashlib.sha256(text_content.encode()).hexdigest()[:16]
    else:
        post_hash = "DEBUG_MODE"

    font = {'fontname': 'monospace', 'weight': 'bold'}
    ax.text(0.5, 0.95, f"// SYSTEM: {sub_mode} //", transform=ax.transAxes, fontsize=20, color='white', ha='center', alpha=0.8, **font)
    ax.text(0.5, 0.02, f"BLOCK_ID: 0x{post_hash}", transform=ax.transAxes, fontsize=10, color='gray', ha='center', alpha=0.6, **font)
    
    ax.axis('off')
    filename = "visual.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='#050505')
    plt.close()
    return filename

# --- PUBLISHER ---
def post_to_linkedin(text, image_path):
    if not text: return print("🛑 NO TEXT GENERATED.")
    
    print("🚀 POSTING TO LINKEDIN...")
    if not LINKEDIN_TOKEN:
        print("❌ Error: LINKEDIN_ACCESS_TOKEN not found in environment.")
        return

    headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}", "Content-Type": "application/json"}
    
    try:
        if not LINKEDIN_ID:
            r = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
            if r.status_code == 200: urn = f"urn:li:person:{r.json()['sub']}"
            else: urn = f"urn:li:person:{requests.get('https://api.linkedin.com/v2/me', headers=headers).json()['id']}"
        else:
            urn = LINKEDIN_ID
    except:
        print("❌ LinkedIn Auth Failed")
        return

    reg = requests.post("https://api.linkedin.com/v2/assets?action=registerUpload", headers=headers, json={
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": urn,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
        }
    })
    
    if reg.status_code != 200: return print(f"❌ Image Upload Init Error: {reg.text}")
    
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
    
    if res.status_code == 201: print("✅ GODFATHER HAS SPOKEN (DEBUG SUCCESS).")
    else: print(f"❌ Post Error: {res.text}")

if __name__ == "__main__":
    if DEBUG_KEY == "PASTE_YOUR_KEY_HERE":
        print("❌ STOP: You forgot to paste your API Key in the code!")
    else:
        intel, sub_mode, mode = get_intel()
        post = generate_text_debug("Write a short test post for LinkedIn about AI.")
        
        if post:
            chart = generate_chart(mode, sub_mode, post)
            post_to_linkedin(post, chart)
        else:
            print("❌ System Failure: All models failed.")
