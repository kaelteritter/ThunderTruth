# core/game.py

import logging
from typing import Any
from core import settings
from core.board import Board
from core.displays import Display
from core.exceptions import (
    CellOccupiedError, CellOutOfBorderError, 
    PlayerInvalidError, RulesOwnershipError
)
from core.handlers import InputHandler
from core.players import HumanPlayer, Player
from core.rules import Rules
from core.tokens import Token

logger = logging.getLogger(__name__)

class Game:
    def __init__(
            self,
            board: Board,
            rules: Rules,
            input_handler: InputHandler,
            display: Display,
            ) -> None:
        self._board = board
        self._rules = rules
        self._input_handler = input_handler
        self._display = display
        self._players = []
        self._current_player_index = 0
        

    @property
    def board(self):
        return self._board
    
    @property
    def rules(self):
        return self._rules
    
    @property
    def input_handler(self):
        return self._input_handler
    
    @property
    def display(self):
        return self._display
    
    @property
    def players(self):
        return self._players
    
    def get_current_player(self):
        return self.players[self._current_player_index]
    
    def switch_player(self):
        """
        Передает ход следующему игроку в списке
        """
        self._current_player_index = (self._current_player_index + 1) % len(self.players)
        logger.debug(f'Переход хода на игрока {self.players[self._current_player_index].get_id()}')
    
    def _validate_player_type(self, player: Any):
        if not isinstance(player, Player):
            logger.warning(f'Передан неверный тип игрока: {type(player)}')
            raise PlayerInvalidError("Игрок должен быть типа Player")
        
    def _validate_unique_players(self, player: Player):
        if player in self.players:
            logger.warning(f'Попытка добавить уже присоединившегося игрока {player.get_id()}')
            raise PlayerInvalidError(f"Игрок {player.get_id()} уже добавлен в игру")
    
    def _validate_players_amount(self):
        limit = settings.PLAYERS_AMOUNT
        if len(self.players) >= limit:
            logger.warning(f'Попытка добавить игрока сверх лимита')
            raise PlayerInvalidError(f"Игроков не может быть больше {limit}")
    
    def add_player(self, player: Player) -> None:
        """
        Добавляет игрока в игру
        """
        self._validate_players_amount()
        self._validate_player_type(player)
        self._validate_unique_players(player)
        self.players.append(player)
        logger.info(f'Добавлен новый игрок {player.get_id()} с именем {player.name}')

    def setup(self) -> None:
        """
        Запрашивает выбор токенов у игроков и инициализирует доску
        """
        i = 1
        while len(self.players) < settings.PLAYERS_AMOUNT:
            self.display.show_prompt(f'Игрок {i}')
            player_name = self.input_handler.get_name()
            new_player = HumanPlayer(name=player_name)
            self.add_player(new_player)
            i += 1

        self.board.setup()
        for player in self.players:
            self.display.show_prompt(f'Выбор токенов для игрока: {player.name}')
            tokens = self.input_handler.get_tokens()
            player.set_tokens(tokens)
        logger.info('Игра инициализирована!')

    def move(self, player: Player, token: Token, row: int, col: int):
        # Токен - в наборе текущего игрока?
        # Логгирование DEBUG также идет в классе обработчика
        if not self.rules.is_token_owner(player, token):
            logger.warning(f'Игрок {player.get_id()} пытается сделать ход не своим токеном {token.get_id()}')
            raise RulesOwnershipError(f'Токен должен принадлежать игроку')
        
        # Проверка на тип координат, токена, валидность координат и занятость клетки идет внутри доски
        self.board.place_token(token, row, col)

    def impute(self, player: Player, row: int, col: int) -> None:
        """
        Рассчет очков после хода
        """
        points = self.rules.count_points(self.board, row, col)
        player.add_points(points)
        self.display.show_prompt(f'Игрок {player.name} набирает {points} очков')
        logger.debug(f'Игрок {player.get_id()} ({player.name}): +{points} очков')
        logger.debug(f'Очки игрока {player.get_id()} ({player.name}): {player.get_points()}')

        extra_points = self.rules.exclude_points_xor(self.board, row, col)
        
        if extra_points:
            opponent, this_player = extra_points
            opponent.add_points(-1)
            this_player.add_points(1)
            self.display.show_prompt(f'Игрок {this_player.name} набирает дополнительно +1 очко')
            self.display.show_prompt(f'Игрок {opponent.name} лишается 1 очка')

    def _turn_info(self, player: Player):
        self.display.show_prompt(f"Ход игрока {player.name}")
        self.display.display_board(self.board)
        self.display.show_prompt(f"Ваши токены: {[token.to_string() for token in player.tokens]}")
        
    def _get_info(self, player: Player) -> tuple[Token, int, int]:
        token_idx, row, col = self.input_handler.get_move(player)
        token = player.tokens[token_idx]
        return token, row, col
    
    def end_turn(self, player: Player, token: Token):
        player.pop_token(token)
        self.display.show_score(self.players)
        self.display.show_prompt(f'Следующий ход...')
        self.switch_player()

    def end_round(self, debug):
        self.display.display_board(self.board)
        winner = self.rules.check_winner(self.board, *self.players)
        if winner:
            self.display.show_prompt(f"Победитель: {winner.name}. Набрано: {winner.get_points()} очко")
        else:
            self.display.show_prompt(f"Ничья")

        if not debug:
            for player in self.players:
                player.reset_points()
        self.display.show_prompt(f"Конец игры")

    def handle_exception(self, 
                         error: Exception, 
                         player: Player, 
                         row: int | None = None, 
                         col: int | None = None):
        errors_map = {
            CellOccupiedError: {
                'log': f'Попытка поставить токен на занятую клетку: {row, col}',
                'prompt': f"Клетка {row, col} уже занята! Попробуйте снова!"
            },
            CellOutOfBorderError: {
                'log': f'Попытка разместить токен на за пределами игрового поля: {row, col}',
                'prompt': f"Координата {row, col} за пределами игрового поля! Попробуйте снова!"
            }
        }

        for error_type, info in errors_map.items():
            if isinstance(error, error_type):
                logger.warning(info['log'])
                self.display.show_prompt(info['prompt'])
                return

        logger.error(f'Неожиданная ошибка: {str(error)}')
        self.display.show_prompt(f'Ошибка: {str(error)}. Попробуйте снова.')

    def play(self, debug=False):
        self.display.show_prompt(f"Добро пожаловать в игру {settings.GAME_NAME}!")
        self.setup()

        while True:
            player = self.get_current_player()
            self._turn_info(player)

            try:
                token, row, col = self._get_info(player)
                self.move(player, token, row, col)
                self.impute(player, row, col)
            except Exception as error:
                self.handle_exception(error, player, row, col)
                continue

            self.end_turn(player, token)

            if (
                self.rules.is_board_full(self.board) or 
                not self.rules.are_tokens_left(self.players)
            ):
                break

        self.end_round(debug)

