import models
from db import get_connection
from datetime import datetime, timezone
from fastapi import HTTPException, status

async def get_user_info(data: models.GetUserInfo):
    # Подключаемся к БД
    with get_connection() as conn:
        cursor = conn.cursor()
        print(data.user_id)
        # Сохраняем нового пользователя в базе данных
        cursor.execute("""
            SELECT
                users.userlogin,
                users.useripaddress,
                users.useremail,
                subscriptions.enddate
            FROM users
            Left JOIN subscriptions ON users.userid = subscriptions.userid
            WHERE users.userid = %s;
        """, (data.user_id,))

    result = cursor.fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_login, user_ipaddress, user_email, end_date= result
    subscribe_status = False
    if end_date is not None:
        subscribe_status = end_date > datetime.now(timezone.utc).date()
    else: end_date = "Подписка не оформлена"
    print("Запрос сделан, переменные получены")
    print(f"Пользователь: login - {user_login}, user_ipaddress - {user_ipaddress}, email - {user_email}, end_date - {end_date}, subscribe_status - {subscribe_status}")

    return models.UserInfo(
        user_login=user_login,
        email=user_email,
        ip_address=user_ipaddress,
        subscribe_status=subscribe_status,
        subscription_end_date=str(end_date)
    )