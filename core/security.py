import hashlib
from .config import settings

def check_authcode(auth_text:str):
    salt=settings.SALT_KEY
    auth_text=salt+auth_text
    
    result = hashlib.sha1(auth_text.encode())
    return result.hexdigest()