import os
import psycopg2

def get_connection():
    conn_str = os.getenv("DATABASE_URL")
    print(f"Conn string: '{conn_str}'")
    return psycopg2.connect(conn_str)

def create_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    UserID SERIAL PRIMARY KEY,
                    UserLogin VARCHAR(50) NOT NULL,
                    UserPassword VARCHAR(255) NOT NULL,
                    UserEmail VARCHAR(100)
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS Subscriptions (
                    SubscriptionID SERIAL PRIMARY KEY,
                    UserID INTEGER REFERENCES Users(UserID),
                    StartDate DATE,
                    EndDate DATE,
                    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

        conn.commit()
        print("Таблицы успешно созданы.")
