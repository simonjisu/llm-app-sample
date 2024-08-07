# LLM APP Sample

Two sample Applications using Langchain, Streamlit and FastAPI.

## Project Structure

```bash
llm-app-sample
├── .env
├── .gitignore
├── Pipfile
├── Pipfile.lock
├── README.md
├── requirements.txt
├── main.py  # FastAPI 
├── app.py   # Streamlit
├── engine.py  # Langchain Engine for applications
├── models.py  # Pydantic models for FastAPI
├── tools.py  # Tools for applications
└── pages
    ├── Financial QA.py  # Financial Stock QA Application
    └── Travel Searcher.py  # Travel Searcher Application
```

### Financial Stock QA

This application is a simple question answering system that can answer questions related to financial data. The application uses the OpenAI API to answer questions related to financial data. The application can answer questions related to the CEO of a company, the revenue of a company in a specific year, and the stock price of a company on a specific date.

#### Example Questions
1. Who is apple's CEO?
2. What is the revenue of apple in 2020?
3. What is apple's today's stock price?

### Travel Searcher

This application is a simple travel search engine that can search for hotels and restaurants in a specific location. The application uses the Google Search API to search for hotels and restaurants in a specific location. 

## Pre-requisites

* Python 3.11+
* SQLite3 >= 3.35.0
* Set-up `.env` file with the following content:

    ```shell
    OPENAI_API_KEY = ""
    GOOGLE_API_KEY = ""  # see Google Search API Wrapper
    GOOGLE_CSE_ID = ""  # see Google Search API Wrapper
    GOOGLE_CSE_ID_HOTEL = ""  # see Google Search API Wrapper
    GOOGLE_CSE_ID_RESTAURANT = ""  # see Google Search API Wrapper
    ```
* Install

    ```shell
    pip install -r requirements.txt
    ```

### Google Search API Wrapper
    
[link to docs](https://api.python.langchain.com/en/latest/utilities/langchain_community.utilities.google_search.GoogleSearchAPIWrapper.html)

1. Install google-api-python-client 
    - If you don’t already have a Google account, sign up. 
    - If you have never created a Google APIs Console project, read the Managing Projects page and create a project in the Google API Console. 
    - Install the library using pip install google-api-python-client

2. Enable the Custom Search API 
    - Navigate to the APIs & Services→Dashboard panel in Cloud Console. 
    - Click Enable APIs and Services. 
    - Search for Custom Search API and click on it. 
    - Click Enable. 
    URL for it: [https://console.cloud.google.com/apis/library/customsearch.googleapis.com](https://console.cloud.google.com/apis/library/customsearch.googleapis.com)

3. To create an API key: 
    - Navigate to the APIs & Services → Credentials panel in Cloud Console. 
    - Select Create credentials, then select API key from the drop-down menu. 
    - The API key created dialog box displays your newly created key. 
    - You now have an API_KEY

    Alternatively, you can just generate an API key here: [https://developers.google.com/custom-search/docs/paid_element#api_key](https://developers.google.com/custom-search/docs/paid_element#api_key)

4. Setup Custom Search Engine so you can search the entire web 
    - Create a custom search engine here: [https://programmablesearchengine.google.com/](https://programmablesearchengine.google.com/) 
    - In What to search to search, pick the Search the entire Web option. After search engine is created, you can click on it and find Search engine ID


### Install SQLite3 >= 3.35.0

```shell
# Download the latest release of SQLite source code and build the source
# amalgamation files (sqlite3.c and sqlite3.h).
$ wget https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release \
    -O sqlite.tar.gz
$ tar xzf sqlite.tar.gz
$ cd sqlite/
$ ./configure
$ make sqlite3.c

# Copy the sqlite3 amalgamation files into the root of the pysqlite3 checkout
# and run build_static + build:
$ cp sqlite/sqlite3.[ch] pysqlite3/
$ cd pysqlite3
$ python setup.py build_static build
```

## Run the Applications

### FastAPI

Run 

```shell
$ python main.py
```

### Streamlit

Run 

```shell
$ streamlit run app.py
```

and navigate to `http://localhost:8501` in your browser.

## References

* https://wikidocs.net/233805