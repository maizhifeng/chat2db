from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import pandas as pd
import re

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

if __name__ == '__main__':
    # bind to 0.0.0.0 so container exposes it
    app.run(debug=True, host='0.0.0.0', port=5001)
