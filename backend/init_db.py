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

INSERT INTO employees (name, department, salary) VALUES
('Alice','Engineering',120000),
('Bob','Sales',80000),
('Carol','Engineering',115000),
('Dave','HR',70000);
'''

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(schema)
    conn.commit()
    conn.close()
    print('Initialized', DB_PATH)
