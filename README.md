# Al Jazeera News Scrapper
This is a Python [RPA](https://rpaframework.org/) bot to scrap news data from the Al Jazeera website, clean the data, store it into an Excel sheet, and download associated images.

## Installation

1. Clone this repository:
   - [Al Jazeera News](https://github.com/muhammad-aamir-mujeeb/aljazaeera-news-scrapper)
2. Navigate to the project directory:
    - cd aljazeera-news-scrapper
3. Install the required dependencies:
    - `pip install -r requirements.txt`

## Configuration
You can customize the behavior of the scrapper by modifying the `config.py` file.

```dotenv
SEARCH_TEXT='<Search text that you want to search>'
NO_OF_MONTHS=6
```

By default `NO_OF_MONTHS` are set to `6` and integer value that will scrap data between 6 months. You can change these `NO_OF_MONTHS` by providing value between 1 and 12.


## Usage
Run the `task.py` script to start scrapping the Al Jazeera website.
 - `python task.py`

This will scrap the latest news articles from Al Jazeera, clean the data, and store it into an Excel sheet named `results.xlsx` in the `output` directory. It will also download associated images and save them in the same directory.