from db import create_tables
from dotenv import load_dotenv
import os

load_dotenv()
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

if __name__ == "__main__":
    create_tables()