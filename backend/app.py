import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import re
import requests
import json
from models import DatabaseConnection, create_tables, User, Role, UserRole
from nlp_enhanced import enhanced_nlp
from auth import init_auth_service
import auth
# 导入embeddings模块
from embeddings.model import EmbeddingsModel

app = Flask(__name__)
CORS(app)
DB_PATH = os.environ.get('CHAT2DB_DB', '/data/chat2db.sqlite')

# Initialize the database
def init_db():
    # Use SQLite for the main application database
    engine = create_engine(f'sqlite:///{DB_PATH}')
    create_tables(engine)
    return engine

# Get database engine based on connection type
def get_db_engine(connection):
    try:
        if connection.type == 'sqlite':
            return create_engine(f'sqlite:///{connection.database}')
        elif connection.type == 'mysql':
            return create_engine(f'mysql+pymysql://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database}')
        elif connection.type == 'postgresql':
            return create_engine(f'postgresql://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database}')
        else:
            raise ValueError(f"Unsupported database type: {connection.type}")
    except Exception as e:
        raise ValueError(f"Failed to create engine for {connection.type}: {str(e)}")

# Create a session for the main app database
app_engine = init_db()
Session = sessionmaker(bind=app_engine)

# Initialize auth service
print("Before calling init_auth_service")
init_auth_service(app_engine)
print("After calling init_auth_service")

# Check if auth_service is properly initialized
print("Checking auth_service...")
print(f"auth.auth_service = {auth.auth_service}")
if auth.auth_service is None:
    raise RuntimeError("Failed to initialize auth service")
print("auth_service is properly initialized")

# Authentication decorator
def require_auth(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1]
            user = auth.auth_service.get_user_by_token(token)
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
            # Add user to request context
            request.user = user
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Admin decorator
def require_admin(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1]
            user = auth.auth_service.get_user_by_token(token)
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Check if user has admin role
            if not auth.auth_service.check_permission(user['id'], 'Administrator'):
                return jsonify({'error': 'Insufficient permissions'}), 403
                
            # Add user to request context
            request.user = user
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

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

# User authentication APIs
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'missing data'}), 400
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'missing {field}'}), 400
    
    try:
        user = auth.auth_service.create_user(
            data['username'],
            data['email'],
            data['password']
        )
        return jsonify(user), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'missing data'}), 400
    
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'missing {field}'}), 400
    
    try:
        result = auth.auth_service.authenticate_user(
            data['username'],
            data['password']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 401

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    return jsonify(request.user)

# Database Connection Management APIs
@app.route('/api/connections', methods=['POST'])
@require_auth
def create_connection():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'missing data'}), 400
    
    try:
        session = Session()
        connection = DatabaseConnection.from_dict(data)
        session.add(connection)
        session.commit()
        session.refresh(connection)
        return jsonify(connection.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/connections', methods=['GET'])
@require_auth
def get_connections():
    try:
        session = Session()
        connections = session.query(DatabaseConnection).all()
        return jsonify([conn.to_dict() for conn in connections])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/connections/<conn_id>', methods=['GET'])
@require_auth
def get_connection(conn_id):
    try:
        session = Session()
        connection = session.query(DatabaseConnection).filter_by(id=conn_id).first()
        if not connection:
            return jsonify({'error': 'connection not found'}), 404
        return jsonify(connection.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/connections/<conn_id>', methods=['PUT'])
@require_auth
def update_connection(conn_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'missing data'}), 400
    
    try:
        session = Session()
        connection = session.query(DatabaseConnection).filter_by(id=conn_id).first()
        if not connection:
            return jsonify({'error': 'connection not found'}), 404
            
        # Update fields
        for key, value in data.items():
            if hasattr(connection, key):
                setattr(connection, key, value)
                
        session.commit()
        session.refresh(connection)
        return jsonify(connection.to_dict())
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/connections/<conn_id>', methods=['DELETE'])
@require_auth
def delete_connection(conn_id):
    try:
        session = Session()
        connection = session.query(DatabaseConnection).filter_by(id=conn_id).first()
        if not connection:
            return jsonify({'error': 'connection not found'}), 404
            
        session.delete(connection)
        session.commit()
        return jsonify({'message': 'connection deleted'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/connections/<conn_id>/test', methods=['POST'])
@require_auth
def test_connection(conn_id):
    try:
        session = Session()
        connection = session.query(DatabaseConnection).filter_by(id=conn_id).first()
        if not connection:
            return jsonify({'error': 'connection not found'}), 404
            
        # Create engine and test connection
        engine = get_db_engine(connection)
        # Try to connect
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({'message': 'connection successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Enhanced query endpoint that supports multiple database types
@app.route('/api/query/<conn_id>', methods=['POST'])
@require_auth
def query_with_connection(conn_id):
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'missing query'}), 400
    
    nl = data['query']
    sql = nl_to_sql(nl)
    
    try:
        # Get the database connection
        session = Session()
        connection = session.query(DatabaseConnection).filter_by(id=conn_id).first()
        if not connection:
            return jsonify({'error': 'connection not found'}), 404
        session.close()
        
        # Create engine for the target database
        engine = get_db_engine(connection)
        
        # Execute query
        df = pd.read_sql_query(sql, engine)
        rows = df.to_dict(orient='records')
        return jsonify({'sql': sql, 'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e), 'sql': sql}), 500

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

# Enhanced NL2SQL endpoint
@app.route('/api/nl2sql', methods=['POST'])
def nl2sql():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'missing query'}), 400
    
    nl = data['query']
    table = data.get('table')  # 可选的表名
    
    try:
        # 使用增强的NLP模块
        sql = enhanced_nlp.parse_nl_to_sql(nl, table)
        return jsonify({'sql': sql})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get tables for a specific connection
@app.route('/api/connections/<conn_id>/tables', methods=['GET'])
@require_auth
def get_tables(conn_id):
    try:
        # Get the database connection
        session = Session()
        connection = session.query(DatabaseConnection).filter_by(id=conn_id).first()
        if not connection:
            return jsonify({'error': 'connection not found'}), 404
        session.close()
        
        # Create engine for the target database
        engine = get_db_engine(connection)
        
        # Get table names
        if connection.type == 'sqlite':
            query = "SELECT name FROM sqlite_master WHERE type='table';"
        elif connection.type == 'mysql':
            query = f"SELECT table_name as name FROM information_schema.tables WHERE table_schema = '{connection.database}';"
        elif connection.type == 'postgresql':
            query = f"SELECT tablename as name FROM pg_tables WHERE schemaname = 'public';"
        else:
            return jsonify({'error': f'Unsupported database type: {connection.type}'}), 400
            
        df = pd.read_sql_query(query, engine)
        tables = df['name'].tolist()
        return jsonify(tables)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get table schema for a specific table
@app.route('/api/connections/<conn_id>/tables/<table_name>', methods=['GET'])
@require_auth
def get_table_schema(conn_id, table_name):
    try:
        # Get the database connection
        session = Session()
        connection = session.query(DatabaseConnection).filter_by(id=conn_id).first()
        if not connection:
            return jsonify({'error': 'connection not found'}), 404
        session.close()
        
        # Create engine for the target database
        engine = get_db_engine(connection)
        
        # Get table schema
        if connection.type == 'sqlite':
            query = f"PRAGMA table_info({table_name});"
        elif connection.type == 'mysql':
            query = f"DESCRIBE {table_name};"
        elif connection.type == 'postgresql':
            query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = 'public';"
        else:
            return jsonify({'error': f'Unsupported database type: {connection.type}'}), 400
            
        df = pd.read_sql_query(query, engine)
        schema = df.to_dict(orient='records')
        return jsonify(schema)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# Embeddings相关的API端点
@app.route('/api/embeddings/encode', methods=['POST'])
def encode_text():
    """
    将文本编码为向量
    
    请求体:
    {
        "text": "要编码的文本"
    }
    
    返回:
    {
        "embedding": [0.1, 0.2, ...]  # 文本的向量表示
    }
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'missing text'}), 400
    
    try:
        # 初始化 Embeddings 模型
        embeddings_model = EmbeddingsModel()
        # 编码文本
        embedding = embeddings_model.encode(data['text'])
        return jsonify({'embedding': embedding.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/embeddings/similarity', methods=['POST'])
def calculate_similarity():
    """
    计算两个文本的相似度
    
    请求体:
    {
        "text1": "第一个文本",
        "text2": "第二个文本"
    }
    
    返回:
    {
        "similarity": 0.85  # 两个文本的相似度
    }
    """
    data = request.get_json()
    if not data or 'text1' not in data or 'text2' not in data:
        return jsonify({'error': 'missing text1 or text2'}), 400
    
    try:
        # 初始化 Embeddings 模型
        embeddings_model = EmbeddingsModel()
        # 计算相似度
        similarity = embeddings_model.similarity(data['text1'], data['text2'])
        return jsonify({'similarity': float(similarity)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # bind to 0.0.0.0 so container exposes it
    app.run(debug=True, host='0.0.0.0', port=5001)