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
    # Try several candidate generate endpoints and payload shapes
    endpoints = [
        '/api/generate',
        '/api/completions',
        '/v1/generate',
        '/v1/completions',
        '/api/chat',
        '/generate'
    ]

    # candidate payload shapes: messages (role/content), prompt string, input field
    payloads = [
        {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 512},
        {"model": model, "prompt": prompt, "max_tokens": 512},
        {"model": model, "input": prompt, "max_tokens": 512}
    ]

    last_err = None
    headers = {'Content-Type': 'application/json'}
    for ep in endpoints:
        url = f"{OLLAMA_URL}{ep}"
        for payload in payloads:
            try:
                r = requests.post(url, json=payload, timeout=timeout, headers=headers)
                if r.status_code == 404:
                    last_err = f'404 from {url}'
                    break
                # Some endpoints may reject method; treat 405 specially
                if r.status_code == 405:
                    last_err = f'405 from {url}'
                    break
                r.raise_for_status()
                # try to parse common response shapes and extract text
                try:
                    j = r.json()
                except Exception:
                    return {'text': r.text}

                # Common patterns: choices, outputs, text, result, generation
                if isinstance(j, dict):
                    # Ollama newer API may return {'outputs':[{'type':'message','content':[{'type':'output_text','text':'...'}]}]}
                    if 'outputs' in j and isinstance(j['outputs'], list) and len(j['outputs'])>0:
                        out = j['outputs'][0]
                        # try nested content
                        if isinstance(out, dict) and 'content' in out:
                            content = out['content']
                            if isinstance(content, list) and len(content)>0 and isinstance(content[0], dict):
                                # look for 'text' or 'content'
                                for c in content:
                                    if isinstance(c, dict) and ('text' in c or 'content' in c):
                                        return {'text': c.get('text') or c.get('content')}
                            elif isinstance(content, str):
                                return {'text': content}
                    if 'choices' in j and isinstance(j['choices'], list) and len(j['choices'])>0:
                        ch = j['choices'][0]
                        if isinstance(ch, dict) and ('text' in ch or 'message' in ch):
                            return {'text': ch.get('text') or ch.get('message')}
                    if 'text' in j and isinstance(j['text'], str):
                        return {'text': j['text']}
                    if 'result' in j and isinstance(j['result'], str):
                        return {'text': j['result']}
                    # direct generation field
                    if 'generation' in j:
                        gen = j['generation']
                        if isinstance(gen, list) and len(gen)>0 and isinstance(gen[0], dict):
                            if 'text' in gen[0]:
                                return {'text': gen[0]['text']}
                # fallback: stringify
                return {'text': json.dumps(j)}
            except Exception as e:
                last_err = str(e)
                continue
    # If POST attempts failed, try GET fallback (some deployments may accept query params)
    try:
        for ep in endpoints:
            params = {'model': model, 'prompt': prompt}
            url = f"{OLLAMA_URL}{ep}"
            try:
                r = requests.get(url, params=params, timeout=timeout)
                if r.status_code in (404, 405):
                    last_err = f'{r.status_code} from {url}'
                    continue
                r.raise_for_status()
                try:
                    j = r.json()
                    # try to extract text similar to above
                    if isinstance(j, dict) and 'text' in j:
                        return {'text': j['text']}
                    return {'text': json.dumps(j)}
                except Exception:
                    return {'text': r.text}
            except Exception as e:
                last_err = str(e)
                continue
    except Exception:
        pass

    # Prefer the official streaming NDJSON endpoint /api/generate
    gen_url = f"{OLLAMA_URL}/api/generate"
    try:
        # Increase read timeout for large-model generation and allow streaming NDJSON
        headers_stream = {'Accept': 'application/x-ndjson', 'Content-Type': 'application/json'}
        # use a longer read timeout (connect timeout short, read timeout long)
        with requests.post(gen_url, json={"model": model, "prompt": prompt, "options": {"num_predict": 64}}, headers=headers_stream, stream=True, timeout=(5, 300)) as resp:
            if resp.status_code not in (404, 405):
                resp.raise_for_status()
                # read NDJSON lines and parse the first meaningful GenerateResponse
                for raw in resp.iter_lines(decode_unicode=True):
                    if not raw:
                        continue
                    try:
                        j = json.loads(raw)
                    except Exception:
                        # return raw chunk as fallback
                        return {'text': raw}
                    # Ollama GenerateResponse uses field 'response'
                    if isinstance(j, dict):
                        if 'response' in j and isinstance(j['response'], str):
                            return {'text': j['response']}
                        if 'message' in j and isinstance(j['message'], dict):
                            # Chat style response
                            msg = j['message']
                            if isinstance(msg, dict) and 'content' in msg:
                                return {'text': msg.get('content')}
                        # fallback: stringify
                        return {'text': json.dumps(j)}
    except Exception as e:
        last_err = str(e)

    # Fallback: try the chat streaming endpoint (/api/chat) which accepts ChatRequest
    chat_url = f"{OLLAMA_URL}/api/chat"
    try:
        headers_stream = {'Accept': 'application/x-ndjson', 'Content-Type': 'application/json'}
        chat_payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": True}
        with requests.post(chat_url, json=chat_payload, headers=headers_stream, stream=True, timeout=(5,300)) as resp:
            if resp.status_code not in (404, 405):
                resp.raise_for_status()
                for raw in resp.iter_lines(decode_unicode=True):
                    if not raw:
                        continue
                    try:
                        j = json.loads(raw)
                    except Exception:
                        return {'text': raw}
                    if isinstance(j, dict):
                        # ChatResponse has Message with Content
                        if 'message' in j and isinstance(j['message'], dict):
                            msg = j['message']
                            if 'content' in msg:
                                return {'text': msg.get('content')}
                        if 'response' in j:
                            return {'text': j['response']}
                        return {'text': json.dumps(j)}
    except Exception as e:
        last_err = str(e)

    # If streaming /api/generate didn't work, fall back to previous attempts
    return {'error': f'no working Ollama generate endpoint found: {last_err}'}


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message')
    model = data.get('model')
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

    # allow caller to specify model to use
    resp = call_ollama(prompt, model=model)
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


@app.route('/api/models', methods=['GET'])
def models():
    """Proxy the Ollama /api/models endpoint so frontend can list available models.
    Returns JSON list or an error object when Ollama is unreachable.
    """
    # Some Ollama instances expose available models/tags at /api/tags
    candidates = ['/api/tags', '/api/models', '/v1/models']
    last_err = None
    for c in candidates:
        try:
            url = f"{OLLAMA_URL}{c}"
            r = requests.get(url, timeout=10)
            if r.status_code == 404:
                last_err = f'404 from {url}'
                continue
            r.raise_for_status()
            # Normalize model list into simple array of model names for frontend
            try:
                j = r.json()
            except Exception:
                return jsonify({'raw': r.text})

            # Ollama /api/tags often returns {"models": [{"name":..., "model":...}, ...]}
            models_out = []
            if isinstance(j, dict) and 'models' in j and isinstance(j['models'], list):
                for item in j['models']:
                    if isinstance(item, dict):
                        name = item.get('model') or item.get('name')
                        if name:
                            models_out.append(name)
            elif isinstance(j, list):
                # could be list of strings or dicts
                for item in j:
                    if isinstance(item, str):
                        models_out.append(item)
                    elif isinstance(item, dict):
                        name = item.get('model') or item.get('name')
                        if name:
                            models_out.append(name)
            elif isinstance(j, dict):
                # maybe dict keyed by name
                models_out = list(j.keys())

            return jsonify({'models': models_out})
        except Exception as e:
            last_err = str(e)
            continue
    return jsonify({'error': f'no models endpoint found: {last_err}'}), 500

if __name__ == '__main__':
    # bind to 0.0.0.0 so container exposes it
    app.run(debug=True, host='0.0.0.0', port=5001)
