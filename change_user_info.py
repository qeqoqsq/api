import models
import key_logic
from db import get_connection
import other_functions
from fastapi import HTTPException, status


async def change_user_password(data: models.ChangePassword):
    # Подключаемся к БД
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT UserId, UserPassword FROM Users WHERE UserLogin = %s", (data.login,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        user_id, stored_hash = row
        print(f"Пользователь: user_id - {user_id}, user_password - {stored_hash} - был найден")
        if not other_functions.verify_password(data.current_password, stored_hash):
            raise HTTPException(status_code=401, detail="Неверный пароль")
        print(f"Пользователь: user_id - {user_id}, user_password - {stored_hash} - пароль правильный")

        hashed_password = other_functions.hash_password(data.new_password)
        cursor.execute("""UPDATE Users
                       SET UserPassword = %s
                       WHERE userLogin = %s""", (hashed_password, data.login,))
        conn.commit()
        return {"Пароль успешно обновлён"}