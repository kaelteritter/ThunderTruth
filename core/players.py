# core/players.py
from abc import ABC, abstractmethod
import logging
import secrets
import string
from typing import Any

from core.exceptions import InvalidNameTypeError, TokenInvalidError
from core.tokens import Token

logger = logging.getLogger(__name__)


class Player(ABC):
    """
    Абстрактный класс для игрока
    Хранит информацию об игроке и управляет своим набором токенов-операторов.
    """
    def __init__(self, name: str | None = None) -> None:
        self._tokens: set = set()
        self._name: str | None = name
        self._id = None

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
    
    @abstractmethod
    def make_id(self):
        """
        Сгенерировать уникальный id.
        """
        pass

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
        if not isinstance(tokens, set) or not all(isinstance(token, Token) for token in tokens):
            logger.warning(f"Попытка установить неверный тип токенов: {type(tokens)}:{tokens}")
            raise TokenInvalidError(
                'Коллекция токенов должна быть set. Все токены должны быть подклассом Token.'
                )   
    
    def set_tokens(self, tokens: set[Token]) -> bool:
        """
        Назначить набор токенов
        """
        self._validate_tokens_set(tokens)
        self._tokens = tokens
        logger.debug(
            f"Игроку {self.name}:{self.get_id()} присвоен набор "
            f"токенов: {', '.join(token.to_string() for token in tokens)}"
            )
        return True

    @abstractmethod
    def add_token(self, token: Token) -> bool:
        """
        Добавить токен в свой набор для раунда
        """
        pass

    @abstractmethod
    def pop_token(self, token: Token) -> Token:
        """
        Удалить токен из своего набора
        """
        pass


class HumanPlayer(Player):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.prefix = 'human'
        self.make_id()
        
        logger.debug(f"Игрок с именем {self.name} успешно создан (id_{self.get_id()})")

    def add_token(self, token: Token) -> bool:
        self.tokens.add(token)
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
        logger.debug(
            f"Игрок {self.name}:id_{self.get_id()}"
            f"пытается использовать токен {token.to_string()} (token_id_{token.get_id()}) "
        )
        return token

    def make_id(self):
        if not self.get_id():
            self._id = self._generate_id(self.prefix)

class AIPlayer(Player):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.prefix = 'ai'
        self.make_id()
        
        logger.debug(f"Игрок с именем {self.name} успешно создан (id_{self.get_id()})")

    def add_token(self, token: Token) -> bool:
        self.tokens.add(token)
        return True

    def pop_token(self, token: Token) -> Token:
        return token

    def make_id(self):
        if not self.get_id():
            self._id = self._generate_id(self.prefix)