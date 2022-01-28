import logging

import pandas as pd
import psycopg2

from config import config
import sqlalchemy


def combine_filters(filters: pd.Series):
    query = ""
    for key, filter_list in filters.items():
        table = "s" if key == "subject" else "t"
        if filter_list is not None:
            subquery = "AND (FALSE"
            for filter_part in filter_list:
                subquery += f" OR {table}.name = '{filter_part}'"
            subquery += ") "
        else:
            subquery = ""
        query += subquery
    return query


class TaskShufflerDB:
    """ Makes the communication with the database easier."""
    def __init__(self):
        self.conn = None
        self.is_connected = False
        self.engine = None

    def connect(self):
        """Connect to the PostgreSQL database server."""
        params = config("postgresql")
        logging.info("Connecting to the PostgreSQL database...")
        self.conn = psycopg2.connect(**params)
        self.engine = sqlalchemy.create_engine('postgresql+psycopg2://', creator=lambda: self.conn)

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
            self.engine.dispose()
            self.conn = None
            logging.info("Database connection closed.")
            self.is_connected = False
        else:
            # executes when there was no connection
            logging.warning("Database was asked to be closed, but there was no connection.")
            logging.warning(f"self.is_connected set to False (before it was {self.is_connected}).")
            self.is_connected = False

    def insert_task(self, df_row: pd.Series) -> int:
        """Creates task and returns its id."""
        cur = self.conn.cursor()

        # Make sure the subject exists
        subject_exists_query = ("SELECT s.subject_id "
                                "FROM public.subjects s "
                                "WHERE s.name = %(subject_name)s;")
        cur.execute(subject_exists_query, {"subject_name": df_row.subject})
        subject_exists_ans = cur.fetchone()
        if subject_exists_ans is None:
            insert_subject_query = ("INSERT INTO public.subjects (name) "
                                    "VALUES (%(subject_name)s) "
                                    "RETURNING subject_id;")
            cur.execute(insert_subject_query, {"subject_name": df_row.subject})
            subject_id = cur.fetchone()[0]
            self.conn.commit()
        else:
            subject_id = subject_exists_ans[0]

        # Make sure the topic exists
        topic_exists_query = ("SELECT topic_id "
                              "FROM public.topics t "
                              "WHERE t.name = %(topic_name)s;")
        cur.execute(topic_exists_query, {"topic_name": df_row.topic})
        topic_exists_ans = cur.fetchone()
        if topic_exists_ans is None:
            insert_topic_query = ("INSERT INTO public.topics (name, folder) "
                                  "VALUES (%(topic_name)s, %(topic_path)s) "
                                  "RETURNING topic_id;")
            cur.execute(insert_topic_query, {"topic_name": df_row.topic,
                                             "topic_path": df_row.topic_path})
            topic_id = cur.fetchone()[0]
            self.conn.commit()
        else:
            topic_id = topic_exists_ans[0]

        # Make sure the topic is connected to the subject
        upsert_subject_topic_query = ("INSERT INTO public.subject_topic"
                                      "(subject_id, topic_id) VALUES "
                                      "(%(subject_id)s, %(topic_id)s) "
                                      "ON CONFLICT DO NOTHING; ")
        cur.execute(upsert_subject_topic_query, {"subject_id": subject_id,
                                                 "topic_id": topic_id})

        # Create task
        insert_task_query = ("INSERT INTO public.tasks "
                             "(task_tex, difficulty, filetype) VALUES "
                             "(%(task_tex)s, %(difficulty)s, %(filetype)s) "
                             "RETURNING task_id;")
        cur.execute(insert_task_query, {"task_tex": df_row.tex,
                                        "difficulty": df_row.difficulty,
                                        "filetype": df_row.filetype})
        task_id = cur.fetchone()[0]
        self.conn.commit()

        # Associate task with the topic
        upsert_topic_task_query = ("INSERT INTO public.topic_task "
                                   "(topic_id, task_id) VALUES "
                                   "(%(topic_id)s, %(task_id)s) "
                                   "ON CONFLICT DO NOTHING; ")
        cur.execute(upsert_topic_task_query, {"topic_id": topic_id,
                                              "task_id": task_id})
        self.conn.commit()
        cur.close()
        logging.debug(f"New task @{task_id=} about {df_row.topic} in the "
                      f"{df_row.subject} subject.")
        return task_id

    def get_subjects(self, filters: pd.Series) -> pd.DataFrame:
        filter_query = combine_filters(filters)
        query = (f"SELECT s.name "
                 f"FROM public.subjects s, public.topics t, public.subject_topic st "
                 f"WHERE s.subject_id = st.subject_id "
                 f"AND t.topic_id = st.topic_id "
                 f"{filter_query}; ")
        df = pd.read_sql(query, self.engine).drop_duplicates()
        df.columns = ["subject"]
        return df

    def get_topics(self, filters: pd.Series) -> pd.DataFrame:
        filter_query = combine_filters(filters)
        query = (f"SELECT s.name, t.name "
                 f"FROM public.subjects s, public.topics t, public.subject_topic st "
                 f"WHERE s.subject_id = st.subject_id "
                 f"AND t.topic_id = st.topic_id "
                 f"{filter_query}; ")
        df = pd.read_sql(query, self.engine).drop_duplicates()
        df.columns = ["subject", "topic"]
        return df

    def get_tasks(self, filters: pd.Series) -> pd.DataFrame:
        filter_query = combine_filters(filters)
        query = (f"SELECT s.name, t.name, tsk.task_tex,"
                 f"tsk.difficulty, t.folder, tsk.task_id, tsk.filetype "
                 f"FROM public.subjects s, public.topics t, public.tasks tsk, "
                 f"public.subject_topic st, public.topic_task tt "
                 f"WHERE s.subject_id = st.subject_id "
                 f"AND t.topic_id = st.topic_id "
                 f"AND t.topic_id = tt.topic_id "
                 f"AND tsk.task_id = tt.task_id "
                 f"{filter_query}; ")
        df = pd.read_sql(query, self.engine).drop_duplicates()
        df.columns = [
            "subject", "topic", "tex", "difficulty", "topic_path", "task_id", "filetype"
        ]
        return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = TaskShufflerDB()
    db.connect()
    db.disconnect()
