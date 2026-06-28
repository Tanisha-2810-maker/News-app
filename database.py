import sqlite3

def create_database():

    conn = sqlite3.connect("news.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        category TEXT,
        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_search(location, category):

    conn = sqlite3.connect("news.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO searches
        (location, category)
        VALUES (?, ?)
        """,
        (location, category)
    )

    conn.commit()
    conn.close()


def get_recent_searches():

    conn = sqlite3.connect("news.db")

    cursor = conn.cursor()

    cursor.execute("""
    SELECT location, category
    FROM searches
    ORDER BY id DESC
    LIMIT 5
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows