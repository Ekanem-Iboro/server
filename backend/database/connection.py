import time
import psycopg2
import psycopg2.extras
from ..config import DB_CONFIG

# def get_connection():
#     """
#     Create and return a connection to the PostgreSQL database.
#     """
#     try:
#         conn = psycopg2.connect(
#             user=DB_CONFIG['user'],
#             password=DB_CONFIG['password'],
#             host=DB_CONFIG['host'],
#             port=DB_CONFIG['port'],
#             database=DB_CONFIG['database']
#         )
#         return conn
#     except Exception as e:
#         print(f"Error connecting to PostgreSQL database: {e}")
#         raise
def get_connection():
    """
    Create and return a connection to the PostgreSQL database with retry logic.
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                database=DB_CONFIG['database']
            )
            return conn
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Error connecting to PostgreSQL database after {max_retries} attempts: {e}")
                raise
            time.sleep(1)  # Wait before retrying
def create_tables():
    """
    Create the necessary tables in the database if they don't exist.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create devices table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            device_name VARCHAR(100) NOT NULL,
            device_id VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create locations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accuracy DOUBLE PRECISION,
            speed DOUBLE PRECISION,
            heading DOUBLE PRECISION,
            altitude DOUBLE PRECISION
        );
        """)

        # Create sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            notes TEXT
        );
        """)

        conn.commit()
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


