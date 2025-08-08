# core/handlers.py

from abc import ABC, abstractmethod
import logging
from typing import Callable

from core import settings
from core.exceptions import InputHandlerDataError
from core.tokens import AND, IMP, OR, XOR, Token


logger = logging.getLogger(__name__)




class InputHandler(ABC):
    @abstractmethod
    def get_player_token_choice(self):
        """
        Выбор токенов перед стартом игры
        """
        pass

    @abstractmethod
    def get_player_move(self):
        """
        Обработка хода игрока: токен и координаты
        """
        pass

    @abstractmethod
    def get_player_name(self):
        pass

class ConsoleInputHandler(InputHandler):
    """
    Обработчик ввода с консоли
    """
    def __init__(self) -> None:
        self.tokens_map = {
            'AND': AND,
            'OR': OR,
            'XOR': XOR,
            'IMP': IMP
        }
    def get_player_token_choice(self, tokens_amount=settings.INITIAL_TOKENS) -> list[Token]:
        tokens = []

        for i in range(1, tokens_amount + 1):
            parse_token = self._create_parser_token(f"Выберите токен {i}: ")
            token_type = parse_token()
            tokens.append(token_type())

        logger.info(f'Игрок успешно выбрал токены: {[token.to_string() for token in tokens]}')
        return tokens
    
    def _create_parser_token(self, prompt: str) -> Callable[[str], Token]:
        """
        Фабрика парсеров, преобразующих
        ввод в верхний регистр, и ищущих
        соответствие в хэш-таблице токенов
        """
        @safe_input(prompt)
        def parser(string: str) -> Token:
            token_str = string.strip().upper()
            token_type = self.tokens_map.get(token_str)
            if not token_type:
                logger.warning(f'Пользователь ввел неверный тип токена: {token_str}. Новая попытка...')
                raise InputHandlerDataError(f'Неверный тип токена. Допустимые значения: {list(self.tokens_map.keys())}')
            return token_type
        return parser

    def _create_parser_int(self, prompt: str) -> Callable[[str], int]:
        """
        Фабрика парсеров, преобразующих
        строку в целое число
        """
        @safe_input(prompt)
        def parser(string: str) -> int:
            return int(string)
        return parser
    
    def _create_parser_tuple_int(self, prompt: str) -> Callable[[str], tuple[int, int]]:
        """
        Фабрика парсеров, преобразующих
        строку в кортеж из двух чисел
        """
        @safe_input(prompt)
        def parser(string: str) -> tuple[int, int]:
            _int1, _int2 = tuple(map(int, string.split()))
            return _int1, _int2
        return parser
    
        
    def get_player_move(self) -> list[int]:
        parse_token = self._create_parser_int("Введите порядковый номер токена: ")
        parse_coords = self._create_parser_tuple_int("Введите координаты клетки (два числа через пробел): ")

        token = parse_token()
        row, col = parse_coords()

        logger.debug(f'Пользователь ввел: порядковый номер токена: {token}; координаты: ({row}, {col})')
        return [token, row, col]
    
    def _create_parser_str(self, prompt: str) -> Callable[[str], str]:
        @safe_input(prompt)
        def parser(string: str) -> str:
            return str(string)
        return parser

    
    def get_player_name(self) -> str:
        parse_name = self._create_parser_str("Введите имя (можно оставить пустым): ")
        name = parse_name()
        logger.debug(f'Введено имя: {name}')
        return name
    



def safe_input(prompt: str):
    """
    Декоратор для обработки
    стандартных ошибок при пользовательском вводе
    :attr prompt: подсказка при вводе
    """
    def decorator(parser_func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    string = input(prompt).strip()
                    return parser_func(string)
                except ValueError:
                    continue
                except InputHandlerDataError:
                    continue
                except EOFError:
                    logger.error(f"Ввод прерван (EOF)")
                    raise
                except KeyboardInterrupt:
                    logger.error(f"Ввод прерван пользователем")
                    raise
        return wrapper
    return decorator