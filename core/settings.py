# core/settings.py
import logging
import os


# Разработка
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'


# Логгирование
if DEBUG:
    LOGGING_LEVEL = logging.DEBUG
else:
    LOGGING_LEVEL = logging.WARNING

LOGGING_FORMAT = '%(levelname)s - %(asctime)s - %(name)s - %(message)s'
LOGGING_DATEFMT = '%Y-%m-%d %H:%M:%S'



# Игровые настройки
GAME_NAME = 'ThunderTruth'

BOARD_SIZE = int(os.getenv('BOARD_SIZE', 5))
INITIAL_TOKENS = int(os.getenv('INITIAL_TOKENS', 4))

PLAYERS_AMOUNT = int(os.getenv('PLAYERS_AMOUNT', 2))