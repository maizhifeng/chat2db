from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import pandas as pd
import re
import requests
import json

app = Flask(__name__)
CORS(app)
DB_PATH = os.environ.get('CHAT2DB_DB', '/data/chat2db.sqlite')

# very small NL->SQL converter: handles simple "show/count/list" intents for a single table 'employees'
def nl_to_sql(nl_text):
    text = nl_text.strip().lower()
    # count
    if text.startswith('count') or text.startswith('how many'):
        m = re.search(r"(employees|users|rows)", text)
        table = m.group(1) if m else 'employees'
        return f"SELECT COUNT(*) as count FROM {table}" 
    # show/list
    if text.startswith('show') or text.startswith('list') or text.startswith('give me'):
        m = re.search(r"from (\w+)", text)
        table = m.group(1) if m else 'employees'
        # simple select *
        return f"SELECT * FROM {table} LIMIT 100"
    # fallback: try to extract SELECT clause
    if 'select' in text:
        return nl_text
    return "SELECT * FROM employees LIMIT 100"

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'missing query'}), 400
    nl = data['query']
    sql = nl_to_sql(nl)
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        rows = df.to_dict(orient='records')
        return jsonify({'sql': sql, 'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}), 500
    finally:
        try:
            conn.close()
        except:
            pass

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'})


# Simple helper to call local Ollama HTTP API
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama2')

def call_ollama(prompt, model=None, timeout=30):
    model = model or OLLAMA_MODEL
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 512
    }
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {'error': str(e)}


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message')
    history = data.get('history', [])
    if not message:
        return jsonify({'error': 'missing message'}), 400

    # Build a simple prompt with optional history
    prompt_parts = []
    for turn in history:
        # expect turns like {"role":"user"/"assistant","text":"..."}
        role = turn.get('role', 'user')
        text = turn.get('text', '')
        prompt_parts.append(f"{role}: {text}")
    prompt_parts.append(f"user: {message}")
    prompt = "\n".join(prompt_parts) + "\nassistant:"

    resp = call_ollama(prompt)
    # If Ollama returned error, pass back
    if 'error' in resp:
        return jsonify({'error': resp['error']}), 500

    # Ollama's response shape may vary; return raw content when possible
    # Common response may include 'choices' or 'text'
    result_text = None
    if isinstance(resp, dict):
        if 'choices' in resp and isinstance(resp['choices'], list) and len(resp['choices'])>0:
            c = resp['choices'][0]
            result_text = c.get('text') or c.get('content') or json.dumps(c)
        elif 'text' in resp:
            result_text = resp['text']
        elif 'output' in resp:
            result_text = resp['output']
        else:
            result_text = json.dumps(resp)
    else:
        result_text = str(resp)

    return jsonify({'message': result_text, 'raw': resp})

if __name__ == '__main__':
    # bind to 0.0.0.0 so container exposes it
    app.run(debug=True, host='0.0.0.0', port=5001)
