import sqlite3
from config import TRIP_UPDATES_DB_PATH


def test_database_connection():
    try:
        conn = sqlite3.connect(TRIP_UPDATES_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        print("\n✅ Database Connection Successful!")
        print(f"📌 Tables in database: {tables}")

    except Exception as e:
        print(f"\n❌ Database Connection Failed: {e}")


def test_trip_updates_data():
    conn = sqlite3.connect(TRIP_UPDATES_DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM trip_updates")
        count = cursor.fetchone()[0]
        print(f"✅ Trip Updates table has {count} records.")

        if count > 0:
            cursor.execute("SELECT * FROM trip_updates ORDER BY update_timestamp DESC LIMIT 5")
            latest_entries = cursor.fetchall()
            print("\n📌 Latest Trip Updates Entries:")
            for entry in latest_entries:
                print(entry)
        else:
            print("⚠️ No Trip Update data found. Check if `trip_updates.py` ran correctly.")

    except Exception as e:
        print(f"❌ Error checking Trip Updates table: {e}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    print("\n🔎 Running Trip Updates Database Tests...\n")
    test_database_connection()
    test_trip_updates_data()
