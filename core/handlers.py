# core/handlers.py

from abc import ABC, abstractmethod
import logging

from core import settings
from core.displays import ConsoleDisplay
from core.players import Player
from core.tokens import AND, IMP, OR, XOR, Token


logger = logging.getLogger(__name__)

class InputHandler(ABC):
    @abstractmethod
    def get_tokens(self):
        """
        Выбор токенов перед стартом игры
        """
        pass

    @abstractmethod
    def get_move(self):
        """
        Обработка хода игрока: токен и координаты
        """
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def ask_play_again(self) -> bool:
        pass

class ConsoleInputHandler(InputHandler):
    """
    Обработчик ввода с консоли
    """
    def __init__(self) -> None:
        self.valid_tokens = {
            'AND': AND,
            'OR': OR,
            'XOR': XOR,
            'IMP': IMP
        }
        self.display = ConsoleDisplay()

    def get_tokens(self, tokens_amount=settings.INITIAL_TOKENS) -> list[Token]:
        tokens = []

        for i in range(1, tokens_amount + 1):
            while True:
                try:
                    self.display.show_prompt(f"Выберите токен №{i} {list(self.valid_tokens.keys())}: ")
                    token_str = input().strip().upper()
                    token_type = self.valid_tokens[token_str]
                except KeyError:
                    logger.warning(f'Пользователь ввел неверный тип токена: {token_str}. Новая попытка...')
                    self.display.show_prompt(
                        f"Неверный тип токена: Доступные токены: {list(self.valid_tokens.keys())}: "
                        )
                else:
                    tokens.append(token_type())
                    break

        logger.info(f'Игрок успешно выбрал токены: {[token.to_string() for token in tokens]}')
        return tokens
    
    def _validate_token_index(self, token_idx: int, player: Player):
        if not 1 <= token_idx <= len(player.tokens):
            raise IndexError(f"Порядковый номер токена должен быть от 1 до {len(player.tokens)}")
    
    def get_move(self, player: Player) -> tuple[int, int, int]:
        while True:
            try:
                self.display.show_prompt("Введите порядковый номер токена: ")
                token_idx = int(input())
                self._validate_token_index(token_idx, player)
            except ValueError as e:
                logger.warning(f'Ошибка: {e}')
                self.display.show_prompt(f"Номер токена должен быть целым числом!")
            except IndexError as e:
                logger.warning(f'Ошибка: {e}')
                self.display.show_prompt(
                    f"Порядковый номер токена должен быть от 1 до {len(player.tokens)}"
                    )
            else:
                break

        while True:
            try:
                self.display.show_prompt("Введите координаты клетки (два числа через пробел): ")
                row, col = list(map(int, input().split()))
            except ValueError as e:
                logger.warning(f'Ошибка: {e}')
                self.display.show_prompt(f"Координаты должны быть в целых числах!")
            else:
                break

        logger.debug(f'Пользователь ввел порядковый номер токена: {token_idx}; координаты: ({row}, {col})')
        return token_idx - 1, row, col

    def get_name(self) -> str:
        self.display.show_prompt("Введите имя (необязательно): ")
        name = input().strip()
        logger.debug(f'Введено имя: {name}')
        return name
    
    def ask_play_again(self) -> bool:
        self.display.show_prompt("Хотите сыграть еще раз? (Y/N) [Пропуск = да]: ")
        play_again = input().strip().upper()

        if play_again == 'N':
            logger.debug(f'Выбрана опция "Завершить игру"')
        else:
            logger.debug(f'Выбрана опция "Новый раунд"')
        return play_again != 'N'
    
    def ask_go_ahead(self) -> bool:
        self.display.show_prompt("Ну, что, начинаем игру? (Y/N) [Пропуск = да]: ")
        answer = input().strip().upper()
        return answer != 'N'
    


