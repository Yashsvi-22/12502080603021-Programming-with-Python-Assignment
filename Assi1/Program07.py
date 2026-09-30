
import re


class FormulaError(Exception):
    pass


class InvalidFormatError(FormulaError):
    pass


class UnknownVariableError(FormulaError):
    pass


class DivisionByZeroError(FormulaError):
    pass


class UnsupportedOperatorError(FormulaError):
    pass


class FormulaValidator:
    def __init__(self):
        self.variables = {}

    def get_value(self, operand):
        if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", operand):
            return float(operand) if "." in operand else int(operand)

        if re.fullmatch(r"[A-Za-z_]\w*", operand):
            if operand in self.variables:
                return self.variables[operand]
            raise UnknownVariableError(
                f"Unknown variable: {operand}"
            )

        raise InvalidFormatError("Invalid operand")

    def evaluate(self, line):
        line = line.strip()

        if not line:
            raise InvalidFormatError("Empty formula")

        assignment = re.fullmatch(
            r"([A-Za-z_]\w*)\s*=\s*(.+)", line
        )

        if assignment:
            name, expression = assignment.groups()

            value = self.get_value(expression.strip())
            self.variables[name] = value
            return None

        match = re.fullmatch(
            r"(\S+)\s*([+\-*/%]+)\s*(\S+)", line
        )

        if not match:
            raise InvalidFormatError("Invalid formula format")

        left_text, operator, right_text = match.groups()

        if operator not in {"+", "-", "*", "/", "%"}:
            raise UnsupportedOperatorError(
                f"Unsupported operator: {operator}"
            )

        left = self.get_value(left_text)
        right = self.get_value(right_text)

        if operator in {"/", "%"} and right == 0:
            raise DivisionByZeroError("Division by zero")

        if operator == "+":
            result = left + right
        elif operator == "-":
            result = left - right
        elif operator == "*":
            result = left * right
        elif operator == "/":
            result = left / right
        else:
            result = left % right

        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return result


def main():
    calculator = FormulaValidator()

    print("Interactive Formula Validator")
    print("Enter a formula, assignment, or 'quit'.")

    while True:
        try:
            line = input("> ").strip()

            if line.lower() == "quit":
                break

            result = calculator.evaluate(line)

            if result is not None:
                print(result)

        except FormulaError as error:
            print(type(error).__name__)
            
            print(error)


if __name__ == "__main__":
    main()
