# core/rules.py

from abc import ABC, abstractmethod
import logging

from core.board import Board
from core.elements import Element
from core.exceptions import TokenInvalidError
from core.operands import FalseOperand, Operand, TrueOperand
from core.players import Player
from core.tokens import AND, IMP, OR, XOR, Token

logger = logging.getLogger(__name__)

class Rules(ABC):
    @abstractmethod
    def 1(self, board: Board) -> bool:
        pass

    @abstractmethod
    def count_points(self, *args, **kwargs) -> int:
        pass

    
class ThunderTruthRules(Rules):
    """
    ОПИСАНИЕ:
    - Привила игры ThunderTruth. Отвечает за информацию о направлениях на
    игровой доске, проверку завершения игры, подсчет очков, проверку
    победителя, проверку владельца токена
    ИНТЕРФЕЙС:
    :::Методы:::
    - is_board_full: остались ли пустые клетки на игровом поле
    """
    def __init__(self) -> None:
        self.directions = ['up', 'left', 'right', 'down']
        self.directions_to_check = [
            ('up', 'left'),
            ('up', 'right'),
            ('up', 'down'),
            ('left', 'down'),
            ('left', 'right'),
            ('right', 'down'),
        ]
        self.valid_token_classes = [AND, OR, XOR, IMP]
        self.valid_operand_classes = [TrueOperand, FalseOperand]

    def is_board_full(self, board: Board) -> bool:
        status = all(
            board.get_cell(row, col).is_empty == False
            for row in range(1, board.get_size() + 1) 
            for col in range(1, board.get_size() + 1)
            )
        if status:
            logger.info(f'Проверка на пустые клетки: игровое поле заполнено!')
        else:
            logger.debug(f'Проверка на пустые клетки: на доске еще остались пустые клетки')
        return status

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
            logger.debug(f'Проверка на владельца: токен {token.get_id()} не принадлежит игроку {player.get_id()}')
            return False
        logger.debug(f'Проверка на владельца: токен {token.get_id()} принадлежит игроку {player.get_id()}')
        return True
        
    def count_points(self, board: Board, row: int, col: int) -> int:
        """
        Cчитает очки из клетки, в которую был положен токен
        """
        element = board.get_cell(row, col).value
        self._validate_count_points_types(element, row, col)

        # На данном этапе обработки токен не может не принадлежать игроку,
        # потому что это проверка осуществляется ранее окрестратром Game
        # через другой метод Rules

        neighbors = board.get_neighbors(row, col)
        neighbors = dict(zip(self.directions, neighbors))
        points = 0

        for direction1, direction2 in self.directions_to_check:
            neighbor1 = neighbors[direction1].value
            neighbor2 = neighbors[direction2].value
            if isinstance(neighbor1, Operand) and isinstance(neighbor2, Operand):
                result = element.evaluate(neighbor1, neighbor2)
                logger.debug(
                    f'Сосед '
                    f'{direction1} {neighbor1.to_string()} '
                    f'{element.to_string()} '
                    f'{neighbor2.to_string()} {direction2} '
                    f'-> {result}'
                    )
                points += 1 if result else 0

        return points

