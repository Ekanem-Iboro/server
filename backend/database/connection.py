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
    last_error = None

    # Log connection attempt with configuration (hide password)
    db_config_safe = DB_CONFIG.copy()
    db_config_safe['password'] = '********'  # Hide password in logs
    print(f"Attempting database connection with config: {db_config_safe}")

    while retry_count < max_retries:
        try:
            # Add sslmode=require for secure connections to hosted databases
            conn = psycopg2.connect(
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                database=DB_CONFIG['database'],
                sslmode='require'
            )
            print(f"Database connection successful to {DB_CONFIG['host']}")
            return conn
        except Exception as e:
            last_error = e
            retry_count += 1
            print(f"Database connection attempt {retry_count} failed: {str(e)}")
            if retry_count >= max_retries:
                error_msg = f"Error connecting to PostgreSQL database after {max_retries} attempts: {str(e)}"
                print(error_msg)
                # Include more detailed error information
                import traceback
                print(traceback.format_exc())
                raise Exception(f"Database connection failed: {str(e)}")
            time.sleep(1)  # Wait before retrying
def create_tables():
    """
    Create the necessary tables in the database if they don't exist.
    """
    conn = None
    try:
        print("Attempting to create database tables...")
        conn = get_connection()
        cursor = conn.cursor()

        # Create users table
        print("Creating users table...")
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
        print("Creating devices table...")
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
        print("Creating locations table...")
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
        print("Creating sessions table...")
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
        print("All tables created successfully")
        return True
    except Exception as e:
        error_msg = f"Error creating tables: {str(e)}"
        print(error_msg)
        # Include more detailed error information
        import traceback
        print(traceback.format_exc())
        if conn:
            conn.rollback()
        # Don't raise the exception, just return False to indicate failure
        # This allows the application to continue even if table creation fails
        return False
    finally:
        if conn:
            conn.close()


