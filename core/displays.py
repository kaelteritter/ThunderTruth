from abc import ABC, abstractmethod

from core.board import Board


class Display(ABC):
    @abstractmethod
    def display_board(self, board: Board):
        pass

    # @abstractmethod
    # def show_hint(self, msg: str) -> str:
    #     """
    #     Подсказка по управлению
    #     """
    #     pass

    # @abstractmethod
    # def show_propmt(self, msg: str) -> str:
    #     """
    #     Сообщение о ходе игры
    #     """
    #     pass

    # @abstractmethod
    # def show_start(self) -> str:
    #     pass

    # @abstractmethod
    # def show_end(self) -> str:
    #     pass

    # @abstractmethod
    # def show_winner(self) -> str:
    #     pass

    # @abstractmethod
    # def show_draw(self) -> str:
    #     pass


class ConsoleDisplay(Display):
    def display_board(self, board: Board) -> None:
        for row in range(board.get_size_buffered()):
            row_cells = []
            for col in range(board.get_size_buffered()):
                element = board.get_cell_buffered(row, col).value.to_string()
                row_cells.append(element)

            print(' | '.join(row_cells))

        
