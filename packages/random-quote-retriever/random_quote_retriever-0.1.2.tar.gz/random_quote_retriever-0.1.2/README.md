# CLI Random Quote Retriever
## By mhasanali2010
## PyPI Project Link
https://pypi.org/project/random-quote-retriever/
## What it does?
- Uses `zenquotes.io/api` to retrieve a random quote. Can optionally save the quote in `./quotes.json` if you like it
- API handling using `requests` and argument parsing using `argparse`
## Setting up
- Download the project:
    ```bash
    python3 -m pip install random-quote-retriever
    ```
## Usage
### Retrieving Quotes
Run the script using (retrieve a random quote):
```bash
quote
```
### Saving Quotes
Run the script with --save:
```
quote --save
```
The last quote that was retrieved will be saved in `./quotes.json`
### Viewing Saved Quotes
Run the script with --view-saved:
```
quote --view-saved
```
All of the quotes that have been saved in `./quotes.json` will be displayed.
