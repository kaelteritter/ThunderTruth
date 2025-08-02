# core/elements.py
from abc import ABC, abstractmethod

class Element(ABC):
    @abstractmethod
    def is_immutable(self) -> bool:
        """
        Неизменяемость объекта на игровом поле.
        Такой объект нельзя двигать и переназначать.
        """
        pass


class Stub(Element):
    def is_immutable(self) -> bool:
        return True

class Empty(Element):
    def is_immutable(self) -> bool:
        return True
