import argparse

import pandas as pd

from tasks import Dispatcher
from db import TaskShufflerDB
from logging_setup import initialize_logging

if __name__ == '__main__':
    initialize_logging()
    lists_parent_parser = argparse.ArgumentParser(add_help=False)
    lists_parent_parser.add_argument(
        "-s", "--filter-subject",
        help="filter selection to specific subjects",
        nargs="+",
        dest="filter_subject",
        metavar="FILTER"
    )
    lists_parent_parser.add_argument(
        "-t", "--filter-topic",
        help="filter selection to specific topics",
        nargs="+",
        dest="filter_topic",
        metavar="FILTER"
    )
    lists_parent_parser.add_argument(
        "-g", "--group-by",
        help="which column to group by (default=none)",
        dest="group_by",
        default="none",
        choices=["subject", "topic", "none"],
        metavar="COLUMN"
    )

    main_parser = argparse.ArgumentParser()
    command_subparsers = main_parser.add_subparsers(
        title="commands", dest="cmd")
    add_parser = command_subparsers.add_parser(
        "add", help="add tasks to the database")
    add_parser.add_argument(
        "path",
        help="folder or file to add", type=str)
    add_parser.add_argument(
        "-d", "--task-details",
        help="CSV file with details about each task", dest="details_csv")
    add_parser.add_argument(
        "--sep",
        help="separator used in the CSV file (default=;)",
        dest="csv_sep", default=';')

    list_parser = command_subparsers.add_parser(
        "list", help="list available items", parents=[lists_parent_parser])
    list_subparsers = list_parser.add_subparsers(
        title="list", dest="what_to_list")
    subject_parser = list_subparsers.add_parser(
        "subjects", help="list all subjects", parents=[lists_parent_parser])
    topics_parser = list_subparsers.add_parser(
        "topics", help="list all topics", parents=[lists_parent_parser])
    tasks_parser = list_subparsers.add_parser(
        "tasks", help="list all tasks", parents=[lists_parent_parser])
    tasks_parser.add_argument(
        "-o", "--output-dir",
        help="path where to save pdf with printed tasks and their solutions",
        dest="output_dir",
        metavar="DIR"
    )
    tasks_parser.add_argument(
        "--sep",
        help="separator used in the CSV file (default=;)",
        dest="csv_sep", default=';')

    args = main_parser.parse_args()

    db = TaskShufflerDB()
    db.connect()

    dp = Dispatcher(db)

    match args.cmd:
        case "add":
            dp.add_tasks(
                path=args.path, details_csv=args.details_csv, sep=args.csv_sep)
        case "list":
            filters = pd.Series({"subject": args.filter_subject,
                                 "topic": args.filter_topic})
            match args.what_to_list:
                case "subjects":
                    dp.list_subjects(filters)
                case "topics":
                    dp.list_topics(filters, args.group_by)
                case "tasks":
                    dp.list_tasks(filters, args.group_by,
                                  args.output_dir, args.csv_sep)

    db.disconnect()
