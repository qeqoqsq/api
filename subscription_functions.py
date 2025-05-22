import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from db import get_connection
import models

async def get_subscription_status(data: models.CheckSubscriptionStatus):
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
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

            if row is None:
                raise HTTPException(status_code=404, detail="Подписка не найдена")

            end_date = row[0]
            print(f"end_date из базы: {end_date}, тип: {type(end_date)}")
            print(f"сравниваем с: {datetime.now(timezone.utc).date()}, тип: {type(datetime.now(timezone.utc).date())}")

            if end_date > datetime.now(timezone.utc).date():
                # Создание launch_token
                launch_token = str(uuid.uuid4())
                expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

                # Вставляем или обновляем
                cursor.execute(
                    """
                    INSERT INTO launch_tokens (userId, token, issuedAt, expiresAt)
                    VALUES (%s, %s, now(), %s)
                    ON CONFLICT (userId) DO UPDATE
                    SET token = EXCLUDED.token, issuedAt = now(), expiresAt = EXCLUDED.expiresAt
                    """,
                    (data.user_id, launch_token, expires_at)
                )
                conn.commit()

                return {"launch_token": launch_token}
            else:
                raise HTTPException(status_code=403, detail="Подписка неактивна")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")
