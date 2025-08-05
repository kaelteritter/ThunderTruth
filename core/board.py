# core/board.py

import logging
import random
from typing import Any
from core import settings
from core.cells import Cell
from core.exceptions import (
    CellOutOfBorderError, InvalidOperandError, 
    InvalidTokenError, CellOccupiedError,
    BoardCoordinateTypeError,
)
from core.operands import FalseOperand, Operand, TrueOperand
from core.tokens import Token


logger = logging.getLogger(__name__)

class Board:
    """
    ОПИСАНИЕ:
    - Игровая доска. Отвечает за доступ к клеткам в пределах игровой сетки

    ИНТЕРФЕЙС:
    :::Методы:::
    - setup: запуск раунда игры - расстановка случайных операндов в шахматном порядке
    - get_cell: доступ к клетке в пределах реального игрового поля
    - get_cell_buffered: доступ к клетке в пределах игрового поля, включая буфер
    - get_size: реальный размер игрового поля
    - get_size_buffered: размер игрового поля, включая буфер
    - place_token: размещение токена в клетке
    """
    def __init__(self, size: int = settings.BOARD_SIZE) -> None:
        """
        attr:_size - реальный размер игрового поля
        attr:_buffered_size - размер игрового поля с буфером (нужен для упрощения проверок и 1-индексации)
        attr:_grid - двумерный массив, хранящий клетки поля
        """
        self._size: int = size
        self._buffered_size: int = size + 2
        self._grid: list[list[Cell]] = self._initialize()

    def get_size(self):
        """
        Возвращает реальный размер игрового поля
        """
        return self._size
    
    def get_size_buffered(self):
        """
        Возвращает размер игрового поля, включая буфер
        """
        return self._buffered_size

    def _initialize(self) -> list[list[Cell]]:
        """
        Инициализация доски с пустыми клетками и буфером из заглушек
        """
        grid = [[Cell(stub=True) for _ in range(self._buffered_size)] for _ in range(self._buffered_size)]

        for row in range(1, self._size + 1):
            for col in range(1, self._size + 1):
                grid[row][col] = Cell(stub=False)

        logger.debug(
            f"Инициализировано поле {self._size}x{self._size} с буфером "
            f"{self._buffered_size}x{self._buffered_size}"
            )

        return grid
    
    def setup(self) -> bool:
        """Расстановка случайных операндов на поле"""
        for row in range(1, self._size + 1):
            for col in range(1, self._size + 1):

                # расстановка в шахматном порядке
                if (row + col) % 2 == 0:
                    operand = TrueOperand() if random.choice([0, 1]) else FalseOperand()
                    self._place_operand(operand, row, col)

        logger.info('Игровое поле успешно создано.')
        return True

    
    def _validate_coordinate_type(self, row: int, col: int) -> None:
        if not type(row) == int or not type(col) == int:
            logger.warning(f'Попытка получить координату не типа int: ({row}, {col})')
            raise BoardCoordinateTypeError(f'Координаты должны быть целыми числами')

    def _validate_coordinate_buffered(self, row: int, col: int) -> None:
          if not 0 <= row < self._buffered_size or not 0 <= col < self._buffered_size:
            logger.warning(f'Попытка получить координату вне поля: ({row}, {col})')
            raise CellOutOfBorderError(f'Неверные координаты клетки: ({row}, {col}) (буфер включен)')     

    def _validate_coordinate(self, row: int, col: int) -> None:
        if not 1 <= row <= self._size or not 1 <= col <= self._size:
            logger.warning(f'Попытка получить координату за пределами игрового поля: ({row}, {col})')
            raise CellOutOfBorderError(f'Неверные координаты клетки: ({row}, {col})') 

    def get_cell(self, row: int, col: int) -> Cell:
        """
        Возвращает объект Cell в пределах реального игрового поля
        """
        self._validate_coordinate_type(row, col)
        self._validate_coordinate(row, col)
        logger.debug(f'Обращение к клетке ({row}, {col}) -> успешно возращен объект Cell')
        return self._grid[row][col]
    
    def get_cell_buffered(self, row: int, col: int) -> Cell:
        """
        Возвращает объект Cell в пределах всего поля, включая буфер
        """
        self._validate_coordinate_type(row, col)
        self._validate_coordinate_buffered(row, col)
        logger.debug(f'Обращение к клетке ({row}, {col}) -> успешно возращен объект Cell [buffered]')
        return self._grid[row][col]
    
    def _validate_operand_placement(self, operand: Any, row: int, col: int) -> None:
        cell = self.get_cell(row, col)

        if not isinstance(operand, Operand):
            logger.warning(f"Попытка разместить не операнд: {operand}")
            raise InvalidOperandError('Операнд должен быть подклассом Operand')
        
        if not cell.is_empty:
            logger.warning(f"Попытка разместить операнд в занятую клетку ({row}, {col})")
            raise CellOccupiedError("Клетка уже содержит элемент")
    
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
            logger.warning(f"Попытка разместить токен не типа Token: {token}")
            raise InvalidTokenError('Токен должен быть подклассом Token')
        
        if not cell.is_empty:
            logger.warning(f"Попытка разместить токен в занятую клетку ({row}, {col})")
            raise CellOccupiedError("Клетка уже содержит элемент")
    
    def place_token(self, token: Token, row: int, col: int) -> None:
        """
        Метод для размещения токенов-операторов
        """
        self._validate_token_placement(token, row, col)
        self.get_cell(row, col).set_value(token)
        logger.debug(
            f'Размещение к клетке ({row}, {col}) -> '
            f'успешно размещен токен {token.to_string()} c id:{token.get_id()}'
        )

