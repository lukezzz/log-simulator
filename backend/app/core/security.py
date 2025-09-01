
import bcrypt
import uuid
from cryptography.fernet import Fernet
from .settings import cfg

# Generate or validate Fernet key
def get_or_generate_fernet_key():
    """
    Get the Fernet key from config, or generate a new one if empty/invalid.
    In dev environment, this helps when FERNET_KEY is not properly set.
    """
    fernet_key = cfg.FERNET_KEY
    
    # Check if key is empty or None
    if not fernet_key or fernet_key.strip() == "":
        print("Warning: FERNET_KEY is empty, generating a new one for development...")
        new_key = Fernet.generate_key()
        # In dev environment, you might want to save this key somewhere
        # For now, we'll just use it for this session
        return new_key
    
    # Validate the existing key by trying to create a Fernet instance
    try:
        # Try to create Fernet instance to validate the key
        test_cipher = Fernet(fernet_key.encode() if isinstance(fernet_key, str) else fernet_key)
        return fernet_key.encode() if isinstance(fernet_key, str) else fernet_key
    except Exception as e:
        print(f"Warning: Invalid FERNET_KEY ({e}), generating a new one for development...")
        new_key = Fernet.generate_key()
        return new_key

fernet_key = get_or_generate_fernet_key()
cipher = Fernet(fernet_key)


def encrypt(data: str):
    # 加密
    encrypted_data = cipher.encrypt(data.encode())

    encrypted_str = encrypted_data.decode()
    return encrypted_str


def decrypt(encrypted_str):
    # 解密
    try:
        decrypted_data = cipher.decrypt(encrypted_str)
    except Exception as e:
        raise ValueError("Invalid data")

    decrypted = decrypted_data.decode()
    return decrypted


# hash password
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")


# verify password
def verify_password(plain_password: str, hashed_password: str):
    password_byte_enc = plain_password.encode("utf-8")
    return bcrypt.checkpw(
        password=password_byte_enc, hashed_password=hashed_password.encode("utf-8")
    )


# generate uuid
def gen_uuid() -> str:
    return str(uuid.uuid4())

