# core/displays.py
from abc import ABC, abstractmethod
import logging

from colorama import Style

from core import settings
from core.board import Board
from core.players import Player

logger = logging.getLogger(__name__)

class Display(ABC):
    @abstractmethod
    def display_board(self, board: Board):
        pass

    @abstractmethod
    def show_prompt(self, msg: str) -> None:
        """
        Сообщение о ходе игры
        """
        pass

    @abstractmethod
    def show_score(self, players: list[Player]):
        pass


class ConsoleDisplay(Display):
    def display_board(self, board: Board) -> None:
        output_board = []

        for row in range(board.get_size_buffered()):
            row_cells = []
            for col in range(board.get_size_buffered()):
                element = board.get_cell_buffered(row, col).value.to_string()
                row_cells.append(element)

            output_board.append(' | '.join(row_cells))
        output_board = '\n'.join(output_board)

        print(output_board)
        logger.debug(f'Отрисовано поле в коносль:\n{output_board}\n')

    def show_prompt(self, msg: str) -> None:
        print(msg)
        logger.debug(f'Выведено сообщение в консоль: {msg}')

    def show_score(self, players: list[Player]):
        result_table = {player.name:player.get_points() for player in players}
        str_output = '\n'.join(map(lambda x: f'{x[0]}: {x[1]}', result_table.items()))
        print(
            f'{Style.BRIGHT}Текущий счет:\n'
            f'{str_output}{Style.RESET_ALL}\n'
        )

    def show_start(self):
        print(
            f"Добро пожаловать в игру {Style.BRIGHT}{settings.GAME_NAME}{Style.RESET_ALL}!\n"
            f"{''.join(self._get_rules())}\n{'=' * 75}\n")

    def _get_rules(self):
        with open('RULES.md', 'r') as f:
            return f.readlines()
