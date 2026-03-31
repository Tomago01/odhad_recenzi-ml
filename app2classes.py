from flask import Flask, request, jsonify, render_template_string
import pickle
import re

app = Flask(__name__)

# Nacteni modelu
with open("model2classes.pkl", "rb") as f:
    model = pickle.load(f)

HTML = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sentiment Analyzer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Segoe UI', sans-serif;
            background: #0f0f1a;
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 640px;
        }

        h1 {
            font-size: 1.6rem;
            margin-bottom: 6px;
            color: #fff;
        }

        .subtitle {
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 28px;
        }

        textarea {
            width: 100%;
            height: 140px;
            background: #1a1a2e;
            border: 1px solid #333;
            border-radius: 10px;
            color: #e0e0e0;
            font-size: 1rem;
            padding: 14px;
            resize: vertical;
            outline: none;
            transition: border 0.2s;
        }

        textarea:focus { border-color: #7c5cbf; }

        button {
            margin-top: 12px;
            width: 100%;
            padding: 13px;
            background: #7c5cbf;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover { background: #9370db; }

        .result {
            margin-top: 24px;
            background: #1a1a2e;
            border-radius: 10px;
            padding: 20px;
            display: none;
        }

        .label {
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 12px;
        }

        .label.positive { color: #4caf87; }
        .label.negative { color: #e05c6e; }

        .score-bar {
            background: #0f0f1a;
            border-radius: 20px;
            height: 10px;
            overflow: hidden;
            margin-bottom: 8px;
        }

        .score-fill {
            height: 100%;
            border-radius: 20px;
            transition: width 0.5s ease;
        }

        .score-fill.positive { background: #4caf87; }
        .score-fill.negative { background: #e05c6e; }

        .score-text { font-size: 0.85rem; color: #888; }

        .examples { margin-top: 28px; font-size: 0.85rem; color: #666; }

        .examples span {
            display: inline-block;
            margin: 4px 4px 0 0;
            padding: 5px 10px;
            background: #1a1a2e;
            border-radius: 20px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .examples span:hover { background: #252540; color: #ccc; }
    </style>
</head>
<body>
<div class="container">
    <h1>Sentiment Analyzer</h1>
    <p class="subtitle">Analyza ceskeho textu - pozitivni nebo negativni?</p>

    <textarea id="text" placeholder="Napis recenzi nebo libovolny cesky text..."></textarea>
    <button onclick="analyze()">Analyzovat</button>

    <div class="result" id="result">
        <div class="label" id="label"></div>
        <div class="score-bar">
            <div class="score-fill" id="scoreFill"></div>
        </div>
        <div class="score-text" id="scoreText"></div>
    </div>

    <div class="examples">
        <div style="margin-bottom:6px; color:#555;">Priklady:</div>
        <span onclick="setExample('Naprost&#253; uzasny film, nejlepsi co jsem videl!')">Skvely film</span>
        <span onclick="setExample('Strasna nuda, totalni ztrata casu.')">Spatny film</span>
        <span onclick="setExample('Krasny pribeh, dojemny a dobre zahran.')">Dojemny</span>
        <span onclick="setExample('Hercineumeji hrat, scenar je katastrofa.')">Katastrofa</span>
    </div>
</div>

<script>
function setExample(text) {
    document.getElementById('text').value = text;
    analyze();
}

async function analyze() {
    const text = document.getElementById('text').value.trim();
    if (!text) return;

    const res = await fetch('/predict', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({text})
    });

    const data = await res.json();

    const resultDiv = document.getElementById('result');
    const label = document.getElementById('label');
    const scoreFill = document.getElementById('scoreFill');
    const scoreText = document.getElementById('scoreText');

    resultDiv.style.display = 'block';

    const isPos = data.sentiment === 'positive';
    label.textContent = isPos ? 'POZITIVNI' : 'NEGATIVNI';
    label.className = 'label ' + data.sentiment;

    const pct = data.score * 10;
    scoreFill.style.width = pct + '%';
    scoreFill.className = 'score-fill ' + data.sentiment;

    scoreText.textContent = 'Jistota: ' + data.score + '/10 (' + Math.round(data.confidence * 100) + '%)';
}

document.getElementById('text').addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'Enter') analyze();
});
</script>
</body>
</html>
"""


def clean_text(text):
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^a-z\u00e1\u010d\u010f\u00e9\u011b\u00ed\u0148\u00f3\u0159\u0161\u0165\u00fa\u016f\u00fd\u017e\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    cleaned = clean_text(text)
    pred = model.predict([cleaned])[0]
    proba = model.predict_proba([cleaned])[0]

    sentiment = "positive" if pred == 1 else "negative"
    confidence = float(max(proba))
    score = int(1 + (confidence - 0.5) * 18)
    score = max(1, min(10, score))

    return jsonify({
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "score": score,
    })


if __name__ == "__main__":
    app.run(debug=True, port=8080)
