import hashlib
import base64
import os
import random
import string

# Хэширование пароля
def hash_password(password: str) -> str:
    iterations = 100000
    salt = os.urandom(16)
    pbkdf2 = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)
    hashed_password = f"{iterations}:{base64.b64encode(salt).decode()}:{base64.b64encode(pbkdf2).decode()}"
    return hashed_password

# Проверка пароля
def verify_password(password: str, stored_hash: str) -> bool:
    iterations, salt_b64, hash_b64 = stored_hash.split(":")
    salt = base64.b64decode(salt_b64)
    original_hash = base64.b64decode(hash_b64)
    iterations = int(iterations)
    pbkdf2 = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)
    return pbkdf2 == original_hash

def generate_activation_key():
    # Доступные символы: латинские буквы верхнего и нижнего регистра
    chars = string.ascii_letters  # 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # Длины сегментов ключа
    segments = [10, 10, 10]
    # Генерация каждого сегмента
    key = '-'.join(
        ''.join(random.choices(chars, k=length)) for length in segments
    )
    return key

def generate_confirmation_code(length=6):
    return ''.join(random.choices('0123456789', k=length))