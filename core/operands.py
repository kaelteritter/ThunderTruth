from abc import abstractmethod
from core.elements import Element


class Operand(Element):
    def is_immutable(self) -> bool:
        return True
    
    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def to_string(self) -> str:
        """Строковое представление операнда на игровом поле"""
        pass


class TrueOperand(Operand):
    def get_value(self):
        return True
    
    def to_string(self) -> str:
        return '1'

class FalseOperand(Operand):
    def get_value(self):
        return False
    
    def to_string(self) -> str:
        return '0'