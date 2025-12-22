from utils.db import db
from main import app
from sqlalchemy import text

with app.app_context():
    try:
        # Check if column exists
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(achievements)")).fetchall()
            columns = [row[1] for row in result]
            if 'is_deleted' not in columns:
                print("Adding is_deleted column...")
                conn.execute(text("ALTER TABLE achievements ADD COLUMN is_deleted BOOLEAN DEFAULT 0"))
                conn.commit()
                print("Column added.")
            else:
                print("Column already exists.")
    except Exception as e:
        print(f"Error: {e}")
