from abc import abstractmethod
from core.elements import Element


class Operand(Element):
    def is_immutable(self) -> bool:
        return True
    
    @abstractmethod
    def get_value(self):
        pass


class TrueOperand(Operand):
    def get_value(self):
        return True

class FalseOperand(Operand):
    def get_value(self):
        return False