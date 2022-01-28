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
