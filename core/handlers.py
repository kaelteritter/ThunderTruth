# core/handlers.py

from abc import ABC, abstractmethod
import logging

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
        i = 1
        while i <= tokens_amount:
            try:
                token_str = input(f"Выберите токен {i}: ").strip().upper()
                token_type = self.tokens_map.get(token_str)
                if not token_type:
                    logger.warning(f'Пользователь ввел неверный тип токена: {token_str}. Новая попытка...')
                    raise InputHandlerDataError(f'Неверный тип токена. Варианты: AND, OR, XOR, IMP')

                tokens.append(token_type())
                i += 1
            except InputHandlerDataError:
                continue
            except EOFError:
                logger.error(f"Ввод токена {i} прерван (EOF)")
                raise
            except Exception as e:
                logger.error(f"Неожиданная ошибка: {str(e)}")
                raise

        logger.info(f'Игрок успешно выбрал токены: {[token.to_string() for token in tokens]}')

        return tokens
    
    def get_player_move(self):
        return super().get_player_move()
    