from cryptography.fernet import Fernet
from app.core.config import settings

# In a real app, use a persistent key from environment
# For now, we'll use a fixed key if available or generate one (which will break between restarts)
ENCRYPTION_KEY = settings.SECRET_KEY[:32].encode().ljust(32, b'a')
import base64
FERNET_KEY = base64.urlsafe_b64encode(ENCRYPTION_KEY)
fernet = Fernet(FERNET_KEY)

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(token: str) -> str:
    try:
        return fernet.decrypt(token.encode()).decode()
    except Exception:
        # Fallback if it's already plain text (for existing data)
        return token
