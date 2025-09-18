import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量以解决SSL连接问题
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HF_HUB_OFFLINE'] = '1'

# 设置transformers库的离线模式
import transformers
transformers.utils.offline_mode = True

from flask import Flask, request, jsonify, Response
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
import secrets

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
    
    # Check if ID is provided, if not generate one
    if not data.get('id'):
        data['id'] = f"conn-{secrets.token_hex(8)}"
    
    # Validate required fields
    required_fields = ['id', 'name', 'type', 'database']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'missing {field}'}), 400
    
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
    
    # Validate conn_id parameter
    if not conn_id or conn_id.strip() == '':
        return jsonify({'error': 'connection id is required'}), 400
    
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
    # Validate conn_id parameter
    if not conn_id or conn_id.strip() == '':
        return jsonify({'error': 'connection id is required'}), 400
    
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

# Query table data for a specific table
@app.route('/api/connections/<conn_id>/tables/<table_name>/query', methods=['POST'])
@require_auth
def query_table_data(conn_id, table_name):
    try:
        # Get request data
        data = request.get_json() or {}
        
        # Get the database connection
        session = Session()
        connection = session.query(DatabaseConnection).filter_by(id=conn_id).first()
        if not connection:
            return jsonify({'error': 'connection not found'}), 404
        session.close()
        
        # Create engine for the target database
        engine = get_db_engine(connection)
        
        # Build query with optional filters, sorting, and pagination
        query = f"SELECT * FROM {table_name}"
        
        # Add filtering
        filter_column = data.get('filterColumn')
        filter_value = data.get('filterValue')
        if filter_column and filter_value:
            query += f" WHERE {filter_column} LIKE '%{filter_value}%'"
        
        # Add sorting
        sort_by = data.get('sortBy')
        sort_order = data.get('sortOrder', 'asc')
        if sort_by:
            query += f" ORDER BY {sort_by} {sort_order.upper()}"
        
        # Add pagination
        page = data.get('page', 1)
        page_size = data.get('pageSize', 50)
        offset = (page - 1) * page_size
        query += f" LIMIT {page_size} OFFSET {offset}"
        
        # Execute query
        df = pd.read_sql_query(query, engine)
        # Convert int64 to int for JSON serialization
        rows = df.to_dict(orient='records')
        for row in rows:
            for key, value in row.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if pd.isna(value):
                        row[key] = None
                    else:
                        row[key] = int(value) if value == int(value) else float(value)
        
        # Get total count for pagination
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        if filter_column and filter_value:
            count_query += f" WHERE {filter_column} LIKE '%{filter_value}%'"
        
        count_df = pd.read_sql_query(count_query, engine)
        total_count = int(count_df['count'].iloc[0]) if not count_df.empty else 0
        
        return jsonify({
            'data': rows,
            'totalCount': total_count,
            'page': page,
            'pageSize': page_size
        })
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
    print(f"Calling Ollama with prompt: {prompt[:100]}... and model: {model}")  # 添加调试信息
    # Try the official streaming NDJSON endpoint /api/generate
    gen_url = f"{OLLAMA_URL}/api/generate"
    try:
        # Increase read timeout for large-model generation and allow streaming NDJSON
        headers_stream = {'Accept': 'application/x-ndjson', 'Content-Type': 'application/json'}
        # use a longer read timeout (connect timeout short, read timeout long)
        payload = {"model": model, "prompt": prompt, "stream": False}  # 先尝试非流式
        with requests.post(gen_url, json=payload, headers=headers_stream, timeout=(5, 300)) as resp:
            print(f"Non-streaming request to {gen_url}, status: {resp.status_code}")  # 添加调试信息
            if resp.status_code not in (404, 405):
                resp.raise_for_status()
                j = resp.json()
                print(f"Non-streaming response: {j}")  # 添加调试信息
                # Check if this is a "load" response and try streaming if so
                if j.get('done_reason') == 'load':
                    print("Model is loading, trying streaming...")  # 添加调试信息
                    # Try streaming instead
                    return call_ollama_streaming(gen_url, model, prompt, headers_stream, timeout)
                if 'response' in j and isinstance(j['response'], str):
                    return {'text': j['response']}
                # fallback: stringify
                return {'text': json.dumps(j)}
    except Exception as e:
        print(f"Non-streaming exception: {str(e)}")  # 添加调试信息
        # If non-streaming failed, try streaming
        pass

    # Fallback to streaming
    return call_ollama_streaming(gen_url, model, prompt, headers_stream, timeout)

def call_ollama_streaming(gen_url, model, prompt, headers_stream, timeout):
    """Handle streaming responses from Ollama"""
    try:
        with requests.post(gen_url, json={"model": model, "prompt": prompt, "stream": True}, headers=headers_stream, stream=True, timeout=(5,300)) as resp:
            print(f"Streaming request to {gen_url}, status: {resp.status_code}")  # 添加调试信息
            if resp.status_code not in (404, 405):
                resp.raise_for_status()
                full_response = ""
                # read NDJSON lines and parse the first meaningful GenerateResponse
                for raw in resp.iter_lines(decode_unicode=True):
                    if not raw:
                        continue
                    try:
                        j = json.loads(raw)
                        print(f"Streaming response line: {j}")  # 添加调试信息
                    except Exception as e:
                        print(f"JSON parsing error: {str(e)}")  # 添加调试信息
                        # return raw chunk as fallback
                        return {'text': raw}
                    # Ollama GenerateResponse uses field 'response'
                    if isinstance(j, dict):
                        if 'response' in j and isinstance(j['response'], str):
                            full_response += j['response']
                        elif 'message' in j and isinstance(j['message'], dict):
                            # Chat style response
                            msg = j['message']
                            if isinstance(msg, dict) and 'content' in msg:
                                full_response += msg.get('content', '')
                        # If we have a done response with content, return it
                        if j.get('done') and full_response:
                            return {'text': full_response}
                # If we've collected a response, return it
                if full_response:
                    return {'text': full_response}
                # fallback: stringify
                return {'text': 'No response from model'}
    except Exception as e:
        last_err = str(e)
        print(f"Streaming exception: {last_err}")  # 添加调试信息
        return {'error': f'Error in streaming: {last_err}'}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        print(f"Received chat request with data: {data}")  # 添加调试信息
        
        message = data.get('message')
        model = data.get('model')
        history = data.get('history', [])
        stream = data.get('stream', False)  # 添加stream参数
        
        if not message:
            print("Missing message in request")  # 添加调试信息
            return jsonify({'error': 'missing message'}), 400

        # Build a simple prompt with optional history
        prompt_parts = []
        
        # Add system instruction for structured output
        system_instruction = """You are a database assistant. Please structure your responses in the following format:
[THINKING_PROCESS]
First, explain your thought process and reasoning steps clearly.
[/THINKING_PROCESS]

[RESPONSE_CONTENT]
Then, provide your final response to the user's question.
[/RESPONSE_CONTENT]

Example:
[THINKING_PROCESS]
I need to analyze the user's question and consider relevant database information...
[/THINKING_PROCESS]

[RESPONSE_CONTENT]
Based on your question, I recommend...
[/RESPONSE_CONTENT]

Always follow this exact format. Do not skip either section."""
        
        prompt_parts.append(system_instruction)
        
        for turn in history:
            # expect turns like {"role":"user"/"assistant","text":"..."}
            role = turn.get('role', 'user')
            text = turn.get('text', '')
            prompt_parts.append(f"{role}: {text}")
        prompt_parts.append(f"user: {message}")
        prompt = "\n".join(prompt_parts) + "\nassistant:"
        print(f"Generated prompt: {prompt}")  # 添加调试信息

        # If streaming is requested, return a streaming response
        if stream:
            print(f"Streaming chat response for model: {model}")  # 添加调试信息
            return stream_ollama_response(prompt, model=model)
        
        # Otherwise, use the existing logic for non-streaming
        print(f"Calling Ollama with model: {model}")  # 添加调试信息
        resp = call_ollama(prompt, model=model)
        print(f"Ollama response: {resp}")  # 添加调试信息
        
        # If Ollama returned error, pass back
        if resp and 'error' in resp:
            print(f"Ollama returned error: {resp['error']}")  # 添加调试信息
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
        
        print(f"Returning result: {result_text}")  # 添加调试信息
        return jsonify({'message': result_text, 'raw': resp})
    except Exception as e:
        print(f"Exception in chat endpoint: {str(e)}")  # 添加调试信息
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        return jsonify({'error': str(e)}), 500

def stream_ollama_response(prompt, model=None, timeout=30):
    """Stream responses from Ollama"""
    model = model or OLLAMA_MODEL
    gen_url = f"{OLLAMA_URL}/api/generate"
    
    # Define a generator function for streaming
    def generate():
        try:
            headers = {'Accept': 'application/x-ndjson', 'Content-Type': 'application/json'}
            payload = {"model": model, "prompt": prompt, "stream": True}
            
            print(f"Starting streaming request to {gen_url}")  # 添加调试信息
            
            with requests.post(gen_url, json=payload, headers=headers, stream=True, timeout=(5, 300)) as resp:
                print(f"Streaming response status: {resp.status_code}")  # 添加调试信息
                
                if resp.status_code not in (404, 405):
                    resp.raise_for_status()
                    
                    # Send the initial SSE message
                    yield f"data: {json.dumps({'status': 'connected'})}\n\n"
                    
                    # Send thinking status to indicate the model is processing
                    yield f"data: {json.dumps({'status': 'thinking', 'message': 'AI正在思考中...'})}\n\n"
                    
                    full_response = ""
                    response_started = False
                    
                    # Stream the response
                    for raw in resp.iter_lines(decode_unicode=True):
                        if not raw:
                            continue
                        try:
                            j = json.loads(raw)
                            print(f"Streaming response line: {j}")  # 添加调试信息
                            
                            # Handle different types of responses
                            if isinstance(j, dict):
                                # Check if this is a done message
                                if j.get('done', False):
                                    # Send final result
                                    if full_response:
                                        yield f"data: {json.dumps({'status': 'result', 'response': full_response})}\n\n"
                                    yield "data: [DONE]\n\n"
                                    break
                                # Collect response content
                                elif 'response' in j and isinstance(j['response'], str):
                                    # Start collecting actual response
                                    if not response_started:
                                        response_started = True
                                        yield f"data: {json.dumps({'status': 'responding', 'message': 'AI正在回答中...'})}\n\n"
                                    
                                    full_response += j['response']
                                    # Send incremental response
                                    yield f"data: {json.dumps({'status': 'chunk', 'response': j['response']})}\n\n"
                                elif 'message' in j and isinstance(j['message'], dict):
                                    # Chat style response
                                    msg = j['message']
                                    if isinstance(msg, dict) and 'content' in msg:
                                        content = msg.get('content', '')
                                        if content:
                                            # Start collecting actual response
                                            if not response_started:
                                                response_started = True
                                                yield f"data: {json.dumps({'status': 'responding', 'message': 'AI正在回答中...'})}\n\n"
                                            
                                            full_response += content
                                            # Send incremental response
                                            yield f"data: {json.dumps({'status': 'chunk', 'response': content})}\n\n"
                                else:
                                    # Send other status messages as-is
                                    yield f"data: {json.dumps(j)}\n\n"
                            else:
                                # Send non-dict responses as-is
                                yield f"data: {json.dumps({'raw': str(j)})}\n\n"
                                
                        except Exception as e:
                            print(f"Error processing streaming response: {str(e)}")  # 添加调试信息
                            yield f"data: {json.dumps({'error': f'Error processing response: {str(e)}'})}\n\n"
                            break
                else:
                    error_msg = f"Error connecting to Ollama: {resp.status_code}"
                    print(error_msg)  # 添加调试信息
                    yield f"data: {json.dumps({'error': error_msg})}\n\n"
        except Exception as e:
            error_msg = f"Error in streaming: {str(e)}"
            print(error_msg)  # 添加调试信息
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    # Return a Response object with the generator, setting the proper content type for SSE
    return Response(generate(), mimetype='text/event-stream')

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
        # 确保返回的是列表而不是numpy数组
        if hasattr(embedding, 'tolist'):
            embedding = embedding.tolist()
        return jsonify({'embedding': embedding})
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