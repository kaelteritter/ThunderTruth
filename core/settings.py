# core/settings.py
import logging
import os

from dotenv import load_dotenv

load_dotenv()

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

MULTIPLAYER = False

BOARD_SIZE = int(os.getenv('BOARD_SIZE', 3))
INITIAL_TOKENS = int(os.getenv('INITIAL_TOKENS', 4))

PLAYERS_AMOUNT = int(os.getenv('PLAYERS_AMOUNT', 2))

AI_OPPONENT_DEFAULT = os.getenv('AI_OPPONENT_DEFAULT', 'Зевс')