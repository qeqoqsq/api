import models
from db import get_connection
import other_functions
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import uuid
from models import TokenCheckRequest


async def register_user(data: models.RegisterData):
    # Подключаемся к БД
    with get_connection() as conn:
        cursor = conn.cursor()
        hashed_password = other_functions.hash_password(data.password)
        # Сохраняем нового пользователя в базе данных
        cursor.execute("INSERT INTO Users (UserLogin, UserPassword, UserIpAddress, UserEmail) VALUES (%s, %s, %s, %s)",
                       (data.login, hashed_password, data.ip_address, data.email))
        conn.commit()

    print(f"Пользователь: login - {data.login}, password - {hashed_password}, ip_address - {data.ip_address}, email - {data.email} был зарегистрирован")
    # ключ при регистрации
    # data = models.KeyCreateRequest(key_duration=7)
    # result = await key_logic.create_license_key(data)
    # key_string = result["key"]
    # data = models.KeyActivateRequest(key_value=key_string, user_id=row[0])
    # await key_logic.activate_license_key(data)
    return {"Регистрация прошла успешно"}

async def check_unique_login(data: models.CheckUniqueLogin):
    # Подключаемся к БД
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM Users WHERE UserLogin = %s", (data.login,))
        if cursor.fetchone() is not None:
            raise HTTPException(status_code=409, detail="Пользователь с таким логином уже существует")
        return

async def login_user(data: models.LoginData):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT UserId, UserPassword FROM Users WHERE UserLogin = %s", (data.login,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        user_id, stored_hash = row

        if not other_functions.verify_password(data.password, stored_hash):
            raise HTTPException(status_code=401, detail="Invalid password")

        created_at = datetime.now(timezone.utc)
        expires_at = created_at + timedelta(days=7)

        # Генерируем уникальный токен
        while True:
            token = str(uuid.uuid4())
            print(f"сгенерированный token: {token}")
            cursor.execute("SELECT 1 FROM tokens WHERE token = %s", (token,))
            if not cursor.fetchone():
                break  # Токен уникален, выходим из цикла

        # Проверяем, есть ли уже токен для пользователя
        cursor.execute("SELECT token FROM tokens WHERE userId = %s", (user_id,))
        existing_token = cursor.fetchone()

        if existing_token:
            cursor.execute("""
                UPDATE tokens
                SET token = %s, createdAt = %s, expiresAt = %s
                WHERE userId = %s
            """, (token, created_at, expires_at, user_id))
        else:
            cursor.execute("""
                INSERT INTO tokens (userId, token, createdAt, expiresAt)
                VALUES (%s, %s, %s, %s)
            """, (user_id, token, created_at, expires_at))

        conn.commit()
        print(f"token: {token}, user_id: {user_id}")
        return {"token": token, "user_id": user_id}



async def validate_token(data: TokenCheckRequest):
    with get_connection() as conn:
        cursor = conn.cursor()
    cursor.execute("""
            SELECT users.* FROM tokens
            JOIN users ON users.userid = tokens.userId
            WHERE tokens.token = %s AND tokens.expiresAt > NOW()
            """, (data.token,))

    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    print(f"userid: {user[0]}, userLogin: {user[1]}, userPass: {user[2]}, userIpAddress: {user[3]}, userEmail: {user[4]}")
    return {"user_id": user[0]}