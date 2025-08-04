# core/board.py

import logging
import random
from typing import Any
from core import settings
from core.cells import Cell
from core.exceptions import (
    InvalidCellCoordinateError, InvalidOperandError, 
    InvalidTokenError, OccupiedCellError,
)
from core.operands import FalseOperand, Operand, TrueOperand
from core.tokens import Token


logger = logging.getLogger(__name__)

class Board:
    """
    Игровая доска
    """
    def __init__(self, size: int = settings.BOARD_SIZE) -> None:
        self.size: int = size
        self.buffered_size: int = size + 2
        self.grid: list[list[Cell]] = self.initialize()

    def initialize(self) -> list[list[Cell]]:
        """
        Инициализация доски с пустыми клетками и буфером из заглушек
        """
        grid = [[Cell(stub=True) for _ in range(self.buffered_size)] for _ in range(self.buffered_size)]

        for row in range(1, self.size + 1):
            for col in range(1, self.size + 1):
                grid[row][col] = Cell(stub=False)

        logger.debug(
            f"Инициализировано поле {self.size}x{self.size} с буфером "
            f"{self.buffered_size}x{self.buffered_size}"
            )

        return grid
    
    def setup(self) -> bool:
        """Расстановка случайных операндов на поле"""
        for row in range(1, self.size + 1):
            for col in range(1, self.size + 1):

                # расстановка в шахматном порядке
                if (row + col) % 2 == 0:
                    operand = TrueOperand() if random.choice([True, False]) else FalseOperand()
                    self._place_operand(operand, row, col)

        logger.info('Игровое поле успешно создано.')
        return True

    
    def _validate_coordinate(self, row: int, col: int) -> None:
        if not 1 <= row <= self.size or not 1 <= col <= self.size:
            logger.warning(f'Попытка получить координату за пределами игрового поля: ({row}, {col})')
            raise InvalidCellCoordinateError(f'Неверные координаты клетки: ({row}, {col})')

    def get_cell(self, row: int, col: int) -> Cell:
        """
        Возвращает объект Cell игрового поля
        """
        self._validate_coordinate(row, col)
        return self.grid[row][col]
    
    def _validate_operand_placement(self, operand: Any, row: int, col: int) -> None:
        cell = self.get_cell(row, col)

        if not isinstance(operand, Operand):
            logger.warning(f"Попытка разместить не операнд: {operand}")
            raise InvalidOperandError('Операнд должен быть подклассом Operand')
        
        if not cell.is_empty:
            logger.warning(f"Попытка разместить операнд в занятую клетку ({row}, {col})")
            raise OccupiedCellError("Клетка уже содержит элемент")
    
    def _place_operand(self, operand: Operand, row: int, col: int) -> bool:
        """
        Защищенный метод для размещения операндов перед запуском игрового цикла
        """
        self._validate_operand_placement(operand, row, col)
        self.get_cell(row, col)._assign_value(operand)
        logger.debug(f"Операнд {operand.get_value()} размещен в клетке ({row}, {col})")
        return True
    
    def _validate_token_placement(self, token: Token, row: int, col: int) -> None:
        cell = self.get_cell(row, col)

        if not isinstance(token, Token):
            logger.warning(f"Попытка разместить не токен: {token}")
            raise InvalidTokenError('Токен должен быть подклассом Token')
        
        if not cell.is_empty:
            logger.warning(f"Попытка разместить токен в занятую клетку ({row}, {col})")
            raise OccupiedCellError("Клетка уже содержит элемент")
    
    def place_token(self, token: Token, row: int, col: int) -> bool:
        """
        Метод для размещения токенов-операторов
        """
        self._validate_token_placement(token, row, col)
        self.get_cell(row, col).set_value(token)
        logger.debug(f"Токен {token.to_string()} размещен в клетке ({row}, {col})")
        return True
