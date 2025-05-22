import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from db import get_connection
import models
import traceback

async def get_subscription_status(data: models.CheckSubscriptionStatus):
    print("=== get_subscription_status вызвана ===")
    print(f"Входные данные: user_id={data.user_id}, token={data.token}")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

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
                print("Подписка не найдена по user_id и token")
                raise HTTPException(status_code=404, detail="Подписка не найдена")

            end_date = row[0]
            print(f"end_date из базы: {end_date}, тип: {type(end_date)}")

            now_utc = datetime.now(timezone.utc)
            today_utc = now_utc.date()
            print(f"Текущее UTC время: {now_utc} (тип: {type(now_utc)})")
            print(f"Текущая UTC дата: {today_utc} (тип: {type(today_utc)})")

            comparison = (end_date >= today_utc)
            print(f"Сравнение end_date >= today_utc: {comparison}")

            if comparison:
                print("Подписка активна — создаю launch_token")

                launch_token = str(uuid.uuid4())
                issued_at = now_utc
                expires_at = issued_at + timedelta(hours=1)

                print(f"launch_token: {launch_token}")
                print(f"issued_at (UTC): {issued_at}")
                print(f"expires_at (UTC): {expires_at}")

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
                print("Подписка неактивна (end_date < today_utc)")
                raise HTTPException(status_code=403, detail="Подписка неактивна")

    except HTTPException as he:
        print(f"HTTPException: {he.detail}")
        raise he
    except Exception as e:
        print("Произошла ошибка:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")