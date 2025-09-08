# CLI Random Quote Retriever
## By mhasanali2010

## What it does?
- Uses `zenquotes.io/api` to retrieve a random quote. Can optionally save the quote in `./quotes.json` if you like it
- API handling using `requests` and argument parsing using `argparse`

## Setting up
- Clone the repository:
    ```bash
    git clone https://github.com/mhasanali2010/random-quote-retriever
    ```
- Optional: Set up virtual environment:
    ```bash
    python3 -m venv venv
    # for macOS/Linux
    source venv/bin/activate
    # for windows (cmd)
    venv\Scripts\activate.bat
    ```
- Install requests:
    ```bash
    python3 -m pip install -r requirements.txt
    ```
- Navigate to the repository:
    ```
    cd random-quote-retriever
    ```

## Retrieving Quotes
Run the script using:
```
python3 main.py
```
## Saving Quotes
Run the script with --save:
```
python3 main.py --save
```
The last quote that was retrieved will be saved in `./quotes.json`
## Viewing Saved Quotes
Run the script with --view-saved:
```
python3 main.py --view-saved
```
All of the quotes that have been saved in `./quotes.json` will be displayed.

## Notes
- Tested only using `Python 3.13`
- Requirements are written in `./requirements.txt`