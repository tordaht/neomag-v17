from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

# --- Ayarlar ---
SECRET_KEY = "a_very_secret_key_that_should_be_in_env_variables"  # Gerçek uygulamada .env dosyasından okunmalı
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Parola İşlemleri ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Sahte Kullanıcı Veritabanı ---
# Gerçek uygulamada bu bir veritabanı olmalı
FAKE_USERS_DB = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("testpassword"),
        "disabled": False,
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Girilen şifre ile hash'lenmiş şifreyi doğrular."""
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> Optional[dict]:
    """Kullanıcıyı veritabanından alır."""
    if username in FAKE_USERS_DB:
        return FAKE_USERS_DB[username]
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Erişim token'ı oluşturur."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verilen token'ı doğrular ve kullanıcı adını (sub) döner."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None 