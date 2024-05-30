import os

from RPA.Robocorp.WorkItems import WorkItems

from loggers import logger

DOWNLOAD_DIRECTORY = f'{os.getcwd()}/output'
if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)
    os.makedirs(f'{DOWNLOAD_DIRECTORY}/images')

ENVIRONMENT = os.getenv('environment', default=None)
SEARCH_TEXT = 'Pakistan china economic corridor and benefits for both countries'
NO_OF_MONTHS = 6

if ENVIRONMENT == 'PROD':
    logger.info('Starting production environment')
    work_item = WorkItems()
    work_item.get_input_work_item()
    env_variables = work_item.get_work_item_payload()
    SEARCH_TEXT = env_variables.get('search_text')
    NO_OF_MONTHS = env_variables.get('no_of_months')
    logger.info('Connected to production environment')
