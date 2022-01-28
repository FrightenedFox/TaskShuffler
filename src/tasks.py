import os
import glob
import pandas as pd

SUPPORTED_FILETYPES = [".png", ".jpg", ".jpeg"]


def add_file(filename: str):

    pass


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

    def __init__(self):
        pass

    def add_tasks(self, path: str, details_csv: str, sep: str) -> None:
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
                print(df)
            else:
                df = self.get_details(files_df.copy())
                print(df)
        else:
            df = self.get_details(pd.DataFrame({
                "filepath": [path],
                "filename": [os.path.basename(path)],
            }))
            print(df)
        pass

    def get_details(self, df: pd.DataFrame) -> pd.DataFrame:
        df.loc[:, "subject"] = input("What subject are these tasks for? ")
        df.loc[:, "topic"] = input("What is the topic of these tasks? ")
        for row in df.index:
            print(f"Working with the task whose filename is {df.filename[row]}.")
            df.loc[row, "tex"] = input(f"Provide the TeX for that task: ")
            df.loc[row, "difficulty"] = self.get_difficulty()
        return df

    def get_difficulty(self) -> int:
        difficulty = input(f"Provide the TeX for that task (integer, default=3): ")
        self._difficulty_trials += 1
        if not difficulty:
            self._difficulty_trials = 0
            return 3
        elif self._difficulty_trials < 5:
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
