import requests
import logging
import argparse
import json
import os
from typing import Any


def initialize_logging() -> None:
    """Initialize Logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="logs.log",
        filemode="a"
    )


def initialize_argument_parser() -> argparse.Namespace:
    """Initialize the Argument Parser"""
    parser = argparse.ArgumentParser(description='finds a random quote')
    parser.add_argument("--save", action="store_true", help="save the quote to file")
    parser.add_argument("--view-saved", action="store_true", help="display saved quotes")
    args = parser.parse_args()

    return args


def check_file_existence(file_path: str) -> bool:
    """Check whether a file exists and if it is not empty"""
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0


def load_from_json(file_path: str) -> Any:
    """Load data from JSON file"""
    with open(file_path, "r") as f:
        data = json.load(f)
        return data
    

def write_to_json(file_path: str, data: Any) -> None:
    """Write data to JSON file"""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def main() -> None:
    try:
        initialize_logging()
        args = initialize_argument_parser()
        save = args.save
        view = args.view_saved
        base_url = "https://zenquotes.io/api/random"
        response = requests.get(base_url)
        data_retrieved = response.status_code == 200

        json_file = "quotes.json"

        if not save and not view:
            if data_retrieved:
                logging.info(f"Data Retrieved Successfully {response.status_code}")
                data = response.json()
                raw_quote = data[0]["q"]
                author = data[0]["a"]
                quote = f"\"{raw_quote}\"\n-{author}"
                print(quote)

                quote_dict = {"author": author, "quote": raw_quote}
                write_to_json("last_quote.json", quote_dict)
            else:
                logging.error(f"Data Not Retrieved {response.status_code}")
                print("Data Not Retrieved")
        if save:
            if check_file_existence("last_quote.json"):
                file = load_from_json("last_quote.json")
                if check_file_existence(json_file):
                    data = load_from_json(json_file)
                else:
                    data = []
                data.append(file)
                write_to_json(json_file, data)

                logging.info("Quote saved successfully")
                print("Quote Saved")
            else:
                logging.error("Error while saving: last quote was not found")
                print("Could not save quote as no quote was found.")
        if view:
            if check_file_existence(json_file):
                data = load_from_json(json_file)
                for each in data:
                    print(f"\"{each["quote"]}\" -{each["author"]}")
    except Exception as e:
        logging.error(f"Error Occured: {e}")
        print("An error occured while retrieving, please try again later.")


if __name__ == "__main__":
    main()
