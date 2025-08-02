# core/tokens.py
from abc import abstractmethod
from core.elements import Element
from core.operands import Operand


class Token(Element):
    def is_immutable(self) -> bool:
        return False
    
    @abstractmethod
    def get_truth_table(self) -> dict:
        pass
    
    def evaluate(self, bool1: Operand, bool2: Operand):
        """Вычисляет по таблице истинности значение булевого выражения"""
        table = self.get_truth_table()
        return table.get((bool1.get_value(), bool2.get_value()))



class AND(Token):
    def get_truth_table(self) -> dict:
        return {
            (True, True): True,
            (True, False): False,
            (False, True): False,
            (False, False): False,
        }


class OR(Token):
    def get_truth_table(self) -> dict:
        return {
            (True, True): True,
            (True, False): True,
            (False, True): True,
            (False, False): False,
        }

class XOR(Token):
    def get_truth_table(self) -> dict:
        return {
            (True, True): False,
            (True, False): True,
            (False, True): True,
            (False, False): False,
        }


class IMP(Token):
    def get_truth_table(self) -> dict:
        return {
            (True, True): True,
            (True, False): False,
            (False, True): True,
            (False, False): True,
        }

