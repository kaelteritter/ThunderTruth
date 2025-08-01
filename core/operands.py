from core.elements import Element


class Operand(Element):
    def is_immutable(self) -> bool:
        return True


class TrueOperand(Operand):
    ...

class FalseOperand(Operand):
    ...