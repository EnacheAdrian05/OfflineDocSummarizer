import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlite3 import connect
from hashlib import sha256
from app_func.gen_summary import read_file


def create_connection():
    basedir = os.path.abspath(os.path.dirname(__file__))
    file = os.path.join(basedir, "documents.db")
    conn = connect(file)
    
    return conn


def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            hash TEXT PRIMARY KEY,
            abspath TEXT UNIQUE,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    

def find_by_hash(hash_val: str):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM documents WHERE hash = ?', (hash_val,))
    result = cursor.fetchone()
    
    conn.close()
    return result


def get_all_documents():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM documents')
    results = cursor.fetchall()
    
    conn.close()
    
    return results
    
    
def insert_document(abspath: str) -> bool:
    abspath = os.path.abspath(abspath)
    text = read_file(abspath)
    if not text:
        return False

    conn = create_connection()
    cursor = conn.cursor()

    hash_val = file_hash(abspath)
    if not hash_val:
        conn.close()
        return False

    cursor.execute('SELECT abspath FROM documents WHERE hash = ?', (hash_val,))
    row = cursor.fetchone()

    if row:
        if row[0] != abspath:
            cursor.execute('UPDATE documents SET abspath = ? WHERE hash = ?', (abspath, hash_val))
            conn.commit()
        conn.close()
        return False

    cursor.execute('''
        INSERT INTO documents (hash, abspath)
        VALUES (?, ?)
    ''', (hash_val, abspath))

    conn.commit()
    conn.close()
    return True


def file_hash(abspath: str) -> str | None:
    content = read_file(abspath)

    if content is None:
        return None

    content = content.lower()
    content = content.split()
    content = ' '.join(content)
    
    return sha256(content.encode('utf-8')).hexdigest()


def update_summary(hash_val: str, summary: str):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT summary FROM documents WHERE hash = ?', (hash_val,))
    current_summary = cursor.fetchone()
    
    if not current_summary:
        conn.close()
        return None

    if current_summary[0] is not None:
        conn.close()
        return None

    cursor.execute('''
        UPDATE documents
        SET summary = ?
        WHERE hash = ?
    ''', (summary, hash_val))

    conn.commit()
    conn.close()
    return True

    

if __name__ == "__main__":
    create_table()