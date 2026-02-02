import os
import random
import requests
import yfinance as yf
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION (Reads from GitHub Secrets) ---
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
LINKEDIN_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
LINKEDIN_ID = os.environ.get("LINKEDIN_USER_ID")

genai.configure(api_key=GEMINI_KEY)

# --- 0. THE REPAIRMAN ---
def get_working_model():
    # Tries to find the best model available
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
    
    # Try Hacker News
    try:
        top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:20]
        for id in top_ids:
            story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json").json()
            title = story.get('title', '')
            if any(k in title.lower() for k in ['ai', 'gpt', 'llm', 'nvidia', 'model', 'deepseek']):
                intel = {"title": title, "source": "Hacker News"}
                break
    except: pass

    # Fallback to simulated logic if scrape fails
    if not intel:
        intel = {"title": "The Silence of Innovation", "source": "Deep Thought"}

    # Market Check
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
    y += np.random.normal(0, 0.1, 100) # Noise

    # Glow effect
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
    - Start with a controversial hook.
    - Connect the news to the market.
    - Tone: Cold, Technical, High-Status.
    """
    return model.generate_content(prompt).text.strip()

# --- 4. THE PUBLISHER ---
def post_to_linkedin(text, image_path):
    print("🚀 PUBLISHER: Uploading...")
    headers = {"Authorization": f"Bearer {LINKEDIN_TOKEN}", "Content-Type": "application/json"}
    
    # Get User ID
    if not LINKEDIN_ID:
        profile = requests.get("https://api.linkedin.com/v2/me", headers=headers).json()
        author_urn = f"urn:li:person:{profile['id']}"
    else:
        author_urn = LINKEDIN_ID

    # Register Image
    reg = requests.post("https://api.linkedin.com/v2/assets?action=registerUpload", headers=headers, json={
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": author_urn,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
        }
    })
    
    if reg.status_code != 200:
        print(f"❌ Upload Error: {reg.text}")
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
    # UNCOMMENT THIS WHEN YOU ADD LINKEDIN KEYS
    # post_to_linkedin(post, chart) 
    print(f"DONE: {post}")
