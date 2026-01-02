import os
import sqlite3
from datetime import datetime

DB_NAME = os.getenv("DB_PATH", "/data/kanban.db")



def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # permite acessar colunas por nome
    return conn


def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_task(title, description=None):
    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    cursor.execute("""
        INSERT INTO tasks (title, description, status, created_at)
        VALUES (?, ?, ?, ?)
    """, (title, description, "todo", created_at))

    task_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None


def list_tasks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
    rows = cursor.fetchall()

    conn.close()
    return [dict(row) for row in rows]


def update_task_status(task_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = ?
        WHERE id = ?
    """, (new_status, task_id))

    conn.commit()
    ok = cursor.rowcount == 1
    conn.close()
    return ok


def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()

    ok = cursor.rowcount == 1
    conn.close()
    return ok


if __name__ == "__main__":
    create_database()
