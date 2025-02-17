from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlite3
import logging
from datetime import datetime
import pandas as pd
import os

from config import GTFS_DB_PATH, TRAIN_VIEW_DB_URL, TRIP_UPDATES_DB_URL

logger = logging.getLogger("database")
engine = create_engine(TRAIN_VIEW_DB_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
trip_updates_engine = create_engine(TRIP_UPDATES_DB_URL, echo=False, connect_args={"check_same_thread": False})
TripUpdatesSession = sessionmaker(autocommit=False, autoflush=False, bind=trip_updates_engine)
Base = declarative_base()


class TrainView(Base):
    __tablename__ = "train_view"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    train_id = Column(String, nullable=False)
    lat = Column(Float)
    lon = Column(Float)
    service = Column(String)
    destination = Column(String)
    current_stop = Column(String)
    next_stop = Column(String)
    line = Column(String)
    consist = Column(String)
    heading = Column(Float)
    late = Column(Integer)
    source = Column(String)
    track = Column(String)
    track_change = Column(String)

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def store_train_view(data, timestamp=None):
    session = SessionLocal()
    if timestamp is None:
        timestamp = datetime.utcnow()

    try:
        for train in data:
            train_entry = TrainView(
                timestamp=timestamp,
                train_id=train.get("trainno"),
                lat=float(train["lat"]) if train["lat"] else None,
                lon=float(train["lon"]) if train["lon"] else None,
                service=train.get("service"),
                destination=train.get("dest"),
                current_stop=train.get("currentstop"),
                next_stop=train.get("nextstop"),
                line=train.get("line"),
                consist=train.get("consist"),
                heading=float(train["heading"]) if train["heading"] else None,
                late=int(train["late"]) if train["late"] else None,
                source=train.get("SOURCE"),
                track=train.get("TRACK"),
                track_change=train.get("TRACK_CHANGE"),
            )
            existing_entry = session.query(TrainView).filter_by(
                train_id=train_entry.train_id, timestamp=train_entry.timestamp
            ).first()
            if existing_entry:
                session.merge(train_entry)
            else:
                session.add(train_entry)

        session.commit()
        print("✅ Train View data stored in SQLite successfully.")

    except Exception as e:
        session.rollback()
        print(f"❌ Failed to store Train View data: {e}")
    finally:
        session.close()


class TripUpdate(Base):
    __tablename__ = "trip_updates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    trip_id = Column(String, nullable=False)
    stop_id = Column(String, nullable=False)
    stop_sequence = Column(Integer)
    delay = Column(Integer)
    uncertainty = Column(Integer)
    update_timestamp = Column(DateTime, nullable=False)

    __table_args__ = ({"sqlite_autoincrement": True},)


def init_trip_updates_db():
    Base.metadata.create_all(bind=trip_updates_engine)


def store_trip_updates(data, timestamp=None):
    session = TripUpdatesSession()
    if timestamp is None:
        timestamp = datetime.utcnow()

    try:
        for entity in data:
            trip_info = entity.get("tripUpdate", {})
            trip_id = trip_info.get("trip", {}).get("tripId")

            for stop_update in trip_info.get("stopTimeUpdate", []):
                trip_entry = TripUpdate(
                    trip_id=trip_id,
                    stop_id=stop_update.get("stopId"),
                    stop_sequence=stop_update.get("stopSequence"),
                    delay=int(stop_update["arrival"]["delay"]) if "arrival" in stop_update else None,
                    uncertainty=int(stop_update["arrival"]["uncertainty"]) if "arrival" in stop_update else None,
                    update_timestamp=datetime.utcfromtimestamp(int(trip_info.get("timestamp", timestamp.timestamp()))),
                )

                session.add(trip_entry)

        session.commit()
        print("✅ Trip Update data stored in SQLite successfully.")

    except Exception as e:
        session.rollback()
        print(f"❌ Failed to store Trip Update data: {e}")
    finally:
        session.close()


def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = sqlite3.connect(GTFS_DB_PATH)
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return None


def update_database(data_dir):
    """Store GTFS data in SQLite database."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        for file in os.listdir(data_dir):
            if file.endswith(".txt"):
                file_path = os.path.join(data_dir, file)
                df = pd.read_csv(file_path)

                if df.empty:
                    logger.warning(f"Skipping empty file: {file}")
                    continue

                table_name = os.path.splitext(file)[0]
                df.to_sql(table_name, conn, if_exists="replace", index=False)

        conn.commit()
        logger.info("GTFS database updated successfully.")

    except Exception as e:
        logger.error(f"Database update failed: {e}")
    finally:
        conn.close()


def get_realtime_queries():
    """Fetch block IDs for real-time schedule queries from the database."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        day_of_week = datetime.now().strftime('%A').lower()  # Example: "monday"

        query = f"""
        SELECT DISTINCT block_id 
        FROM trips t 
        INNER JOIN calendar c 
        ON t.service_id = c.service_id
        WHERE c.{day_of_week} = 1;
        """
        logger.info(f"Executing query: {query}")

        cursor.execute(query)
        result = cursor.fetchall()
        output = [str(row[0]) for row in result]

        logger.info(f"Query result: {output}")

        cursor.close()
        return output

    except Exception as e:
        logger.error(f"Error fetching real-time queries: {e}")
        return []
    finally:
        conn.close()
