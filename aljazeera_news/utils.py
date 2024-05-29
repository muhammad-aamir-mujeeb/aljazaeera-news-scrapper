import os
import re
import shutil
import zipfile
from datetime import datetime, timedelta, date

from dateutil.parser import parse, ParserError
from dateutil.relativedelta import relativedelta

from config import DOWNLOAD_DIRECTORY
from loggers import logger


def parse_news_data(news_data: str):
    """
    Parse news data by removing "X days ago" and leading/trailing ellipses.

    Args:
        news_data (str): The news data to parse.

    Returns:
        str: The parsed news data.
    """
    try:
        re_pattern = r'\\x[0-9a-fA-F]{2}'
        cleaned_string = ''.join(char for char in news_data if ord(char) < 128)
        cleaned_string = re.sub(re_pattern, '', cleaned_string)
        return cleaned_string.replace('...', '').strip()
    except Exception as e:
        logger.error(f"Failed to parse news data: {str(e)}")
        return news_data.replace('...', '').strip()


def parse_date_from_string(date_str: str):
    """
    Parse date from a string.

    Args:
        date_str (str): The string to parse.

    Returns:
        datetime: The parsed date.
    """
    try:
        formated_date = date.today()
        days_re_pattern = r'(\d+)\s+days?\s+ago'
        days_match = re.search(days_re_pattern, date_str)
        if days_match:
            days = int(days_match.group(1))
            formated_date = (datetime.now() - timedelta(days=days)).date()
            logger.info(f"Found date {formated_date} from 'days ago' format in string: {date_str}")

        hours_re_pattern = r'(\d+)\s+hours?\s+ago'
        hours_match = re.search(hours_re_pattern, date_str)
        if hours_match:
            hours_str = hours_match.group(1)
            formated_date = parse(f'{hours_str} hour').date()
            logger.info(f"Found date {formated_date} from 'hours ago' format in string: {date_str}")

        date_re_pattern = r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})'
        date_match = re.search(date_re_pattern, date_str)
        if date_match:
            date_str = date_match.group(1)
            try:
                formated_date = parse(date_str).date()
                logger.info(f"Found date {formated_date} from 'Month Day, Year' format in string: {date_str}")
            except ValueError:
                pass
        return formated_date

    except (ParserError, Exception) as e:
        logger.error(f"Failed to parse date: {str(e)}")


def check_articles_within_date_range(article_date, threshold_date, date_range):
    """
    Check if articles' dates fall within the specified date range.

    Args:
        article_date (datetime): The date to check.
        date_range (int, optional): Number of months before the current date. Defaults to 6.
        threshold_date (datetime): The minimum date to check for article existence.

    Returns:
        bool: True if articles' dates fall within the date range, False otherwise.
    """
    date_range = max(date_range, 1)
    threshold_date = (threshold_date + relativedelta(months=12 - date_range)).replace(day=1)
    return article_date >= threshold_date.date()


def check_amount(text: str):
    """
    Check if the text contains an amount.

    Args:
        text (str): The text to check.

    Returns:
        MatchObject or None: A match object if an amount is found, otherwise None.
    """
    try:
        amount_re_pattern = r'\$[\d,]+(?:\.\d+)?|\b\d+\s*dollars?\b|\b\d+\s*USD\b'
        match = re.findall(amount_re_pattern, text)
        return match
    except Exception as e:
        logger.error(f"Failed to check amount in text: {str(e)}")
        return None


def zip_and_remove_images_directory():
    """
    Compresses a directory into a zip file and removes the directory.
    """
    images_dir = f"{DOWNLOAD_DIRECTORY}/images"
    zip_dir = f"{DOWNLOAD_DIRECTORY}/archive_images"
    logger.info(f"Zipping {images_dir} to {zip_dir}")
    with zipfile.ZipFile(zip_dir, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(images_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), images_dir))
    logger.info(f"Zip file {zip_dir} created successfully.")

    try:
        shutil.rmtree(images_dir)
        logger.info(f"Directory {images_dir} removed successfully.")
    except Exception as e:
        logger.error(f"Error removing directory {images_dir}: {str(e)}")
