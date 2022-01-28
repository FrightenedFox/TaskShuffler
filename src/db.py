import logging

import pandas as pd
import psycopg2
from config import config


class TaskShufflerDB:
    """ Makes the communication with the database easier."""
    def __init__(self):
        self.conn = None
        self.is_connected = False

    def connect(self):
        """Connect to the PostgreSQL database server."""
        params = config("postgresql")
        logging.info("Connecting to the PostgreSQL database...")
        self.conn = psycopg2.connect(**params)

        # Display PostgreSQL version
        cur = self.conn.cursor()
        cur.execute('SELECT version()')
        logging.info(f"PostgreSQL version:\t{cur.fetchone()}")
        cur.close()

        if self.conn is not None:
            self.is_connected = True

    def disconnect(self):
        """Disconnect from the PostgreSQL database server."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logging.info("Database connection closed.")
            self.is_connected = False
        else:
            # executes when there was no connection
            logging.warning("Database was asked to be closed, but there was no connection.")
            logging.warning(f"self.is_connected set to False (before it was {self.is_connected}).")
            self.is_connected = False

    def insert_task(self, df_row: pd.Series):
        cur = self.conn.cursor()
        se_query = (f"SELECT EXISTS(SELECT 1 "
                    f"FROM public.subjects s "                    
                    f"WHERE s.name = %(subject_name)s);")
        cur.execute(se_query, {"subject_name": df_row.subject})
        subject_exists = cur.fetchone()[0]
        cur.close()
        logging.debug(f"Add {subject_exists=}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = TaskShufflerDB()
    db.connect()
    db.insert_task(pd.Series({"subject": "something"}))
    db.disconnect()
