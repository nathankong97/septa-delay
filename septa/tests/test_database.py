import sqlite3
from config import GTFS_DB_PATH


def test_database_connection():
    """Test if the database connection is working."""
    try:
        conn = sqlite3.connect(GTFS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        print("\n✅ Database Connection Successful!")
        print(f"📌 Tables in database: {tables}")

    except Exception as e:
        print(f"\n❌ Database Connection Failed: {e}")


def test_gtfs_data():
    """Check if GTFS tables have data."""
    conn = sqlite3.connect(GTFS_DB_PATH)
    cursor = conn.cursor()

    tables_to_check = ["trips", "calendar"]

    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Table `{table}` has {count} records.")
        except Exception as e:
            print(f"❌ Error checking `{table}`: {e}")

    cursor.close()
    conn.close()


def test_realtime_query():
    """Test if the `get_realtime_queries` function works."""
    conn = sqlite3.connect(GTFS_DB_PATH)
    cursor = conn.cursor()

    day_of_week = "monday"  # Change as needed
    query = f"""
        SELECT DISTINCT block_id 
        FROM trips t 
        INNER JOIN calendar c 
        ON t.service_id = c.service_id
        WHERE c.{day_of_week} = 1;
    """

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        output = [str(row[0]) for row in result]

        print(f"\n✅ Query executed successfully! Results: {output}")
    except Exception as e:
        print(f"\n❌ Query failed: {e}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    print("\n🔎 Running Database Tests...\n")
    test_database_connection()
    test_gtfs_data()
    test_realtime_query()
