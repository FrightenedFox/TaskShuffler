from typing import List

from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def get_yaml_dict(filepath: str) -> dict:
    with open(filepath, mode="r") as file:
        yaml_dict: dict = load(file, Loader=Loader)
    return yaml_dict


def get_topics(topics_list: List[dict]):
    pass


def get_tasks(yaml_dict: dict):
    pass


if __name__ == '__main__':
    print(get_yaml_dict("../../input_files/details.yml"))
