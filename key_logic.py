import models
import other_functions
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from db import get_connection

MSK = timezone(timedelta(hours=3))

async def create_license_key(data: models.KeyCreateRequest):
    duration = data.key_duration
    if duration not in [1, 7, 30, 180]:
        raise HTTPException(status_code=400, detail="Invalid key type")

    key_string = other_functions.generate_activation_key()
    created_at = datetime.now(MSK)

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO LicenseKeys (KeyValue, DurationDays, IsUsed, CreatedAt)
                VALUES (%s, %s, false, %s)
                RETURNING KeyID
            """, (key_string, duration, created_at))
            key_id = cursor.fetchone()[0]
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

    return {
        "key": key_string,
        "duration_days": duration,
        "key_id": key_id
    }

async def activate_license_key(data: models.KeyActivateRequest):
    with get_connection() as conn:
        cursor = conn.cursor()

    keyid, duration_days = get_key_info(cursor, data.key_value)
    now = datetime.now(MSK)
    subscription = get_subscription(cursor, data.user_id)

    if subscription:
        subscriptionid, startdate, enddate = subscription
        now = datetime.now(MSK).date()
        if enddate and enddate > now:
            # Продлить с текущей даты окончания
            new_startdate = startdate  # можно оставить старую дату начала
            new_enddate = enddate + timedelta(days=duration_days)
        else:
            # Новая подписка с текущей даты
            new_startdate = now
            new_enddate = now + timedelta(days=duration_days)

        update_subscription(cursor, subscriptionid, keyid, new_startdate, new_enddate, now)
    else:
        new_startdate = now
        new_enddate = now + timedelta(days=duration_days)
        create_subscription(cursor, data.user_id, keyid, new_startdate, new_enddate, now)
    deactivate_key(cursor, keyid)
    conn.commit()

    return {
        "message": "Subscription activated/updated successfully",
        "startdate": new_startdate.isoformat(),
        "enddate": new_enddate.isoformat()
    }

def get_key_info(cursor, key: str):
    cursor.execute("SELECT keyId, durationDays, isUsed FROM LicenseKeys WHERE keyValue = %s", (key,))
    key_row = cursor.fetchone()
    if not key_row:
        raise HTTPException(status_code=404, detail="Key not found")
    keyid, duration_days, is_active = key_row
    if is_active:
        raise HTTPException(status_code=400, detail="Key is already used")
    return keyid, duration_days

def get_subscription(cursor, user_id: int):
    cursor.execute("SELECT subscriptionId, startDate, endDate FROM subscriptions WHERE userId = %s", (user_id,))
    return cursor.fetchone()

def update_subscription(cursor, subscriptionid: int, keyid: int, startdate: datetime, enddate: datetime, createdat: datetime):
    cursor.execute(
        """
        UPDATE subscriptions
        SET keyId = %s, startDate = %s, endDate = %s, createdAt = %s
        WHERE subscriptionId = %s
        """,
        (keyid, startdate, enddate, createdat, subscriptionid)
    )

def create_subscription(cursor, user_id: int, keyid: int, startdate: datetime, enddate: datetime, createdat: datetime):
    cursor.execute(
        """
        INSERT INTO subscriptions (userId, keyId, startDate, endDate, createdAt)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, keyid, startdate, enddate, createdat)
    )

def deactivate_key(cursor, key_id):
    cursor.execute(
        """
    UPDATE LicenseKeys
    SET isUsed = %s
    WHERE keyId = %s
        """,
        (True, key_id)
    )