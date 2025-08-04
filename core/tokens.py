# core/tokens.py
from abc import abstractmethod
import logging
import uuid
from core.elements import Element
from core.exceptions import InvalidOperandError
from core.operands import Operand
# from core.players import Player


logger = logging.getLogger(__name__)

class Token(Element):
    def __init__(self, owner=None) -> None:
        self._owner = owner
        self._id = str(uuid.uuid4())

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


class AND(Token):
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
    def get_truth_table(self) -> dict:
        return {
            (True, True): True,
            (True, False): False,
            (False, True): True,
            (False, False): True,
        }
    
    def to_string(self) -> str:
        return '->'

