# core/tokens.py
from core.elements import Element


class Token(Element):
    def is_immutable(self) -> bool:
        return False


class Empty(Token):
    ...

class AND(Token):
    ...

class OR(Token):
    ...

class XOR(Token):
    ...

class IMP(Token):
    ...