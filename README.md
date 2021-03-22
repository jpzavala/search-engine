# Dependencies/Files
1. Install the dependencies listed in requirements.txt
2. To run the indexer, the DEV folder containing the web pages must be downloaded and placed in this project folder.

# Indexing 
1. Run main.py
2. The inverted index will be automatically written into inverted_index.txt after merging parts.
3. Index of index for file seeking is written in index_of_index.json file.
4. Mapping from docIDs to urls is saved in docids.json

# Search
1. After running main.py, run search.py to use the search engine.
2. Type your query in the console after being prompted for input.
3. Type '-quit' to stop reprompting and exit the program.

# Web GUI
1. After running main.py, run web_gui.py
2. Go to http://127.0.0.1:8080/ in your internet browser.
3. Type your query into the text form and press enter to retrieve results (or click on the 'search' button).
4. The Web GUI runs in a debug server, to close just ctrl-c the program from console.