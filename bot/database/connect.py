import psycopg2
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def get_db_connection():
    try:
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            print(f"Используем DATABASE_URL: {database_url}")
            conn = psycopg2.connect(database_url)
        else:
            print("Создаем подключение к базе данных вручную")
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "db"),
                database=os.getenv("DB_NAME", "diplomdb"),
                user=os.getenv("DB_USER", "postgres"),
                password=str(os.getenv("DB_PASSWORD", "postgres")),
                port=os.getenv("DB_PORT", "5432"),
                client_encoding='utf8'
            )
        
        print("Успешное подключение к базе данных!")
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к PostgreSQL: {e}", file=sys.stderr)
        print(f"Connection details:", file=sys.stderr)
        print(f"Host: {os.getenv('DB_HOST', 'db')}", file=sys.stderr)
        print(f"Database: {os.getenv('DB_NAME', 'diplomdb')}", file=sys.stderr)
        print(f"User: {os.getenv('DB_USER', 'postgres')}", file=sys.stderr)
        print(f"Port: {os.getenv('DB_PORT', '5432')}", file=sys.stderr)
        print(f"Full environment: {dict(os.environ)}", file=sys.stderr)
        return None
