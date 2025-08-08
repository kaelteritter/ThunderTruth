# core/rules.py

from abc import ABC, abstractmethod
import logging

from core.board import Board
from core.elements import Element
from core.exceptions import CellOutOfBorderError, TokenInvalidError
from core.operands import FalseOperand, Operand, TrueOperand
from core.players import Player
from core.tokens import AND, IMP, OR, XOR, Token

logger = logging.getLogger(__name__)

class Rules(ABC):
    @abstractmethod
    def is_board_full(self, board: Board) -> bool:
        pass

    @abstractmethod
    def count_points(self, *args, **kwargs) -> int:
        pass

    @abstractmethod
    def check_winner(self) -> Player | None:
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
    - is_token_owner: владеет ли игрок данным токеном
    - count_points: подсчитать очки после хода
    - exclude_points_xor: добавить себе/убавить сопернику очки, если токен - XOR
    - check_winner: определить победителя в конце игры
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
            not board.get_cell(row, col).is_empty
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
    def check_winner(self, board: Board, *players) -> Player | None:
        """
        Определяет победителя (в конце игры)
        """
        if not self.is_board_full(board):
            return None

        players_by_points = list(sorted(players, key=lambda p: -p.get_points()))
        player1, player2 = players_by_points[0], players_by_points[1]

        if player1.get_points() == player2.get_points():
            return None
        return player1
        
    def is_token_owner(self, player: Player, token: Token):
        """
        Проверят, игрок, совершающий ход, кладет свой токен
        """
        if token.get_owner() != player:
            logger.debug(f'Проверка на владельца: токен {token.get_id()} не принадлежит игроку {player.get_id()}')
            return False
        logger.debug(f'Проверка на владельца: токен {token.get_id()} принадлежит игроку {player.get_id()}')
        return True
    
    def _is_chain_on_board(self, board: Board, chain: list[tuple[int, int]]) -> bool:
        if not all(1 <= _row <= board.get_size() and 1 <= _col <= board.get_size() for _row, _col in chain):
            logger.debug(f'Не все клетки в цепочке {chain} внутри игрового поля. Пропуск...')
            return False
        return True
    
    def _has_chain_valid_types(self, elements, types):
        if not all(isinstance(element, instance) for element, instance in zip(elements, types)):
            logger.debug(
                f'Не все клетки в цепочке верных типов: '
                f'Действительный/Ождиаемый типы элементов: '
                f'{[(type(element), instance) for element, instance in zip(elements, types)]}'
                )
            return False
        return True
        
    def exclude_points_xor(self, board: Board, row: int, col: int) -> tuple[Player, Player] | None:
        """
        Ищет "обнуляющую" цепочку из 3 операндов и 2 токенов (один - соперника, второй - свой XOR).
        В случае успеха возвращет двух игроков. Первый - соперник, второй - текущий игрок с XOR
        """
        chains = [
            [(row, col-3), (row, col-2), (row, col-1), (row, col), (row, col+1)],  # по горизонтали
            [(row-3, col), (row-2, col), (row-1, col), (row, col), (row+1, col)],  # по вертикали
        ]
        expected = [Operand, Token, Operand, XOR, Operand]

        for chain in chains:
            # Проверяем, что все координат в границах
            if not self._is_chain_on_board(board, chain):
                continue
            
            elements = [board.get_cell_buffered(_row, _col).value for _row, _col in chain]
            
            # Все элементы составляют цепочку op1, token1, op2, token2, op3
            if not self._has_chain_valid_types(elements, expected):
                continue

            op1, token1, op2, token2, op3 = elements

            # Токены принадлежат: один - сопернику, второй - делающему ход
            if self.is_token_owner(token2.get_owner(), token1):
                continue
            

            op1_op2 = TrueOperand() if token1.evaluate(op1, op2) else FalseOperand()
            result = token2.evaluate(op1_op2, op3)

            if result:
                logger.debug(
                f"Цепочка XOR: {op1.to_string()} {token1.to_string()} {op2.to_string()} "
                f"{token2.to_string()} {op3.to_string()} -> {result}"
                )
                return token1.get_owner(), token2.get_owner()
            
            else:
                logger.debug(
                    f"Цепочка XOR: {op1.to_string()} {token1.to_string()} {op2.to_string()} "
                    f"{token2.to_string()} {op3.to_string()} не валидна"
                    )

        return None
        
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

