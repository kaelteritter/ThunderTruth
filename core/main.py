# core/main.py
import logging
from core.board import Board
from core.rules import ThunderTruthRules
from core.handlers import ConsoleInputHandler
from core.displays import ConsoleDisplay
from core.game import Game
from core import settings

def setup_logging():
    """
    Настраивает логирование для отладки
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def main():
    """
    Точка входа для игры
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Запуск игры")

    # Инициализация компонентов
    board = Board(size=5)  # Доска 5x5
    rules = ThunderTruthRules()
    input_handler = ConsoleInputHandler()
    display = ConsoleDisplay()
    game = Game(board, rules, input_handler, display)

    # Запуск игрового цикла
    try:
        game.play(debug=True)
    except KeyboardInterrupt:
        logger.error("Игра прервана пользователем")
        display.show_prompt("Игра прервана!")
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        display.show_prompt(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main()