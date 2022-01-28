import os
import glob
import shutil

import pandas as pd

from db import TaskShufflerDB
from config import config

SUPPORTED_FILETYPES = [".png", ".jpg", ".jpeg"]


class Subject:
    subject_name: str
    subject_folder: str
    topics_list: list
    
    def __init__(self, name: str, folder: str) -> None:
        self.subject_name = name
        self.subject_folder = folder
        pass


class Topic:
    topic_name: str
    topic_folder: str
    tasks_list: list

    def __init__(self, name: str, folder: str) -> None:
        self.topic_name = name
        self.topic_folder = folder
        pass


class Task:
    task_tex: str
    solution_path: str
    difficulty: int

    def __init__(self, task_tex: str, solution: str, difficulty: int = 3) -> None:
        self.task_tex = task_tex
        self.solution_path = solution
        self.difficulty = difficulty
        pass


class Dispatcher:
    _difficulty_trials = 0

    def __init__(self, db: TaskShufflerDB) -> None:
        self.db = db
        self.params = config("tasher")
        self.private_dir = os.path.join(self.params["directory"], ".tasher/")
        self.solutions_dir = os.path.join(self.private_dir, "solutions/")
        if not os.path.exists(self.private_dir):
            os.makedirs(self.private_dir)
        if not os.path.exists(self.solutions_dir):
            os.makedirs(self.solutions_dir)

    def add_tasks(self, path: str, details_csv: str, sep: str) -> None:
        # Read all given files
        if os.path.isdir(path):
            if path[-1] not in ["/", "\\"]:
                path += "/"
            files_df = pd.DataFrame(columns=["filepath", "filename"])
            for i, filepath in enumerate(glob.iglob(path + "**/**", recursive=True)):
                if os.path.splitext(filepath)[1] in SUPPORTED_FILETYPES:
                    files_df.at[i] = [filepath, os.path.basename(filepath)]
            files_df.drop_duplicates(inplace=True)
            if details_csv is not None:
                details_df = pd.read_csv(details_csv, sep=sep)
                df = files_df.merge(details_df, on="filename",
                                    how="left", validate="one_to_one")
            else:
                df = self.get_details(files_df.copy())
        else:
            df = self.get_details(pd.DataFrame({
                "filepath": [path],
                "filename": [os.path.basename(path)],
            }))

        # Make sure there is a directory for each topic
        df.loc[:, "topic_path"] = self.solutions_dir + df.topic
        for topic_path in df.topic_path.drop_duplicates():
            if not os.path.exists(topic_path):
                os.makedirs(topic_path)

        # Add info to the database and copy files to private folder
        for index, row in df.iterrows():
            task_id = self.db.insert_task(row)
            sol_extension = os.path.splitext(row.filename)[1]
            new_solution_path = os.path.join(row.topic_path,
                                             f"sol_{task_id}{sol_extension}")
            shutil.copy(row.filepath, new_solution_path)

    def get_details(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ask user for details about each file in the df."""
        df.loc[:, "subject"] = input("What subject are these tasks for? ")
        df.loc[:, "topic"] = input("What is the topic of these tasks? ")
        for row_id, row in df.iterrows():
            print(f"Working with the task whose filename is {row.filename}.")
            df.loc[row_id, "tex"] = input(f"Provide the TeX for that task: ")
            df.loc[row_id, "difficulty"] = self.get_difficulty()
        return df

    def get_difficulty(self, max_trials: int = 5) -> int:
        """Ask user until it gives correct answer or exceeds max number of trials."""
        difficulty = input(f"Provide the TeX for that task (integer, default=3): ")
        self._difficulty_trials += 1
        if not difficulty:
            self._difficulty_trials = 0
            return 3
        elif self._difficulty_trials < max_trials:
            try:
                int_difficulty = int(difficulty)
            except ValueError:
                print("Only integers are supported, preferably in the range 1 to 5.")
                return self.get_difficulty()
            else:
                self._difficulty_trials = 0
                return int_difficulty
        else:
            print("To many trials. Skipping with default value = 3")
            self._difficulty_trials = 0
            return 3

    def list_subjects(self, filters: pd.Series) -> None:
        print(self.db.get_subjects(filters))

    def list_topics(self, filters: pd.Series, group_by: str) -> None:
        df = self.db.get_topics(filters)
        if group_by == "none":
            print(df)
        else:
            df.groupby(group_by).apply(print)

    def list_tasks(self, filters: pd.Series,
                   group_by: str,
                   pdf_dir: str) -> None:
        df = self.db.get_tasks(filters)
        if group_by == "none":
            print(df)
        else:
            df.groupby(group_by).apply(print)

        # If pdf directory is given generate pdf
        if pdf_dir is not None:
            pass
