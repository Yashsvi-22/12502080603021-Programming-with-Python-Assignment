
import re
import sys
from functools import lru_cache


class CycleError(Exception):
    pass


class InvalidExpression(Exception):
    pass


def tokenize(expression):
    tokens = re.findall(
        r"\d+|[A-Za-z_][A-Za-z0-9_]*|[()+*-]|\S",
        expression
    )

    if "".join(tokens).replace(" ", "") != re.sub(r"\s+", "", expression):
        raise InvalidExpression()

    return tokens


def evaluate_expression(expression, variables):
    tokens = tokenize(expression)
    position = 0

    def parse_expression():
        nonlocal position
        value = parse_term()

        while position < len(tokens) and tokens[position] in ("+", "-"):
            operator = tokens[position]
            position += 1
            right = parse_term()

            if operator == "+":
                value += right
            else:
                value -= right

        return value

    def parse_term():
        nonlocal position
        value = parse_factor()

        while position < len(tokens) and tokens[position] == "*":
            position += 1
            value *= parse_factor()

        return value

    def parse_factor():
        nonlocal position

        if position >= len(tokens):
            raise InvalidExpression()

        token = tokens[position]

        if token == "-":
            position += 1
            return -parse_factor()

        if token == "+":
            position += 1
            return parse_factor()

        if token == "(":
            position += 1
            value = parse_expression()

            if position >= len(tokens) or tokens[position] != ")":
                raise InvalidExpression()

            position += 1
            return value

        if token.isdigit():
            position += 1
            return int(token)

        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
            position += 1
            return variables[token]

        raise InvalidExpression()

    result = parse_expression()

    if position != len(tokens):
        raise InvalidExpression()

    return result


def main():
    try:
        v = int(input())
        if v < 1 or v > 200000:
            print("INVALID")
            return

        definitions = {}

        for _ in range(v):
            line = input().strip()

            if "=" not in line:
                print("INVALID")
                return

            name, expression = line.split("=", 1)
            name = name.strip()
            expression = expression.strip()

            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                print("INVALID")
                return

            if name in definitions:
                print("INVALID")
                return

            definitions[name] = expression

        target = input().strip()
        if not target:
            print("INVALID")
            return

        visiting = set()
        memo = {}

        def resolve(name):
            if name in memo:
                return memo[name]

            if name not in definitions:
                raise InvalidExpression()

            if name in visiting:
                raise CycleError()

            visiting.add(name)

            def lookup(variable):
                return resolve(variable)

            value = evaluate_expression(
                definitions[name], VariableResolver(lookup)
            )

            visiting.remove(name)
            memo[name] = value
            return value

        class Resolver:
            def __init__(self, lookup):
                self.lookup = lookup

            def __getitem__(self, name):
                return self.lookup(name)

        VariableResolver = Resolver

        print(evaluate_expression(target, VariableResolver(resolve)))

    except CycleError:
        print("CYCLE")
    except (InvalidExpression, ValueError, RecursionError, KeyError):
        print("INVALID")
    except EOFError:
        print("INVALID")


if __name__ == "__main__":
    main()