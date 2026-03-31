from flask import Flask, request, jsonify, render_template_string
import pickle
import re

app = Flask(__name__)

with open('model3classes.pkl', 'rb') as f:
    pipeline = pickle.load(f)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'http\S+|www\S+', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^a-záčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_sentiment(text):
    cleaned = clean_text(text)
    pred = pipeline.predict([cleaned])[0]
    proba = pipeline.predict_proba([cleaned])[0]
    confidence = float(max(proba))

    if pred == 'positive':
        stars = round(3 + (confidence - 0.33) * 3)
    elif pred == 'negative':
        stars = round(3 - (confidence - 0.33) * 3)
    else:
        stars = 3

    stars = max(1, min(5, stars))
    return pred.upper(), confidence, stars

HTML = """
<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sentiment Analyzátor</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0d0d0d;
    --surface: #141414;
    --border: #2a2a2a;
    --text: #f0ede8;
    --muted: #666;
    --pos: #4ade80;
    --neg: #f87171;
    --neu: #fbbf24;
    --pos-dim: rgba(74,222,128,0.08);
    --neg-dim: rgba(248,113,113,0.08);
    --neu-dim: rgba(251,191,36,0.08);
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Mono', monospace;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 60px 20px;
  }

  .noise {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    opacity: 0.4;
  }

  .container {
    position: relative; z-index: 1;
    width: 100%; max-width: 680px;
  }

  header {
    margin-bottom: 52px;
    border-left: 3px solid var(--text);
    padding-left: 20px;
  }

  header h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.2rem, 6vw, 3.4rem);
    font-weight: 900;
    line-height: 1.05;
    letter-spacing: -0.02em;
  }

  header p {
    margin-top: 10px;
    color: var(--muted);
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 32px;
    margin-bottom: 24px;
  }

  label {
    display: block;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 12px;
  }

  textarea {
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: 'DM Mono', monospace;
    font-size: 0.9rem;
    padding: 16px;
    resize: vertical;
    min-height: 140px;
    outline: none;
    transition: border-color 0.2s;
    line-height: 1.6;
  }

  textarea:focus { border-color: #555; }
  textarea::placeholder { color: #333; }

  button {
    margin-top: 16px;
    width: 100%;
    padding: 14px;
    background: var(--text);
    color: var(--bg);
    border: none;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
    transition: opacity 0.2s, transform 0.1s;
  }

  button:hover { opacity: 0.88; }
  button:active { transform: scale(0.99); }
  button:disabled { opacity: 0.3; cursor: not-allowed; }

  .result {
    display: none;
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 32px;
    animation: slideIn 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .result.visible { display: block; }

  .result-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 28px;
  }

  .label-badge {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 900;
    letter-spacing: -0.02em;
    line-height: 1;
  }

  .label-badge.positive { color: var(--pos); }
  .label-badge.negative { color: var(--neg); }
  .label-badge.neutral  { color: var(--neu); }

  .label-sub {
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 6px;
  }

  .stars {
    font-size: 1.8rem;
    letter-spacing: 4px;
  }

  .star-full  { color: #fbbf24; }
  .star-empty { color: #2a2a2a; }

  .divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 20px 0;
  }

  .confidence-row {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .conf-label {
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    white-space: nowrap;
  }

  .conf-bar-wrap {
    flex: 1;
    height: 4px;
    background: var(--border);
  }

  .conf-bar {
    height: 100%;
    transition: width 0.6s ease;
  }

  .conf-bar.positive { background: var(--pos); }
  .conf-bar.negative { background: var(--neg); }
  .conf-bar.neutral  { background: var(--neu); }

  .conf-pct {
    font-size: 0.78rem;
    color: var(--muted);
    white-space: nowrap;
    min-width: 38px;
    text-align: right;
  }

  .sentiment-bg {
    position: absolute;
    inset: 0;
    opacity: 0;
    transition: opacity 0.4s;
    pointer-events: none;
  }

  .result.positive .sentiment-bg { background: var(--pos-dim); opacity: 1; }
  .result.negative .sentiment-bg { background: var(--neg-dim); opacity: 1; }
  .result.neutral  .sentiment-bg { background: var(--neu-dim); opacity: 1; }

  .loading {
    text-align: center;
    padding: 24px;
    color: var(--muted);
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    display: none;
  }

  .loading.visible { display: block; }

  .dot-anim::after {
    content: '';
    animation: dots 1.2s steps(4, end) infinite;
  }

  @keyframes dots {
    0%   { content: ''; }
    25%  { content: '.'; }
    50%  { content: '..'; }
    75%  { content: '...'; }
  }

  footer {
    margin-top: 48px;
    color: var(--muted);
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-align: center;
    text-transform: uppercase;
  }
</style>
</head>
<body>
<div class="noise"></div>
<div class="container">
  <header>
    <h1>Sentiment<br>Analyzátor</h1>
    <p>ČSFD recenze · TF-IDF + SVM · 3 třídy</p>
  </header>

  <div class="card">
    <label>Zadej text recenze</label>
    <textarea id="input" placeholder="Krásný příběh, dojemný a velmi dobře zahraný..."></textarea>
    <button id="btn" onclick="analyze()">Analyzovat →</button>
  </div>

  <div class="loading" id="loading">
    <span class="dot-anim">Analyzuji</span>
  </div>

  <div class="result" id="result">
    <div class="sentiment-bg"></div>
    <div class="result-top">
      <div>
        <div class="label-badge" id="label-text">—</div>
        <div class="label-sub" id="label-sub">sentiment</div>
      </div>
      <div class="stars" id="stars"></div>
    </div>
    <hr class="divider">
    <div class="confidence-row">
      <span class="conf-label">Jistota</span>
      <div class="conf-bar-wrap">
        <div class="conf-bar" id="conf-bar" style="width:0%"></div>
      </div>
      <span class="conf-pct" id="conf-pct">0%</span>
    </div>
  </div>

  <footer>model trénovaný na recenzích z csfd.cz</footer>
</div>

<script>
const LABELS = {
  POSITIVE: { cs: 'Pozitivní', emoji: '😊' },
  NEGATIVE: { cs: 'Negativní', emoji: '😞' },
  NEUTRAL:  { cs: 'Neutrální', emoji: '😐' },
};

async function analyze() {
  const text = document.getElementById('input').value.trim();
  if (!text) return;

  const btn = document.getElementById('btn');
  const loading = document.getElementById('loading');
  const result = document.getElementById('result');

  btn.disabled = true;
  result.classList.remove('visible', 'positive', 'negative', 'neutral');
  loading.classList.add('visible');

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();

    const cls = data.label.toLowerCase();
    const info = LABELS[data.label] || { cs: data.label, emoji: '' };

    document.getElementById('label-text').textContent = info.cs;
    document.getElementById('label-text').className = 'label-badge ' + cls;
    document.getElementById('label-sub').textContent = info.emoji + ' sentiment';

    // Hvězdičky podle sentimentu
    let starsHtml = '';
    for (let i = 1; i <= 5; i++) {
      starsHtml += i <= data.stars
        ? '<span class="star-full">★</span>'
        : '<span class="star-empty">★</span>';
    }
    document.getElementById('stars').innerHTML = starsHtml;

    // Confidence bar
    const pct = Math.round(data.confidence * 100);
    document.getElementById('conf-bar').style.width = pct + '%';
    document.getElementById('conf-bar').className = 'conf-bar ' + cls;
    document.getElementById('conf-pct').textContent = pct + '%';

    result.className = 'result visible ' + cls;

  } catch(e) {
    alert('Chyba při analýze.');
  } finally {
    btn.disabled = false;
    loading.classList.remove('visible');
  }
}

document.getElementById('input').addEventListener('keydown', e => {
  if (e.ctrlKey && e.key === 'Enter') analyze();
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')
    if not text.strip():
        return jsonify({'error': 'Prázdný text'}), 400
    label, confidence, stars = predict_sentiment(text)
    return jsonify({
        'label': label,
        'confidence': confidence,
        'stars': stars,
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080)
