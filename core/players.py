# core/players.py
from abc import ABC, abstractmethod

from core.tokens import Token


class Player(ABC):
    def __init__(self) -> None:
        self.tokens = set()

    @abstractmethod
    def add_token(self, token: Token) -> None:
        pass


class HumanPlayer(Player):
    def add_token(self, token: Token) -> None:
        self.tokens.add(token)

class AIPlayer(Player):
    def add_token(self, token: Token) -> None:
        self.tokens.add(token)