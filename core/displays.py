# core/displays.py
from abc import ABC, abstractmethod
import logging

from colorama import Fore, Style

from core import settings, utils
from core.board import Board
from core.elements import Stub
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

    @abstractmethod
    def show_now_turn(self, player: Player) -> None:
        pass

    @abstractmethod
    def show_token_available(self, player: Player) -> None:
        pass

    @abstractmethod
    def show_next_move_notification(self) -> None:
        pass

    @abstractmethod
    def show_winner(self, winner: Player | None) -> None:
        pass


class ConsoleShowMixin:
    def _substitute_to_string(self, element, row, col):
        if isinstance(element, Stub):
            if col == row == 0:
                return element.to_string()
            if col == 0:
                return self.boldify(self.colorize(row, Fore.LIGHTMAGENTA_EX))
            if row == 0:
                return self.boldify(self.colorize(col, Fore.LIGHTMAGENTA_EX))
            return self.boldify(element.to_string())
        return element.to_string()
    
    def boldify(self, string: str):
        return f'{Style.BRIGHT}{string}{Style.RESET_ALL}'
    
    def colorize(self, string: str, color):
        return f'{color}{string}{Style.RESET_ALL}'


class ConsoleDisplay(Display, ConsoleShowMixin):
    def display_board(self, board: Board) -> None:
        output_board = []

        for row in range(board.get_size_buffered()):
            row_cells = []
            for col in range(board.get_size_buffered()):
                element = board.get_cell_buffered(row, col).value
                row_cells.append(self._substitute_to_string(element, row, col))

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
        rules = utils.get_path_compiling('RULES.md')
        with open(rules, 'r', encoding='utf-8') as f:
            return f.readlines()
        
    def show_now_turn(self, player: Player):
        print(f"Ход игрока {player.get_color()}{Style.BRIGHT}{player.name}{Style.RESET_ALL}")
        
    def show_token_available(self, player: Player) -> None:
        print(f'Ваши токены: [{", ".join(token.to_string() for token in player.tokens)}]')

    def show_next_move_notification(self) -> None:
        print(f'{Style.DIM}Следующий ход...{Style.RESET_ALL}')

    def show_winner(self, winner: Player | None) -> None:
        if winner:
            print(
                f'{Style.BRIGHT}Победитель: {winner.get_color()}{winner.name}{Style.RESET_ALL}. '
                f'Набрано: {Style.BRIGHT}{winner.get_points()}{Style.RESET_ALL} очков\n'
            )
        else:
            print(f"{Style.BRIGHT}Ничья{Style.RESET_ALL}")
