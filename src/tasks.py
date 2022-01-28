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

    def __init__(self):
        pass

    def add_tasks(self, path: str, details_csv: str) -> None:
        if os.path.isdir(path):
            if path[-1] not in ["/", "\\"]:
                path += "/"
            files = pd.DataFrame(columns=["filename", "basename"])
            for i, filename in enumerate(glob.iglob(path + "**/**", recursive=True)):
                if os.path.splitext(filename)[1] in SUPPORTED_FILETYPES:
                    files.at[i] = [filename, os.path.basename(filename)]
            files.drop_duplicates(inplace=True)
            print(files)
        else:
            pass
        pass
