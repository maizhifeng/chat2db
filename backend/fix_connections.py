import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import DatabaseConnection
import secrets

# 数据库路径
DB_PATH = os.environ.get('CHAT2DB_DB', '/data/chat2db.sqlite')

def fix_connections():
    """Fix connections with empty IDs"""
    # 创建数据库引擎
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 查找ID为空的连接
        connections = session.query(DatabaseConnection).filter(DatabaseConnection.id == '').all()
        
        if not connections:
            print("No connections with empty IDs found")
            return
        
        print(f"Found {len(connections)} connections with empty IDs")
        
        # 为每个连接分配新的ID
        for conn in connections:
            conn.id = f"conn-{secrets.token_hex(8)}"
            print(f"Updated connection '{conn.name}' with new ID: {conn.id}")
        
        session.commit()
        print("Connections fixed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error fixing connections: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    fix_connections()