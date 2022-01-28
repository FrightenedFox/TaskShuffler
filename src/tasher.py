import argparse
import logging
from config import config
from logging_setup import initialize_logging
from tasks import Dispatcher

initialize_logging()
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument('-u', '--user',
                           default="xxx",
                           help='username')

main_parser = argparse.ArgumentParser()
command_subparsers = main_parser.add_subparsers(title="commands", dest="cmd")
add_parser = command_subparsers.add_parser("add",
                                           help="add tasks to the database",
                                           parents=[parent_parser])
add_parser.add_argument("path", help="folder or file to add", type=str)
add_parser.add_argument("-d", "--task-details",
                        help="CSV file with details about each task",
                        dest="details_csv")
add_parser.add_argument("--sep", help="separator used in the CSV file",
                        dest="csv_sep", default=';')

args = main_parser.parse_args()

dp = Dispatcher()
match args.cmd:
    case "add":
        dp.add_tasks(path=args.path,
                     details_csv=args.details_csv,
                     sep=args.csv_sep)
    case _:
        pass
