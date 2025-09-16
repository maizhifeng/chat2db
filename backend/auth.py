import hashlib
import secrets
import jwt
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from models import User, Role, UserRole

# JWT配置
JWT_SECRET = os.environ.get('JWT_SECRET', 'chat2db_secret_key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(hours=24)

class AuthService:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
        
        # 检查数据库连接和表是否存在
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Database tables: {tables}")
            
            # 检查必要的表是否存在
            required_tables = ['users', 'roles', 'user_roles']
            missing_tables = [table for table in required_tables if table not in tables]
            if missing_tables:
                print(f"Warning: Missing tables: {missing_tables}")
        except Exception as e:
            print(f"Warning: Could not inspect database: {e}")
        
        print("AuthService.__init__ completed successfully")
    
    def hash_password(self, password: str) -> str:
        """Hash a password with a salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        salt, pwd_hash = hashed.split('$')
        pwd_hash_bytes = bytes.fromhex(pwd_hash)
        verify_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return pwd_hash_bytes == verify_hash
    
    def create_user(self, username: str, email: str, password: str) -> dict:
        """Create a new user"""
        session = self.Session()
        try:
            # Check if user already exists
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                raise ValueError("User with this username or email already exists")
            
            # Create new user
            user_id = secrets.token_hex(16)
            password_hash = self.hash_password(password)
            
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash
            )
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            # Assign default user role
            user_role = UserRole(
                id=secrets.token_hex(16),
                user_id=user.id,
                role_id='user'  # 默认角色
            )
            
            session.add(user_role)
            session.commit()
            
            return user.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate a user and return a JWT token"""
        session = self.Session()
        try:
            # Find user by username or email
            user = session.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                raise ValueError("User not found")
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                raise ValueError("Invalid password")
            
            # Generate JWT token
            payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA
            }
            
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            return {
                'user': user.to_dict(),
                'token': token
            }
        finally:
            session.close()
    
    def get_user_by_token(self, token: str) -> dict:
        """Get user information from JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload['user_id']
            
            session = self.Session()
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    return user.to_dict()
                return None
            finally:
                session.close()
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def get_user_roles(self, user_id: str) -> list:
        """Get all roles for a user"""
        session = self.Session()
        try:
            user_roles = session.query(UserRole).filter(UserRole.user_id == user_id).all()
            role_ids = [ur.role_id for ur in user_roles]
            
            if not role_ids:
                return []
            
            roles = session.query(Role).filter(Role.id.in_(role_ids)).all()
            return [role.to_dict() for role in roles]
        finally:
            session.close()
    
    def check_permission(self, user_id: str, required_role: str) -> bool:
        """Check if user has a specific role"""
        roles = self.get_user_roles(user_id)
        role_names = [role['name'] for role in roles]
        return required_role in role_names

# Create global auth service instance
auth_service = None

def init_auth_service(engine):
    global auth_service
    try:
        print("Initializing AuthService...")
        auth_service = AuthService(engine)
        print("AuthService initialized successfully")
        print(f"auth_service after initialization: {auth_service}")
        return auth_service
    except Exception as e:
        print(f"Failed to initialize AuthService: {e}")
        import traceback
        traceback.print_exc()
        auth_service = None
        raise
