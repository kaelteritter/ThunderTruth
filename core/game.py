# core/game.py

import logging
from typing import Any
from core import settings
from core.board import Board
from core.displays import Display
from core.exceptions import PlayerInvalidError, RulesOwnershipError
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
        while len(self.players) < settings.PLAYERS_AMOUNT:
            player_name = self.input_handler.get_player_name()
            new_player = HumanPlayer(name=player_name)
            self.add_player(new_player)

        self.board.setup()
        for player in self.players:
            tokens = self.input_handler.get_player_token_choice()
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
        
        # Изымаем токен из набора игрока
        player.pop_token(token)
    

    def play(self):
        # начало раунда
        self.display.show_prompt(f"Добро пожаловать в игру {settings.GAME_NAME}")
        self.setup()

        while True:
            # до хода: получаем игрока и данные из ввода
            player: Player = self.get_current_player()
            token_idx, row, col = self.input_handler.get_player_move()
            token = player.tokens[token_idx]

            # ход: кладем токен, обрабатывем все исключения, считаем очки
            self.move(player, token, row, col)
            # self.rules.count_points() ...
            # self.rules.exclude_points_xor() ...

            # после хода: меняем игрока, проверяем, что остались пустые клетки
            break

        # конец раунда: считаем очки, показываем итог игры
        self.display.show_prompt(f"Конец игры")