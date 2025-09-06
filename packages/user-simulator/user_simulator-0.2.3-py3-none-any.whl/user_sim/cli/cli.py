import argparse
from argparse import Namespace
from chatbot_connectors import parse_connector_params

def parse_chat_arguments() -> Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="User Simulator - Converses with chatbots to test capabilities")

    # default_sessions = 3
    # default_turns = 8
    # default_model = "gpt-4o-mini"
    default_output_dir = "output"
    default_technology = "taskyto"


    parser.add_argument(
        "-rfy"
        "--run-from-yaml",
        type=str,
        default=None,
        help="Path to the project folder which contains run.yaml."
             "Runs Sensei with CLI arguments contained in the run.yaml file."
             "Example: --run-from-yaml /path/to/project/folder",
    )

    parser.add_argument(
        "-ic",
        "--ignore-cache",
        type=int,
        default=0,
        help=f"Cache is ignored during the testing process.",
    )

    parser.add_argument(
        "-t",
        "--technology",
        type=str,
        default=default_technology,
        help=f"Chatbot technology to use (default: {default_technology})",
    )

    parser.add_argument(
        "-cp",
        "--connector-params",
        type=parse_connector_params,
        default=None,
        help="Connector parameters as JSON string or key=value pairs separated by commas. "
        'Examples: \'{"base_url": "http://localhost", "port": 8080}\' or '
        '"base_url=http://localhost,port=8080". Use --list-connector-params <technology> to see required parameters for each connector.',
    )

    parser.add_argument(
        "-pp",
        "--project-path",
        type=str,
        default=None,
        help="The project path where all testing content is stored for a specific project."
    )

    parser.add_argument(
        "-up",
        "--user-profile",
        type=str,
        default=None,
        help="Name of the user profile YAML or the folder containing user profiles to use in the testing process."
    )

    #todo: extract
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=default_output_dir,
        help=f"Output directory for results and profiles (default: {default_output_dir})",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )

    parser.add_argument(
        "-cc",
        "--clean-cache",
        action="store_true",
        help=f"Cache is cleaned after the testing process",
    )

    parser.add_argument(
        "-uc",
        "--update-cache",
        action="store_true",
        help=f"Cache is updated with new content if previous cache was saved",
    )

    #todo: implement
    parser.add_argument(
        "--list-connector-params",
        type=str,
        metavar="TECHNOLOGY",
        help="List the available parameters for a specific chatbot technology and exit",
    )

    #todo: implement
    parser.add_argument(
        "--list-connectors",
        action="store_true",
        help="List all available chatbot connector technologies and exit",
    )

    return parser.parse_args()