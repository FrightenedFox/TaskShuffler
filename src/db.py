import logging
from typing import Tuple

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extensions import register_adapter, AsIs

from config import config
import sqlalchemy


def adapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def adapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(np.float64, adapt_numpy_float64)
register_adapter(np.int64, adapt_numpy_int64)


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
        self.sqlalchemy_engine = None

    def connect(self):
        """Connect to the PostgreSQL database server."""
        params = config("postgresql")
        logging.info("Connecting to the PostgreSQL database...")
        self.conn = psycopg2.connect(**params)
        self.sqlalchemy_engine = sqlalchemy.create_engine(
            'postgresql+psycopg2://',
            creator=lambda: self.conn)

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
            self.sqlalchemy_engine.dispose()
            self.conn = None
            logging.info("Database connection closed.")
            self.is_connected = False
        else:
            # executes when there was no connection
            logging.warning("Database was asked to be closed, but there was no connection.")
            logging.warning(f"self.is_connected set to False (before it was {self.is_connected}).")
            self.is_connected = False

    def insert_task(self, task_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Creates task and returns its id. If task isn't new, also deletes
        previous solutions and returns their old ids."""
        cur = self.conn.cursor()

        # Make sure the subject exists
        upsert_subject_query = ("INSERT INTO public.subjects (subject_name) "
                                "VALUES (%(subject_name)s) "
                                "ON CONFLICT (subject_name) DO UPDATE "
                                "SET subject_name = excluded.subject_name "
                                "RETURNING subject_id;")
        cur.execute(upsert_subject_query,
                    {"subject_name": task_df.subject[0]})
        subject_id = cur.fetchone()[0]

        # Make sure the topic exists
        insert_topic_query = ("INSERT INTO public.topics (topic_name, topic_folder) "
                              "VALUES (%(topic_name)s, %(topic_path)s) "
                              "ON CONFLICT (topic_name) DO UPDATE "
                              "SET topic_name = excluded.topic_name, "
                              "    topic_folder = excluded.topic_folder "
                              "RETURNING topic_id;")
        cur.execute(insert_topic_query,
                    {"topic_name": task_df.topic[0],
                     "topic_path": task_df.topic_path[0]})
        topic_id = cur.fetchone()[0]

        # Make sure the topic is connected to the subject
        upsert_subject_topic_query = ("INSERT INTO public.subject_topic"
                                      "(subject_id, topic_id) VALUES "
                                      "(%(subject_id)s, %(topic_id)s) "
                                      "ON CONFLICT DO NOTHING; ")
        cur.execute(upsert_subject_topic_query,
                    {"subject_id": subject_id,
                     "topic_id": topic_id})

        # Create task
        insert_task_query = ("INSERT INTO public.tasks "
                             "(task_tex, difficulty, answer) VALUES "
                             "(%(task_tex)s, %(difficulty)s, %(answer)s) "
                             "ON CONFLICT (task_tex) DO UPDATE "
                             "SET difficulty = excluded.difficulty,"
                             "    answer = excluded.answer "
                             "RETURNING task_id;")
        cur.execute(insert_task_query,
                    {"task_tex": task_df.tex[0],
                     "difficulty": task_df.difficulty[0],
                     "answer": task_df.answer[0]})
        task_id = cur.fetchone()[0]

        # Associate task with the topic
        upsert_topic_task_query = ("INSERT INTO public.topic_task "
                                   "(topic_id, task_id) VALUES "
                                   "(%(topic_id)s, %(task_id)s) "
                                   "ON CONFLICT DO NOTHING; ")
        cur.execute(upsert_topic_task_query,
                    {"topic_id": topic_id,
                     "task_id": task_id})
        self.conn.commit()
        cur.close()

        # Delete all solutions of this task, if such exist
        delete_solutions_query = ("DELETE FROM public.solutions "
                                  "WHERE task_id = %(task_id)s "
                                  "RETURNING solution_id, solution_filetype;")
        deleted_solutions = pd.read_sql_query(delete_solutions_query,
                                              self.sqlalchemy_engine,
                                              params={"task_id": task_id})
        deleted_solutions.columns = ["solution_id", "solution_filetype"]

        # Add solution file
        solution_query_inserts, insert_vals = "", ()
        for sol_id, sol_row in task_df.iterrows():
            solution_query_inserts += "(%s, %s), "
            insert_vals += (sol_row.solution_filetype, task_id)
        # remove two last symbols ", " from the last insert values
        solution_query_inserts = solution_query_inserts[:-2]

        insert_solution_query = (f"INSERT INTO public.solutions"
                                 f"(solution_filetype, task_id) VALUES "
                                 f"{solution_query_inserts} "
                                 f"RETURNING solution_id;")
        solution_ids = pd.read_sql_query(insert_solution_query,
                                         self.sqlalchemy_engine,
                                         params=insert_vals)
        solution_ids.columns = ["solution_id"]

        logging.debug(f"New task @{task_id=} about {task_df.topic[0]} in the "
                      f"{task_df.subject[0]} subject.")
        return solution_ids, deleted_solutions

    def get_subjects(self, filters: pd.Series) -> pd.DataFrame:
        filter_query = combine_filters(filters)
        query = (f"SELECT s.subject_name "
                 f"FROM public.subjects s, public.topics t, public.subject_topic st "
                 f"WHERE s.subject_id = st.subject_id "
                 f"AND t.topic_id = st.topic_id "
                 f"{filter_query}; ")
        df = pd.read_sql_query(query, self.sqlalchemy_engine).drop_duplicates()
        df.columns = ["subject"]
        return df

    def get_topics(self, filters: pd.Series) -> pd.DataFrame:
        filter_query = combine_filters(filters)
        query = (f"SELECT s.name, t.topic_name "
                 f"FROM public.subjects s, public.topics t, public.subject_topic st "
                 f"WHERE s.subject_id = st.subject_id "
                 f"AND t.topic_id = st.topic_id "
                 f"{filter_query}; ")
        df = pd.read_sql(query, self.sqlalchemy_engine).drop_duplicates()
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
        df = pd.read_sql(query, self.sqlalchemy_engine).drop_duplicates()
        df.columns = [
            "subject", "topic", "tex", "difficulty", "topic_path", "task_id", "filetype"
        ]
        return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = TaskShufflerDB()
    db.connect()
    db.disconnect()
