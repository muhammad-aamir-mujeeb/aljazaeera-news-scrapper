from collections import defaultdict
from datetime import datetime

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from SeleniumLibrary.errors import SeleniumLibraryException
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By

from aljazeera_news.locators import NewsLocators
from aljazeera_news.utils import parse_news_data, check_amount, parse_date_from_string, \
    zip_and_remove_images_directory, check_articles_within_date_range
from config import DOWNLOAD_DIRECTORY
from loggers import logger


class AlJazeeraNewsScraper:
    def __init__(self, search_text: str, no_of_months: int):
        """
        Initialize the Al Jazeera News Scraper.
        """
        self.browser = Selenium()
        self.http = HTTP()
        self.excel = Files()
        self.news_data = set()
        self.search_text = search_text
        self.no_of_months = no_of_months
        self.site_url = 'https://www.aljazeera.com'
        self.threshold_date = (datetime.today() + relativedelta(months=1 - max(no_of_months, 1))).replace(day=1)

    def open_browser(self):
        """Open browser to scrape data.

        This method opens a browser to scrape data from the specified site URL.
        It sets the download directory and opens the browser in maximized mode.

        """
        logger.info(f"Opening browser to scrape data from: {self.site_url}")
        self.browser.set_download_directory(DOWNLOAD_DIRECTORY)
        self.browser.open_available_browser(self.site_url, maximized=True)
        logger.info("Browser opened successfully.")

    def open_and_search_input_text(self):
        """Open search input field and perform a search.

        This method opens the search input field on the website, inputs the search text,
        and performs a search.

        """
        try:
            logger.info("Opening search input field.")
            self.browser.element_should_be_visible(
                locator=NewsLocators.search_button,
                message="Click here to search"
            )
            self.browser.click_button(locator=NewsLocators.search_trigger)
            self.browser.input_text(locator=NewsLocators.search_input, text=self.search_text, clear=True)
            logger.info(f"Search text '{self.search_text}' entered.")
            self.browser.element_should_be_visible(
                locator=NewsLocators.search_button_after_input,
                message="Search"
            )
            self.browser.click_button(locator="class:css-sp7gd")
            logger.info("Search performed.")
        except AssertionError as e:
            logger.error(f'Failed to open and search input field: {e}')
            self.browser.close_browser()

    def load_and_sort_news_data(self):
        """
            Load and sort news data based on the search query.

            This method uses a browser instance to load news data, check for search results,
            sort the articles by date, and log the process. If no results are found or if
            an error occurs, the browser is closed.
        """
        try:
            self.browser.wait_until_page_contains_element(locator=NewsLocators.is_results_available, timeout=20)
            if not self.browser.is_element_visible(locator=NewsLocators.is_results_available):
                logger.info(f"No results found for search query: '{self.search_text}'")
                self.browser.close_browser()
                return

            self.browser.click_element_when_visible(locator=NewsLocators.sort_articles)
            logger.info(f"Clicked on the 'Sort' button to sort articles by date.")

            logger.info(f"Found results for search query: '{self.search_text}'")
        except (AssertionError, SeleniumLibraryException) as e:
            logger.error("There is a problem with scraping data: %s", str(e))
            self.browser.close_browser()
            return

        self.click_show_more_button()
        logger.info("All news articles loaded.")

    def scrap_news_data(self):
        """
        Scrap news data from search results.

        Scrapes news data including title, description, date, and image from search results.
        """

        logger.info("Starting to scrap news data.")
        self.browser.wait_until_page_contains_element(NewsLocators.search_result)
        news_results = self.browser.find_elements(NewsLocators.search_result)

        for idx, element in enumerate(news_results):
            img_ele = element.find_element(By.TAG_NAME, 'img')

            title = parse_news_data(element.find_element(By.TAG_NAME, 'h3').text)
            description = parse_news_data(element.find_elements(By.TAG_NAME, 'p')[0].text)
            target_file = f'{DOWNLOAD_DIRECTORY}/images/news-article-{idx + 1}.jpg'
            article_date = parse_date_from_string(description)

            if not check_articles_within_date_range(article_date, self.threshold_date):
                logger.info("Article date is not within the specified date range. Skipping further scraping.")
                break

            news_item = {
                'title': title,
                'description': description,
                'date': article_date,
                'picture': target_file,
                'search_text_in_title': title.count(self.search_text),
                'search_text_in_description': description.count(self.search_text),
                'is_contains_amount': str(any([check_amount(title) or check_amount(description)]))
            }

            try:
                image_src = img_ele.get_attribute('src')
                self.http.download(image_src, target_file=target_file)
            except FileNotFoundError as e:
                logger.warning(f"Failed to download image: {str(e)}")

            self.news_data.add(tuple(news_item.items()))
            logger.info(f"Scraped news data {idx + 1}: {news_item}")
        logger.info("Scraping of news data completed.")

    def click_show_more_button(self):
        """
            Click the 'Show More' button repeatedly until it's no longer visible.

            This function scrolls to the bottom of the page and clicks the 'Show More' button to load more news articles.
            It repeats this process until the 'Show More' button is no longer visible on the page.

            Raises:
                Exception: If there's any error during the process.
        """
        try:
            self.browser.wait_until_page_contains_element(locator=NewsLocators.show_more)
            self.browser.execute_javascript(NewsLocators.scroll_page)
            self.browser.click_element(locator=NewsLocators.show_more)
            self.click_show_more_button()
        except (AssertionError, SeleniumLibraryException):
            logger.info("No more articles to load.")

    def create_excel_file_for_news_data(self):
        """
        Write news data into an Excel file.

        If there is no news data, it logs a warning and returns.
        """

        if not self.news_data:
            logger.warning("No data to write into Excel file.")
            self.browser.close_browser()

        sorted_data = sorted(self.news_data, key=lambda x: x[2], reverse=True)

        table_data = defaultdict(list)

        for data_tuple in sorted_data:
            for key, value in data_tuple:
                table_data[key].append(value)
        file_path = f"{DOWNLOAD_DIRECTORY}/results.xlsx"
        sheet = self.excel.create_workbook(file_path, fmt='xlsx')

        sheet.append_worksheet('Sheet', table_data, header=True, start=1)
        sheet.save()

        logger.info(f"News data saved into Excel file: {file_path}")
        zip_and_remove_images_directory()
