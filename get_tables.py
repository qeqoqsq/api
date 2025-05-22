from fastapi import HTTPException
from db import get_connection

async def get_users():
    try:
        print("Проверка users")
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT UserID, UserLogin, UserPassword, UserEmail FROM Users")
            rows = cursor.fetchall()
            users = [{"id": row[0], "login": row[1], "password":row[2], "email": row[3]} for row in rows]
            return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_subscriptions():
    try:
        print("Проверка subscriptions")
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SubscriptionID, UserID, StartDate, EndDate, CreatedAt FROM Subscriptions")
            rows = cursor.fetchall()
            subscriptions = [
                {
                    "id": row[0],
                    "user_id": row[1],
                    "start_date": row[2],
                    "end_date": row[3],
                    "CreatedAt": row[4]
                }
                for row in rows
            ]
            return {"subscriptions": subscriptions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# async def get_license_keys():
#     try:
#         print("Проверка LicenseKeys")
#         with get_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute("SELECT KeyId, KeyValue, DurationDays, IsUsed, CreatedAt FROM LicenseKeys")
#             rows = cursor.fetchall()
#             licenseKeys = [
#                 {
#                     "KeyId": row[0],
#                     "KeyValue": row[1],
#                     "DurationDays": row[2],
#                     "IsUsed": row[3],
#                     "CreatedAt": row[4]
#                 }
#                 for row in rows
#             ]
#             return {"LicenseKeys": licenseKeys}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))