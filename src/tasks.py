import os
import sys
import logging
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
    _difficulty_trials: int = 0
    _max_difficulty_trials: int = 5

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

    def get_sol_filename(self,
                         solution_id: int,
                         solution_filetype: str) -> str:
        """Returns solution filename."""
        return f"{self.solution_prefix}{solution_id}{solution_filetype}"

    def get_sol_path(self,
                     solution_id: int,
                     solution_filetype: str) -> str:
        """Returns full or relative path to the solution."""
        return os.path.join(
            self.solutions_dir,
            self.get_sol_filename(solution_id, solution_filetype)
        )

    def add_tasks(self, path: str, details_csv: str, sep: str) -> None:
        path = clean_path(path)
        if os.path.isdir(path):
            # Given path is a directory
            solutions_df = pd.DataFrame(columns=["solution_name", "solution_path"])
            for i, item in enumerate(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    # item_path is a directory
                    for j, sub_item in enumerate(os.listdir(item_path)):
                        sub_item_path = os.path.join(item_path, sub_item)
                        if os.path.splitext(sub_item_path)[1] in SUPPORTED_FILETYPES:
                            solutions_df = pd.concat([solutions_df, pd.DataFrame({
                                "solution_name": [os.path.splitext(item)[0]],
                                "solution_path": [sub_item_path],
                                "solution_filetype": [os.path.splitext(sub_item_path)[1]],
                            })], ignore_index=True)
                elif os.path.splitext(item_path)[1] in SUPPORTED_FILETYPES:
                    # item_path is a supported file
                    solutions_df = pd.concat([solutions_df, pd.DataFrame({
                        "solution_name": [os.path.splitext(item)[0]],
                        "solution_path": [item_path],
                        "solution_filetype": [os.path.splitext(item_path)[1]],
                    })], ignore_index=True)
                else:
                    logging.warning(f"Unsupported file was skipped: {item_path}")

            print(solutions_df)

            if details_csv is not None:
                details_df = pd.read_csv(details_csv, sep=sep)
                details_df.loc[:, "solution_name"] = details_df.solution.apply(
                    lambda x: os.path.splitext(os.path.basename(x))[0]
                )
                df = solutions_df.merge(details_df, on="solution_name",
                                        how="inner", validate="many_to_one")
            else:
                df = self.get_task_details(solutions_df.copy())
        elif os.path.splitext(path)[1] in SUPPORTED_FILETYPES:
            # Given path is a supported solution file
            df = self.get_task_details(pd.DataFrame({
                "solution_name": [os.path.splitext(os.path.basename(path))[0]],
                "solution_path": [path],
                "solution_filetype": [os.path.splitext(path)[1]],
            }))
        else:
            raise ValueError(f"Filetype is not supported yet. "
                             f"Accepted filetypes: {SUPPORTED_FILETYPES}")

        # Add info to the database and copy files to private folder
        df.groupby("solution_name").apply(self.task_to_db)

    def task_to_db(self, task_df: pd.DataFrame) -> None:
        """Adds a new task with all of its solutions to the DB."""
        task_df.reset_index(inplace=True)
        solution_ids, deleted_solutions = self.db.insert_task(task_df)

        # Copy files to private directory and rename them accordingly
        for row_id, sol in solution_ids.iterrows():
            new_solution_path = self.get_sol_path(
                sol.solution_id,
                task_df.solution_filetype[row_id])
            shutil.copy(task_df.solution_path[row_id], new_solution_path)
        logging.debug(f"Inserted solutions:\n {solution_ids}")

        # Delete old solutions from private directory
        for row_id, deleted_sol in deleted_solutions.iterrows():
            os.remove(self.get_sol_path(
                solution_id=deleted_sol.solution_id,
                solution_filetype=deleted_sol.solution_filetype
            ))
        if deleted_solutions.size > 0:
            logging.info(f"Deleted solutions:\n {deleted_solutions}")

    def get_task_details(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ask user for details about each file in the df."""
        df.loc[:, "subject"] = input("\nWhat subject are these tasks for? ")
        df.loc[:, "topic"] = input("What is the topic of these tasks? ")
        for row_id, row in df.iterrows():
            print(f"\n--- Working with the solution "
                  f"whose name is '{row.solution_name}' ---")
            df.loc[row_id, "tex"] = input(f"Provide the TeX for that task: ")
            df.loc[row_id, "difficulty"] = self.get_task_difficulty()
            df.loc[row_id, "answer"] = input(
                f"Provide the answer for that solution: ")
        return df

    def get_task_difficulty(self) -> int:
        """Ask user until it gives correct answer or exceeds max number of trials."""
        difficulty = input(f"Provide the difficulty level "
                           f"of that task (integer, default=3): ")
        self._difficulty_trials += 1
        if not difficulty:
            self._difficulty_trials = 0
            return 3
        elif self._difficulty_trials < self._max_difficulty_trials:
            try:
                int_difficulty = int(difficulty)
            except ValueError:
                print("Only integers are supported, preferably in the range 1 to 5.")
                return self.get_task_difficulty()
            else:
                self._difficulty_trials = 0
                return int_difficulty
        else:
            print("To many trials. Skipping with default value = 3")
            self._difficulty_trials = 0
            return 3

    def list_subjects(self, filters: pd.Series) -> None:
        print(self.db.get_subjects_topics(filters).loc[:, ["subject"]])

    def list_topics(self, filters: pd.Series, group_by: str) -> None:
        df = self.db.get_subjects_topics(filters)
        if group_by == "none":
            print(df)
        else:
            df.groupby(group_by).apply(print)

    def list_tasks(self, filters: pd.Series,
                   group_by: str, output_dir: str,
                   csv_sep: str = ";",
                   verbose: int = 0) -> None:
        df = self.db.get_tasks(filters)

        # Generate the list of solution IDs
        solution_ids_list = df.groupby("task_id").apply(lambda x: x.solution_id.tolist())
        solution_ids_list.name = "solution_ids_list"
        df = df.merge(solution_ids_list,
                      left_on="task_id",
                      right_index=True,
                      how="inner",
                      validate="many_to_one")

        # Display the result of the query
        if not verbose:
            cols = ["subject", "topic", "task_id", "difficulty", "solution_ids_list"]
            df_to_print = df.loc[:, cols].drop_duplicates(subset="task_id")
        else:
            pd.options.display.max_columns = 20
            df_to_print = df.copy()
        if group_by == "none":
            print(df_to_print)
        else:
            df_to_print.groupby(group_by).apply(print)

        # If pdf directory is given generate all files
        if output_dir is not None and os.path.isdir(output_dir) and df.size > 0:
            with open(self.params["latex_preamble"]) as preamble, \
                    open(self.params["latex_preamble"]) as ending:
                pass
        elif output_dir is not None and not os.path.isdir(output_dir):
            raise ValueError("Given path is not a directory")
