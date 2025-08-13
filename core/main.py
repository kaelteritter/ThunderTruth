# core/main.py
import logging
from logging.handlers import RotatingFileHandler

from core.board import Board
from core.rules import ThunderTruthRules
from core.handlers import ConsoleInputHandler
from core.displays import ConsoleDisplay
from core.game import Game
from core import settings


def setup_logging():
    """
    Настраивает логирование в зависимости от режима (DEBUG или PRODUCTION)
    """
    logger = logging.getLogger()
    logger.setLevel(settings.LOGGING_LEVEL)
    log_format = logging.Formatter(settings.LOGGING_FORMAT, datefmt=settings.LOGGING_DATEFMT)
    
    # Очищаем существующие хендлеры, чтобы избежать дублирования
    logger.handlers.clear()
    
    if settings.PRODUCTION:
        # В боевом режиме логи только в файл
        file_handler = RotatingFileHandler(
            'game.log',
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=3  # Хранить до 3 архивных логов
        )
        file_handler.setLevel(settings.LOGGING_LEVEL)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    else:
        # В режиме разработки логи в консоль
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(settings.LOGGING_LEVEL)
        stream_handler.setFormatter(log_format)
        logger.addHandler(stream_handler)
    
    logging.info("Инициализация логирования завершена")

def main():
    """
    Точка входа для игры
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Запуск игры")

    board = Board(settings.BOARD_SIZE)
    rules = ThunderTruthRules()
    input_handler = ConsoleInputHandler()
    display = ConsoleDisplay()
    game = Game(board, rules, input_handler, display)

    # Запуск игрового цикла
    try:
        game.play(debug=settings.DEBUG)
    except KeyboardInterrupt:
        logger.error("Игра прервана пользователем")
        display.show_prompt("Игра прервана!")
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        display.show_prompt(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main()