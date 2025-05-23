import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from db import get_connection
import models

async def get_subscription_status(data: models.CheckSubscriptionStatus):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            print("=== get_subscription_status вызвана ===")
            print(f"Входные данные: user_id={data.user_id}, token={data.token}")
            print(f"Conn string: '{conn.dsn}'")
            print("Выполняю SELECT подписки:")

            cursor.execute(
                """
                SELECT s.endDate
                FROM subscriptions s
                JOIN tokens t ON s.userId = t.userid
                WHERE s.userId = %s AND t.token = %s
                """,
                (data.user_id, data.token)
            )

            row = cursor.fetchone()
            print(f"Результат SELECT: {row}")

            if row is None:
                raise HTTPException(status_code=404, detail="Подписка не найдена")

            end_date = row[0]
            print(f"end_date из базы: {end_date}, тип: {type(end_date)}")

            now_msk = datetime.now(timezone.utc)
            today_msk = now_msk.date()

            print(f"Текущее МСК время: {now_msk} (тип: {type(now_msk)})")
            print(f"Текущая МСК дата: {today_msk} (тип: {type(today_msk)})")
            print(f"Сравнение end_date >= today_msk: {end_date >= today_msk}")

            if end_date >= today_msk:
                print("Подписка активна — создаю launch_token")
                launch_token = str(uuid.uuid4())
                issued_at = now_msk
                expires_at = issued_at + timedelta(hours=1)

                print(f"launch_token: {launch_token}")
                print(f"issued_at (MSK): {issued_at}")
                print(f"expires_at (MSK): {expires_at}")

                cursor.execute(
                    """
                    INSERT INTO launch_tokens (userId, token, issuedAt, expiresAt)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (userId) DO UPDATE
                    SET token = EXCLUDED.token, issuedAt = EXCLUDED.issuedAt, expiresAt = EXCLUDED.expiresAt
                    """,
                    (data.user_id, launch_token, issued_at, expires_at)
                )
                conn.commit()

                print("Данные успешно записаны в launch_tokens")
                return {"launch_token": launch_token}
            else:
                print("Подписка неактивна")
                raise HTTPException(status_code=403, detail="Подписка неактивна")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


async def check_valid_launch_token(data: models.CheckValidLaunchToken):
    with get_connection() as conn:
        cursor = conn.cursor()
        print(f"check try")
        try:
            cursor.execute(
                """
                select lt.expiresAt
                from launch_tokens lt
                join tokens t on lt.userId = t.userId
                where t.userId = %s and t.token = %s and lt.token = %s
                """,
                (data.user_id, data.sub_token, data.launch_token)
            )
            print(f"query")
            row = cursor.fetchone()

            if row is None:
                raise HTTPException(status_code=404, detail="Пользователь с таким токеном не найден")
            print(f"row not none")
            expires_at = row

            if datetime.now(timezone.utc) < expires_at:
                print(f"Токен рабочий: {expires_at}")
                return;
            else:  print(f"Токен нерабочий: {expires_at}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")