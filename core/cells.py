# core/cells.py
import logging
from typing import Any
from core.exceptions import InvalidCellValueError, OccupiedCellError
from core.elements import Element, Empty

logger = logging.getLogger(__name__)

class Cell:
    """
    Класс для представления клетки игрового поля
    ###### SOLID-карта #####
    # SRP: хранит только собственные значения и отвечает за назначение экземпляров подкласса Element в атрибут ._value
    # OCP: поддерживает расширение через Element, новые типы значений добавляются без изменения Cell
    # LSP: не наследуется, но подклассы (например, BorderCell) могут быть добавлены с соблюдением контракта
    # ISP: минимальный интерфейс (value, is_empty, set_value, clear), не навязывает лишних методов
    # DIP: зависит от абстракции Element, а не от конкретных реализаций Token, Operand или Stub
    """
    def __init__(self) -> None:
        self._value: Element = Empty()

    @property
    def value(self) -> Element:
        """Значение клетки"""
        return self._value
    
    @property
    def is_empty(self):
        """Проверяет, пуста ли клетка (содержит Empty)."""
        return isinstance(self._value, Empty)
    
    def clear(self) -> None:
        """
        Очистить клетку. Используется в тестах и при дебаге
        """
        self._value = Empty()
    
    def set_value(self, value: Element) -> bool:
        """
        Поставить элемент в клетку
        Публичный метод для строгой проверки
        """
        self._validate_mutable(value)
        return self._assign_value(value)

    def _assign_value(self, value: Element) -> bool:
        """
        Назначение элемента любого типа изменяемости
        Нужен при инициализации игрового поля
        """
        self._validate_value(value)
        logger.debug(f'В клетку помещен элемент {value}')
        self._value = value
        return True
    
    def _validate_mutable(self, value: Element):
        # Переданное значение - неизменяемый элемент
        if isinstance(value, Element) and value.is_immutable():
            logger.warning(f'Попытка разместить в клетку неизменяемый тип Element: {value}')
            raise InvalidCellValueError('Значение клетки должно быть изменяемым элементом')

    def _validate_value(self, value: Any) -> None:
        if not isinstance(value, Element):
            logger.warning(f'Попытка разместить в клетку значение не типа Element: {value}')
            raise InvalidCellValueError('Значение клетки должно быть подклассом Element')
        
        # В клетке находится заглушка или операнд
        if self._value.is_immutable() and not self.is_empty:
            logger.warning('Попытка разместиться в недоступной клетке')
            raise OccupiedCellError('Нельзя разместить в клетке неизменяемый элемент')
        
        # В клетке находится движимый элемент игры (например, токен)
        if not self.is_empty:
            logger.warning('Попытка разместиться в занятой клетке')
            raise OccupiedCellError(f'Эта клетка уже занята')