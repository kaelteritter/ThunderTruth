# core/board.py

import logging
from core import settings
from core.cells import Cell


logger = logging.getLogger(__name__)

class Board:
    """
    Игровая доска
    """
    def __init__(self, size: int = settings.BOARD_SIZE) -> None:
        self.size = size
        self.buffered_size = size + 2
        self.grid = self.initialize()

    def initialize(self):
        """
        Инициализация доски с пустыми клетками и буфером из заглушек
        """
        grid = [[Cell(stub=True) for _ in range(self.buffered_size)] for _ in range(self.buffered_size)]

        for row in range(1, self.size + 1):
            for col in range(1, self.size + 1):
                grid[row][col] = Cell(stub=False)

        logger.debug(
            f"Инициализировано поле {self.size}x{self.size} с буфером "
            f"{self.size + 2}x{self.size + 2}"
            )

        return grid