import sqlite3
from config import TRAIN_VIEW_DB_PATH


def test_database_connection():
    try:
        conn = sqlite3.connect(TRAIN_VIEW_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        print("\n✅ Database Connection Successful!")
        print(f"📌 Tables in database: {tables}")

    except Exception as e:
        print(f"\n❌ Database Connection Failed: {e}")


def test_train_view_data():
    """Check if Train View table has data."""
    conn = sqlite3.connect(TRAIN_VIEW_DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM train_view")
        count = cursor.fetchone()[0]
        print(f"✅ Train View table has {count} records.")

        if count > 0:
            cursor.execute("SELECT * FROM train_view ORDER BY timestamp DESC LIMIT 5")
            latest_entries = cursor.fetchall()
            print("\n📌 Latest Train View Entries:")
            for entry in latest_entries:
                print(entry)
        else:
            print("⚠️ No Train View data found. Check if `train_view.py` ran correctly.")

    except Exception as e:
        print(f"❌ Error checking Train View table: {e}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    print("\n🔎 Running Train View Database Tests...\n")
    test_database_connection()
    test_train_view_data()
