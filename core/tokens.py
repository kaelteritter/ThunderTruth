# core/tokens.py
from abc import abstractmethod
import logging
import secrets
import string
from core.elements import Element
from core.exceptions import InvalidOperandError
from core.operands import Operand
# from core.players import Player


logger = logging.getLogger(__name__)

class Token(Element):
    """
    ОПИСАНИЕ:
    - Токен. Отвечает за хранение информации о себе,
    своем владельце и вычисляет булеово выражение с собой
    в качестве оператора

    ИНТЕРФЕЙС:
    :::Методы:::
    - get_id: уникальный id
    - get_owner: игрок-владелец токена
    - set_owner: устанавливает игрока-владельца после инициализации
    - remove_owner: удаляет игрока-владельца
    - get_truth_table: таблица истинности
    - evaluate: вычислить булеово выражение вида: op1 [self] op2
    - to_string: строковое представление
    """
    def __init__(self, owner=None) -> None:
        self._owner = owner
        self._last_owner = owner
        self._id = None
        self._prefix = 'token'

    @staticmethod
    def _generate_id(prefix='', length=10) -> str:
        """
        Возвращает случайный id с префиксом
        По умолчанию случайный набор из букв и цифр длиной 10
        """
        characters = string.ascii_letters + string.digits
        suffix = ''.join(secrets.choice(characters) for _ in range(length))
        return '_'.join(['token', prefix, suffix])

    def get_id(self):
        return self._id

    def is_immutable(self) -> bool:
        return False
    
    def _validate_operand(self, value1, value2):
        if not isinstance(value1, Operand) or not isinstance(value2, Operand):
            logger.warning(f"Попытка передать в evaluate() значения не Operand: {value1, value2}")
            raise InvalidOperandError('Операнды могут быть только подклассами Operand')
        
    def get_owner(self):
        return self._owner
    
    def get_last_owner(self):
        return self._last_owner
    
    def set_owner(self, player):
        """
        Назначает владельца токена
        """
        self._owner = player
        if self._last_owner is None:
            self._last_owner = player
        if self not in player.tokens:
            player.add_token(self)
        logger.debug(f'Для токена {self.get_id()} установлен владелец {player.get_id()}')

    def remove_owner(self):
        """
        Удаляет владельца токена
        """
        self._owner = None
        if self in self._last_owner.tokens:
            self._last_owner.tokens.remove(self)
        logger.debug(f'Для токена {self.get_id()} удален владелец {self._last_owner.get_id()}')
    
    @abstractmethod
    def get_truth_table(self) -> dict:
        pass
    
    def evaluate(self, bool1: Operand, bool2: Operand):
        """Вычисляет по таблице истинности значение булевого выражения"""
        self._validate_operand(bool1, bool2)
        table = self.get_truth_table()
        logger.info(f"Вычисление выражения {bool1.get_value()} {self.to_string()} {bool2.get_value()}")
        return table.get((bool1.get_value(), bool2.get_value()))
    
    @abstractmethod
    def to_string(self) -> str:
        """Возвращает строковое представление токена."""
        pass

    def __hash__(self) -> int:
        return hash(self.get_id())
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Token):
            return False
        return self.get_id() == other.get_id()


class AND(Token):
    def __init__(self, owner=None) -> None:
        super().__init__(owner)
        self._prefix = 'and'
        self._id = self._generate_id(self._prefix)

    def get_truth_table(self) -> dict:
        return {
            (True, True): True,
            (True, False): False,
            (False, True): False,
            (False, False): False,
        }
    
    def to_string(self) -> str:
        return '^'


class OR(Token):
    def __init__(self, owner=None) -> None:
        super().__init__(owner)
        self._prefix = 'or'
        self._id = self._generate_id(self._prefix)

    def get_truth_table(self) -> dict:
        return {
            (True, True): True,
            (True, False): True,
            (False, True): True,
            (False, False): False,
        }
    
    def to_string(self) -> str:
        return 'v'

class XOR(Token):
    def __init__(self, owner=None) -> None:
        super().__init__(owner)
        self._prefix = 'xor'
        self._id = self._generate_id(self._prefix)

    def get_truth_table(self) -> dict:
        return {
            (True, True): False,
            (True, False): True,
            (False, True): True,
            (False, False): False,
        }
    
    def to_string(self) -> str:
        return '⊕'


class IMP(Token):
    def __init__(self, owner=None) -> None:
        super().__init__(owner)
        self._prefix = 'imp'
        self._id = self._generate_id(self._prefix)

    def get_truth_table(self) -> dict:
        return {
            (True, True): True,
            (True, False): False,
            (False, True): True,
            (False, False): True,
        }
    
    def to_string(self) -> str:
        return '⇒'

