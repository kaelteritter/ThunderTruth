# core/rules.py

from abc import ABC, abstractmethod
import logging

from core.board import Board
from core.elements import Element
from core.exceptions import TokenInvalidError
from core.operands import FalseOperand, TrueOperand
from core.players import Player
from core.tokens import AND, IMP, OR, XOR, Token

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

    def _validate_count_points_types(self, element: Element, row: int, col: int) -> None:
        if type(element) not in self.valid_token_classes:
            logger.warning(f'Передан неразрешенный тип токена: {element}')
            raise TokenInvalidError(
                f'Токен должен быть одного из следующих типов: {self.valid_token_classes}'
                )
        
    def is_token_owner(self, player: Player, token: Token):
        """
        Проверят, игрок, совершающий ход, кладет свой токен
        """
        if token.get_owner() != player:
            return False
        return True
        
    def count_points(self, board: Board, row: int, col: int):
        """
        Cчитает очки из клетки, в которой был положен токен
        """
        element = board.get_cell(row, col).value
        self._validate_count_points_types(element, row, col)

        # На данном этапе обработки токен не может не принадлежать игроку,
        # потому что это проверка осуществляется ранее окрестратром Game
        # через другой метод Rules

