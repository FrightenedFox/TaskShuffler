import os
import sys
import glob
import shutil
from datetime import datetime

import pandas as pd

from db import TaskShufflerDB
from config import config

# TODO: separate python file with constants
SUPPORTED_FILETYPES = [".png", ".jpg", ".jpeg"]


def clean_path(path: str, trailing_slash: bool = False) -> str:
    """Sets the correct slashes for different operating systems, adds the
    trailing slash to the end if `trailing_slash` is set to True."""
    if trailing_slash and path[-1] not in ["/", "\\"]:
        path += "/"
    if sys.platform.startswith('win'):
        path = path.replace("/", "\\")
        return path
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        path = path.replace("\\", "/")
        return path
    else:
        raise OSError("This operation system is not supported yet.")


class Dispatcher:
    """Contains all the algorithms for each command."""
    _difficulty_trials = 0

    def __init__(self, db: TaskShufflerDB):
        """Initializes all the common attributes of the Dispatcher class.
        Makes sure all necessary paths exist.

        Parameters
        ----------
            db:
                An instance of the TaskShufflerDB class.
        """
        self.db = db
        self.params = config("tasher")
        self.private_dir = clean_path(os.path.join(self.params["directory"], ".tasher/"))
        self.solutions_dir = clean_path(os.path.join(self.private_dir, "solutions/"))
        self.solution_prefix = self.params['solution_prefix']
        if not os.path.exists(self.private_dir):
            os.makedirs(self.private_dir)
        if not os.path.exists(self.solutions_dir):
            os.makedirs(self.solutions_dir)

    def add_tasks(self, path: str, details_csv: str, sep: str) -> None:
        path = clean_path(path)
        if os.path.isdir(path):
            # Given path is a directory
            path = clean_path(path, trailing_slash=True)
            files_df = pd.DataFrame(columns=["filepath", "filename", "filetype"])
            for i, filepath in enumerate(glob.iglob(path + "**/**", recursive=True)):
                filetype = os.path.splitext(filepath)[1]
                if filetype in SUPPORTED_FILETYPES:
                    files_df.at[i] = [filepath, os.path.basename(filepath), filetype]
            files_df.drop_duplicates(inplace=True)
            if details_csv is not None:
                details_df = pd.read_csv(details_csv, sep=sep)
                df = files_df.merge(details_df, on="filename",
                                    how="left", validate="one_to_one")
            else:
                df = self.get_details(files_df.copy())
        elif os.path.splitext(path)[1] in SUPPORTED_FILETYPES:
            # Given path is a supported solution file
            df = self.get_details(pd.DataFrame({
                "filepath": [path],
                "filename": [os.path.basename(path)],
                "filetype": [os.path.splitext(path)[1]],
            }))
        else:
            raise ValueError(f"Filetype is not supported yet. "
                             f"Accepted filetypes: {SUPPORTED_FILETYPES}")

        # Make sure there is a directory for each topic
        df.loc[:, "topic_path"] = self.solutions_dir + df.topic
        for topic_path in df.topic_path.drop_duplicates():
            if not os.path.exists(topic_path):
                os.makedirs(topic_path)

        # Add info to the database and copy files to private folder
        for index, row in df.iterrows():
            task_id = self.db.insert_task(row)
            new_solution_path = os.path.join(
                row.topic_path,
                f"{self.solution_prefix}{task_id}{row.filetype}")
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
                   group_by: str, output_dir: str,
                   csv_sep: str = ";") -> None:
        df = self.db.get_tasks(filters)
        if group_by == "none":
            print(df)
        else:
            df.groupby(group_by).apply(print)

        # If pdf directory is given generate all files
        if output_dir is not None and os.path.isdir(output_dir) and df.size > 0:
            with open(self.params["latex_preamble"]) as preamble,\
                    open(self.params["latex_preamble"]) as ending\
                    :
                pass

            # Create folders
            results_folder = os.path.join(
                output_dir,
                f"{self.params['folder_prefix']}"
                f"{datetime.now().strftime(' %Y-%m-%d %H-%M-%S')}")
            solution_folder = os.path.join(
                results_folder, f"{self.solution_prefix}images")
            os.makedirs(results_folder)
            os.makedirs(solution_folder)

            # Copy solutions to the destination folder
            for index, row in df.iterrows():
                start_solution_path = os.path.join(
                    row.topic_path,
                    f"{self.solution_prefix}{row.task_id}{row.filetype}").replace(
                    "/", "\\"
                )
                destination_solution_path = os.path.join(
                    solution_folder,
                    f"{self.solution_prefix}{index + 1}{row.filetype}").replace(
                    "/", "\\"
                )
                shutil.copy(start_solution_path, destination_solution_path)

            csv_path = os.path.join(results_folder, "result.csv")
            df.to_csv(csv_path, sep=csv_sep,
                      encoding="UTF-8", index_label="result_index")

        elif output_dir is not None and not os.path.isdir(output_dir):
            raise ValueError("Given path is not a directory")
