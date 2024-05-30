from aljazeera_news import AlJazeeraNewsScraper
from config import SEARCH_TEXT, NO_OF_MONTHS
from loggers import logger


def run_task():
    """
        Run the process to scrape news data, create an Excel file.
    """
    try:
        scraper = AlJazeeraNewsScraper(search_text=SEARCH_TEXT, no_of_months=NO_OF_MONTHS)
        scraper.open_browser()
        scraper.open_and_search_input_text()
        scraper.load_and_sort_news_data()
        scraper.scrap_news_data()
        scraper.create_excel_file_for_news_data()
        logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"Failed to run the process: {str(e)}")


if __name__ == "__main__":
    run_task()
