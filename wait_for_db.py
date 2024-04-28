import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from settings import DB_URL


def handle():
    """Custom command to wait for the database to be available"""
    print("Waiting for the database...")
    retry_count = 0

    engine = create_engine(DB_URL)

    while True:
        try:
            with engine.connect():
                print("Database available!")
                break
        except OperationalError:
            if retry_count >= 5:
                print("Unable to connect to the database.")
                return
            print("Database unavailable, waiting 3 seconds...")
            time.sleep(3)
            retry_count += 1


handle()
