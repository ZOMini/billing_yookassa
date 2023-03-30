import logging
import os
import sys

# Для дебага.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
logging.error('DEBUG --- BASE_DIR --- %s', BASE_DIR)
sys.path.append(f'{BASE_DIR}/functional/')

pytest_plugins = ("functional.fixtures.fixtures_base_io",
                  "functional.fixtures.fixtures_prepare_data")
