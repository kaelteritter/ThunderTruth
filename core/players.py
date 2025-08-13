# core/players.py
from abc import ABC, abstractmethod
import logging
import random
import secrets
import string
from typing import Any

from core import settings
from core.board import Board
from core.exceptions import InvalidNameTypeError, TokenInvalidError
from core.tokens import AND, IMP, OR, XOR, Token

logger = logging.getLogger(__name__)


class Player(ABC):
    """
    Абстрактный класс для игрока
    Хранит информацию об игроке и управляет своим набором токенов-операторов.
    """
    def __init__(self, name: str | None = None) -> None:
        self._tokens: list = []
        self._id = None
        self._name: str | None = name
        self._points = 0

    def get_id(self) -> str | None:
        """
        Уникальный идентификатор.
        Используется в логах.
        """
        return self._id
    
    @staticmethod
    def _generate_id(prefix='', length=10) -> str:
        """
        Возвращает случайный id с префиксом
        По умолчанию случайный набор из букв и цифр длиной 10
        """
        characters = string.ascii_letters + string.digits
        suffix = ''.join(secrets.choice(characters) for _ in range(length))
        return prefix + '_' + suffix

    @property
    def name(self):
        return self._name

    @property
    def tokens(self):
        return self._tokens
    
    def _validate_name(self, name):
        if not isinstance(name, str):
            logger.warning(f"Попытка присвоить игроку id_{self.get_id()} некорректно имя: {self.name}")
            raise InvalidNameTypeError('Имя должен быть строкой')

    def set_name(self, name) -> bool:
        """
        Присвоить игроку имя
        """
        self._validate_name(name)
        self._name = name
        logger.debug(f"Игроку id_{self.get_id()} назначено новое имя: {self.name}")
        return True
    
    def _validate_tokens_set(self, tokens: Any):
        if not isinstance(tokens, list) or not all(isinstance(token, Token) for token in tokens):
            logger.warning(f"Попытка установить неверный тип токенов: {type(tokens)}:{tokens}")
            raise TokenInvalidError(
                'Коллекция токенов должна быть list. Все токены должны быть подклассом Token.'
                )   
    
    def set_tokens(self, tokens: list[Token]) -> bool:
        """
        Назначить набор токенов
        """
        self._validate_tokens_set(tokens)

        for token in self.tokens:
            token.remove_owner()

        self._tokens = []

        for token in tokens:
            self.add_token(token)
            
        logger.debug(
            f"Игроку {self.name}:{self.get_id()} присвоен набор "
            f"токенов: {', '.join(token.to_string() for token in tokens)}"
            )
        return True

    def add_token(self, token: Token) -> bool:
        self.tokens.append(token)
        if token.get_owner() is not self:
            token.set_owner(self)
        logger.debug(
            f"Игрок {self.name}:id_{self.get_id()} получил "
            f"токен {token.to_string()} (token_id_{token.get_id()}"
            )
        return True

    def _validate_pop_token(self, token):
        if not isinstance(token, Token):
            logger.warning(f'Попытка извлечь из набора игрока неверный тип токена: {token}')
            raise TokenInvalidError('Токен должен быть подклассом Token')
        
        if not token in self.tokens:
            logger.warning(
                f"Токен {token.to_string()} (token_id_{token.get_id()}) "
                f"не найден у игрока id_{self.get_id()}"
            )
            raise TokenInvalidError('Нельзя удалить токен у игрока, который ему не принадлежит')

    def pop_token(self, token: Token) -> Token:
        self._validate_pop_token(token)
        self.tokens.remove(token)
        if token.get_owner():
            token.remove_owner()
        logger.debug(
            f"Игрок {self.name}:id_{self.get_id()}"
            f"пытается использовать токен {token.to_string()} (token_id_{token.get_id()}) "
        )
        return token

    def add_points(self, points: int) -> None:
        self._points += points
        if self._points < 0:
            self._points = 0
        logger.debug(
            f'Игроку {self.get_id()} добавлено {points} очков.'
            f'Текущие очки {self.get_id()}: {self.get_points()}'
            )
        
    def make_id(self):
        if not self.get_id():
            self._id = self._generate_id(self.prefix)

    def get_points(self) -> int:
        return self._points
    
    def reset_points(self) -> None:
        self._points = 0
        logger.debug(f'Игрок {self.get_id()}: очки сброшены')

    def get_color(self):
        return getattr(self, 'color')


class HumanPlayer(Player):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.prefix = 'human'
        self.make_id()
        self._name = name or f'AnonymousPlayer_{self.get_id()}'
        
        logger.debug(f"Игрок с именем {self.name} успешно создан (id_{self.get_id()})")
    

class AIPlayer(Player):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.prefix = 'ai'
        self.make_id()
        self._name = name or f'{settings.AI_OPPONENT_DEFAULT}'
        
        logger.debug(f"Игрок с именем {self.name} успешно создан (id_{self.get_id()})")

    def _choose_token_random(self):
        if self.tokens:
            return random.randint(1, len(self.tokens))
        return None
    
    def think(self, board: Board) -> tuple[int, int, int]:
        token_idx = self._choose_token_random()

        empty_cells = []
        for row in range(1, board.get_size() + 1):
            for col in range(1, board.get_size() + 1):
                if board.get_cell(row, col).is_empty:
                    empty_cells.append((row, col))

        row, col = random.choice(empty_cells)
        logger.debug(f'AI {self.name}:{self.get_id()} выбрал {row, col} из пустых клеток: {empty_cells}')
        logger.warning(f'ВЫБРАНО РАНДОМОМ: Токен: {token_idx}, Координата: {row, col}')
        return token_idx - 1, row, col


    