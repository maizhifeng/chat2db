import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import secrets
import hashlib
from models import User, UserRole

# 数据库路径
DB_PATH = os.environ.get('CHAT2DB_DB', '/data/chat2db.sqlite')

def hash_password(password: str) -> str:
    """Hash a password with a salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${pwd_hash.hex()}"

def create_default_user():
    """Create a default admin user if not exists"""
    # 创建数据库引擎
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 检查是否已存在admin用户
        existing_user = session.query(User).filter(User.username == 'admin').first()
        if existing_user:
            print("Admin user already exists")
            return
        
        # 创建默认admin用户
        user_id = secrets.token_hex(16)
        password_hash = hash_password('admin123')
        
        user = User(
            id=user_id,
            username='admin',
            email='admin@chat2db.com',
            password_hash=password_hash
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # 分配管理员角色
        user_role = UserRole(
            id=secrets.token_hex(16),
            user_id=user.id,
            role_id='admin'
        )
        
        session.add(user_role)
        session.commit()
        
        print("Default admin user created successfully")
        print("Username: admin")
        print("Password: admin123")
        
    except Exception as e:
        session.rollback()
        print(f"Error creating default user: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    create_default_user()