from abc import ABC, abstractmethod


def get_value(row, arg) -> str:
    if arg['type'] == 'operand':
        return arg['value'].test(row)

    if arg['type'] == 'literal':
        return arg['value']

    if arg['type'] == 'column':
        return row[arg['value']]

    raise ValueError(arg)


class Operand(ABC):
    args: list

    def __init__(self):
        self.args = []

    @abstractmethod
    def test(self, row: list) -> bool:
        ...


class AndOperand(Operand):
    def test(self, row: list) -> bool:
        result = True

        for arg in self.args:
            if arg['type'] == 'operand':
                result = result and arg['value'].test(row)
            elif arg['type'] == 'literal':
                result = result and arg['value']

        return result


class OrOperand(Operand):
    def test(self, row: list) -> bool:
        result = False

        for arg in self.args:
            if arg['type'] == 'operand':
                result = result or arg['value'].test(row)
            elif arg['type'] == 'literal':
                result = result or arg['value']

        return result


class EqOperand(Operand):
    def test(self, row: list) -> bool:
        value1 = get_value(row, self.args[0])
        value2 = get_value(row, self.args[1])

        return value1 == value2


class EchoOperand(Operand):
    def test(self, row: list) -> any:
        if len(self.args) != 1:
            raise ValueError(self.args)

        return get_value(row, self.args[0])


class InOperand(Operand):
    def test(self, row: list) -> bool:
        value1 = get_value(row, self.args[0])
        value2 = get_value(row, self.args[1])

        return value1 in value2


operand_map: dict[str, Operand.__class__] = {
    'and': AndOperand,
    'or': OrOperand,
    'eq': EqOperand,
    'echo': EchoOperand,
    'in': InOperand
}
