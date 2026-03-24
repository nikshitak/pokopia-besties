import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

# Debug logging
print(f"DB_HOST: {DB_CONFIG['host']}")
print(f"DB_USER: {DB_CONFIG['user']}")
print(f"DB_NAME: {DB_CONFIG['database']}")
print(f"DB_PORT: {DB_CONFIG['port']}")

def get_connection():
    '''
    Creates connection to mysql database
    '''
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        print(f"DB Config: host={DB_CONFIG['host']}, user={DB_CONFIG['user']}, database={DB_CONFIG['database']}, port={DB_CONFIG['port']}")
        return None

def setup_database():
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()

    # Main pokemon table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pokemon (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            ideal_habitat VARCHAR(100)
        )
    """)

    # Specialties table (up to 2 per pokemon)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS specialties (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pokemon_id INT NOT NULL,
            specialty VARCHAR(100) NOT NULL,
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE
        )
    """)

    # Favorites table (up to 6 per pokemon)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pokemon_id INT NOT NULL,
            favorite VARCHAR(100) NOT NULL,
            FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables created successfully!")

if __name__ == "__main__":
    setup_database()