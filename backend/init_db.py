import os
import sqlite3

# write DB into the mounted data directory inside the container
DATA_DIR = os.environ.get('CHAT2DB_DATA', '/data')
DB_PATH = os.path.join(DATA_DIR, 'chat2db.sqlite')

schema = '''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    salary INTEGER
);

CREATE TABLE IF NOT EXISTS connections (
    id TEXT PRIMARY KEY,
    name TEXT,
    type TEXT,
    host TEXT,
    port INTEGER,
    username TEXT,
    password TEXT,
    database TEXT,
    environment TEXT,
    file_path TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS user_roles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    role_id TEXT NOT NULL
);

INSERT INTO employees (name, department, salary) VALUES
('Alice','Engineering',120000),
('Bob','Sales',80000),
('Carol','Engineering',115000),
('Dave','HR',70000);

INSERT INTO roles (id, name, description) VALUES
('admin', 'Administrator', 'Full access to all features'),
('user', 'User', 'Standard user access');
'''

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(schema)
    conn.commit()
    conn.close()
    print('Initialized', DB_PATH)