# core/rules.py

from abc import ABC, abstractmethod
import logging

from core.board import Board
from core.exceptions import TokenInvalidError
from core.operands import FalseOperand, TrueOperand
from core.tokens import AND, IMP, OR, XOR

logger = logging.getLogger(__name__)

class Rules(ABC):
    @abstractmethod
    def count_points(self, *args, **kwargs):
        pass

    
class ThunderTruthRules(Rules):
    def __init__(self) -> None:
        self.directions = ['up', 'left', 'right', 'down']
        self.directions_to_check = [
            ('up', 'left'),
            ('up', 'right'),
            ('up', 'down'),
            ('left', 'down'),
            ('left', 'right'),
            ('down', 'right'),
        ]
        self.valid_token_classes = [AND, OR, XOR, IMP]
        self.valid_operand_classes = [TrueOperand, FalseOperand]

    def _validate_count_points_types(self, board: Board, row: int, col: int) -> None:
        element = board.get_cell(row, col).value
        if type(element) not in self.valid_token_classes:
            logger.warning(f'Передан неразрешенный тип токена: {element}')
            raise TokenInvalidError(
                f'Токен должен быть одного из следующих типов: {self.valid_token_classes}'
                )
    
    def count_points(self, board: Board, row: int, col: int):
        """
        Cчитает очки исходя из клетки, в которой был положен токен
        """
        self._validate_count_points_types(board, row, col)