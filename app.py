from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
from collections import Counter
import os

app = Flask(__name__)
CORS(app)   # Ye line bahut important hai frontend ke liye

# ==================== Load Both Files ====================
def load_all_articles():
    all_articles = []

    # 1. Load JSON file
    if os.path.exists('articles.json'):
        try:
            with open('articles.json', 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            for item in json_data:
                content = item.get('content') or item.get('markdown') or ""
                all_articles.append({
                    "title": item.get('title', 'Untitled'),
                    "url": item.get('url', ''),
                    "content": str(content)
                })
            print(f"✅ Loaded {len(json_data)} articles from articles.json")
        except Exception as e:
            print("❌ Error loading articles.json:", e)

    # 2. Load TXT file
    if os.path.exists('articles.txt'):
        try:
            with open('articles.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            
            raw_articles = content.split('===ARTICLE_START===')
            
            for raw in raw_articles:
                if '===ARTICLE_END===' not in raw:
                    continue
                article_text = raw.split('===ARTICLE_END===')[0].strip()
                
                title_match = re.search(r'TITLE:\s*(.+)', article_text)
                url_match = re.search(r'URL:\s*(.+)', article_text)
                content_match = re.search(r'CONTENT:\s*(.+)', article_text, re.DOTALL)
                
                if title_match and content_match:
                    all_articles.append({
                        "title": title_match.group(1).strip(),
                        "url": url_match.group(1).strip() if url_match else "",
                        "content": content_match.group(1).strip()
                    })
            print(f"✅ Loaded articles from articles.txt")
        except Exception as e:
            print("❌ Error loading articles.txt:", e)

    print(f"Total {len(all_articles)} articles loaded in memory.")
    return all_articles


articles = load_all_articles()

# ==================== Short Summarizer (same rakho) ====================
def create_short_reply(text, max_words=80):
    if not text or len(text) < 20:
        return "Information nahi mili is topic par."
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
    
    if len(sentences) <= 3:
        return " ".join(sentences[:3])
    
    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)
    
    scored = []
    for sent in sentences:
        score = sum(word_freq.get(w, 0) for w in re.findall(r'\w+', sent.lower()))
        scored.append((score, sent))
    
    scored.sort(reverse=True)
    summary = ". ".join([sent for _, sent in scored[:5]]) + "."
    
    word_list = summary.split()
    if len(word_list) > max_words:
        summary = " ".join(word_list[:max_words]) + "..."
    
    return summary

# ==================== Chat Endpoint ====================
@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip().lower()
    
    if not user_msg or len(user_msg) < 3:
        return jsonify({"reply": "Kuch travel related sawaal poochho ✈️"})

    best_score = 0
    best_title = ""
    best_url = ""
    best_summary = ""

    for art in articles:
        title_lower = art["title"].lower()
        content_lower = art["content"].lower()
        
        title_score = sum(1 for word in user_msg.split() if len(word) > 2 and word in title_lower)
        content_score = sum(1 for word in user_msg.split() if len(word) > 2 and word in content_lower)
        
        total_score = (title_score * 5) + content_score
        
        if total_score > best_score:
            best_score = total_score
            best_title = art["title"]
            best_url = art["url"]
            best_summary = create_short_reply(art["content"], max_words=85)

    if best_score < 2:
        return jsonify({"reply": "Sorry, is topic par abhi clear information nahi mili. Thoda aur specific poochho!"})

    reply = f"**{best_title}**\n\n{best_summary}\n\n🔗 {best_url}"

    return jsonify({"reply": reply})


# ==================== IMPORTANT: Render ke liye yeh part badal do ====================
if __name__ == '__main__':
    print("🚀 TraveChat Backend Started - Both JSON & TXT supported!")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)   # debug=False rakho
