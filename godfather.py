import os
import random
import requests
import yfinance as yf
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION ---
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
LINKEDIN_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_ID = os.environ.get("LINKEDIN_USER_ID")

genai.configure(api_key=GEMINI_KEY)

# --- 0. THE REPAIRMAN ---
def get_working_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    return genai.GenerativeModel(m.name)
    except: pass
    return genai.GenerativeModel('gemini-1.5-flash')

# --- 1. THE SCOUT ---
def get_intel():
    print("📡 SCOUT: Scanning...")
    intel = None
    try:
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:20]
        for id in top_ids:
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
            title = story.get('title', '')
            if any(k in title.lower() for k in ['ai', 'gpt', 'llm', 'nvidia', 'model', 'deepseek']):
                intel = {"title": title, "source": "Hacker News"}
                break
    except: pass

    if not intel:
        intel = {"title": "The Silence of Innovation", "source": "Deep Thought"}

    market = "Market Offline"
    try:
        nvda = yf.Ticker("NVDA")
        hist = nvda.history(period="1d")
        if not hist.empty:
            change = ((hist['Close'].iloc[0] - hist['Open'].iloc[0]) / hist['Open'].iloc[0]) * 100
            market = f"NVDA {'UP' if change > 0 else 'DOWN'} {abs(change):.2f}%"
    except: pass
        
    return intel, market

# --- 2. THE ARTIST ---
def generate_chart(topic, market):
    print("🎨 ARTIST: Generating chart...")
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.linspace(0, 10, 100)
    color = '#00ff41' if "UP" in market else '#ff0055'
    y = np.sin(x) * np.exp(0.1 * x)
    if "UP" in market: y += x * 0.1
    y += np.random.normal(0, 0.1, 100)

    ax.plot(x, y, color=color, linewidth=10, alpha=0.3)
    ax.plot(x, y, color=color, linewidth=2.5)
    ax.set_title(f"ANALYSIS: {topic[:30]}... // {market}", color='white')
    ax.axis('off')
    
    filename = "chart.png"
    plt.savefig(filename, dpi=100, bbox_inches='tight', facecolor='#050505')
    plt.close()
    return filename

# --- 3. THE GODFATHER ---
def generate_post(intel, market):
    print("🧠 BRAIN: Writing...")
    model = get_working_model()
    prompt = f"""
    You are a Cynical Deep Tech CTO.
    NEWS: "{intel['title']}" ({intel['source']})
    MARKET: {market}
    Task: Write a LinkedIn post (max 500 chars).
    - Controversial hook.
    - Connect news to market.
    - Tone: Cold, High-Status.
    """
    return model.generate_content(prompt).text.strip()

# --- 4. THE PUBLISHER (FIXED FOR OPENID) ---
def post_to_linkedin(text, image_path):
    print("🚀 PUBLISHER: Authenticating...")
    headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}", "Content-Type": "application/json"}
    
    # --- ID FETCH FIX ---
    if not LINKEDIN_ID:
        # Try Method 1: OpenID (New Standard)
        try:
            resp = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)
            if resp.status_code == 200:
                profile = resp.json()
                author_urn = f"urn:li:person:{profile['sub']}"
            else:
                # Try Method 2: Classic (Legacy)
                resp = requests.get("https://api.linkedin.com/v2/me", headers=headers)
                if resp.status_code == 200:
                    profile = resp.json()
                    author_urn = f"urn:li:person:{profile['id']}"
                else:
                    print(f"❌ CRITICAL ERROR: Could not fetch User ID. Response: {resp.text}")
                    return
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")
            return
    else:
        author_urn = LINKEDIN_ID
        
    print(f"✅ Authenticated as: {author_urn}")

    # Register Image
    reg = requests.post("https://api.linkedin.com/v2/assets?action=registerUpload", headers=headers, json={
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author_urn,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
        }
    })
    
    if reg.status_code != 200:
        print(f"❌ Image Register Error: {reg.text}")
        return

    upload_url = reg.json()['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset_urn = reg.json()['value']['asset']

    # Upload Binary
    with open(image_path, 'rb') as f:
        requests.put(upload_url, headers={"Authorization": f"Bearer {LINKEDIN_TOKEN}"}, data=f)

    # Publish
    post_body = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "IMAGE",
                "media": [{"status": "READY", "media": asset_urn, "title": {"text": "Analysis"}}]
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    final = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=post_body)
    if final.status_code == 201:
        print("✅ GODFATHER HAS SPOKEN.")
    else:
        print(f"❌ Post Failed: {final.text}")

# --- RUN ---
if __name__ == "__main__":
    intel, market = get_intel()
    chart = generate_chart(intel['title'], market)
    post = generate_post(intel, market)
    post_to_linkedin(post, chart)
