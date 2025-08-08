import logging
from typing import Any
from core.board import Board
from core.displays import Display
from core.exceptions import PlayerInvalidError
from core.handlers import InputHandler
from core.players import Player
from core.rules import Rules

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
    
    def _validate_player_type(self, player: Any):
        if not isinstance(player, Player):
            logger.warning(f'Передан неверный тип игрока: {type(player)}')
            raise PlayerInvalidError("Игрок должен быть типа Player")
        
    def _validate_unique_players(self, player: Player):
        if player in self.players:
            logger.warning(f'Попытка добавить уже присоединившегося игрока {player.get_id()}')
            raise PlayerInvalidError(f"Игрок {player.get_id()} уже добавлен в игру")
    
    def add_player(self, player: Player) -> None:
        """
        Добавляет игрока в игру
        """
        self._validate_player_type(player)
        self._validate_unique_players(player)
        self.players.append(player)
        logger.info(f'Добавлен новый игрок {player.get_id()} с именем {player.name}')

    def setup(self):
        """
        Запрашивает выбор токенов у игроков и инициализирует доску
        """
        pass
    

    def play(self):
        # Показать приветствие
        # Инициализировать доску и запросить выбор токенов

        # Делать ход, давать промпты, сверяться с правилами

        # Закончить игровой цикл, показать итог, предложить сыграть снова
        pass