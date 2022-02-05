# Search Engine (Indexer and Search)

This project is an implementation of a search engine application in Python. It includes an indexer program, which parses HTML files and creates an inverted index. Also, it includes a search component program that prompts the user for a query and returns a ranked list of pages that are relevant for the query. The motivation for this project was to build a search engine from the ground up and optimizing code in order to achieve very short query response times comparable to industry web search engines.

## Dependencies/Files
1. Install the dependencies listed in requirements.txt

## Indexing 
1. Run main.py
2. The inverted index will be automatically written into inverted_index.txt after merging parts.
3. Index of index for file seeking is written in index_of_index.json file.
4. Mapping from docIDs to urls is saved in docids.json

## Search
1. After running main.py, run search.py to use the search engine.
2. Type your query in the console after being prompted for input.
3. Type '-quit' to stop reprompting and exit the program.

## Web GUI
1. After running main.py, run web_gui.py
2. Go to http://127.0.0.1:8080/ in your internet browser.
3. Type your query into the text form and press enter to retrieve results (or click on the 'search' button).
4. The Web GUI runs in a debug server, to close just ctrl-c the program from console.
