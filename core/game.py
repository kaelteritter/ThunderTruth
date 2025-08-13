# core/game.py

import logging
import random
from typing import Any

from colorama import Fore, Style
from core import settings
from core.board import Board
from core.displays import Display
from core.exceptions import (
    CellOccupiedError, CellOutOfBorderError, 
    PlayerInvalidError, RulesOwnershipError
)
from core.handlers import InputHandler
from core.players import AIPlayer, HumanPlayer, Player
from core.rules import Rules
from core.tokens import AND, IMP, OR, XOR, Token

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
        self.play_again = False
        

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

    def _add_human_player(self) -> None:
        player_name = self.input_handler.get_name()
        new_player = HumanPlayer(name=player_name)
        setattr(new_player, 'color', Fore.CYAN)
        self.add_player(new_player)

    def _add_ai_player(self) -> None:
        ai_player = AIPlayer()
        setattr(ai_player, 'color', Fore.RED)
        self.add_player(ai_player)

    def _get_tokens_random(self) -> list[AND | XOR | IMP | OR]:
        tokens = [random.choice([AND(), XOR(), IMP(), OR()]) for _ in range(settings.INITIAL_TOKENS)]
        return tokens

    def setup(self, multiplayer: bool = settings.MULTIPLAYER) -> None:
        """
        Запрашивает выбор токенов у игроков и инициализирует доску
        """
        if multiplayer:
            i = 1
            while len(self.players) < settings.PLAYERS_AMOUNT:
                self.display.show_prompt(f'Игрок {i}')
                self._add_human_player()
                i += 1
        else:
            self.display.show_prompt(f'Игрок №1')
            if not self.players: 
                self._add_human_player()
                self._add_ai_player()

        self.board.setup()
        for player in self.players:
            self.display.show_prompt(f'Выбор токенов для игрока: {player.name}\n')
            if isinstance(player, HumanPlayer):
                tokens = self.input_handler.get_tokens()
            elif isinstance(player, AIPlayer):
                tokens = self._get_tokens_random()
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
        self.display.show_prompt(f"Ход игрока {player.get_color()}{Style.BRIGHT}{player.name}{Style.RESET_ALL}")
        self.display.display_board(self.board)
        tokens_str = ", ".join(token.to_string() for token in player.tokens)
        self.display.show_prompt(f"Ваши токены: [{tokens_str}]")
        
    def _get_info(self, player: Player) -> tuple[Token, int, int]:
        if isinstance(player, HumanPlayer):
            token_idx, row, col = self.input_handler.get_move(player)
        else:
            token_idx, row, col = player.think(self.board)
        token = player.tokens[token_idx]
        return token, row, col
    
    def end_turn(self, player: Player, token: Token):
        player.pop_token(token)
        self.display.show_score(self.players)
        self.display.show_prompt(f'{Style.DIM}Следующий ход...{Style.RESET_ALL}')
        self.switch_player()

    def end_round(self, debug) -> bool:
        self.display.display_board(self.board)
        winner = self.rules.check_winner(self.board, *self.players)
        
        if winner:
            self.display.show_prompt(f"{Style.BRIGHT}Победитель: {winner.get_color()}{winner.name}.{Style.RESET_ALL} Набрано: {Style.BRIGHT}{winner.get_points()}{Style.RESET_ALL} очков\n")
        else:
            self.display.show_prompt(f"{Style.BRIGHT}Ничья{Style.RESET_ALL}")
        
        if not debug:
            for player in self.players:
                player.reset_points()
        self.display.show_prompt(f"Конец игры!")

        if isinstance(self.get_current_player(), AIPlayer):
            self.switch_player()

        newRound = self.input_handler.ask_play_again()

        logger.debug(f"Играть снова? {newRound}")
        return newRound

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

    def start_round(self):
        if self.play_again:
            self._board = Board()
        self.setup()

    def play(self, debug=False):
        self.display.show_start()
        if not self.input_handler.ask_go_ahead():
            self.display.show_prompt('До встречи!')
            return
        
        while True:
            self.start_round()
            
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

            self.play_again = self.end_round(debug)
            if not self.play_again:
                self.display.show_prompt('Игра завершена!')
                return

