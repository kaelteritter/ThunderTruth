# core/elements.py
from abc import ABC, abstractmethod

class Element(ABC):
    @abstractmethod
    def is_immutable(self) -> bool:
        """
        Неизменяемость объекта на игровом поле.
        Неизменяемый объект нельзя двигать и переназначать.
        """
        pass

    @abstractmethod
    def to_string(self) -> str:
        """
        Строковое представление элемента на игровом поле
        в консоли
        """
        pass


class Stub(Element):
    def is_immutable(self) -> bool:
        return True
    
    def to_string(self) -> str:
        return '#'

class Empty(Element):
    def is_immutable(self) -> bool:
        return True
    
    def to_string(self) -> str:
        return '.'
