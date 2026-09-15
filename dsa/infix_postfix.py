# Infix to Postfix using Stack

from dsa.stack import Stack
from dsa.simple_infix_postfix import (
    evaluate_postfix as evaluate_postfix_with_steps,
    infix_to_postfix as infix_to_postfix_with_steps,
)


class InfixPostfix:
    """Class-based API used by the expression visualizer endpoint."""

    @staticmethod
    def infix_to_postfix(expression):
        return infix_to_postfix_with_steps(expression)

    @staticmethod
    def evaluate_postfix(expression):
        return evaluate_postfix_with_steps(expression)


def precedence(operator):
    if operator == '+' or operator == '-':
        return 1
    elif operator == '*' or operator == '/':
        return 2
    elif operator == '^':
        return 3
    return 0


def infix_to_postfix(expression):

    stack = Stack(max_size=100)
    result = ""

    for ch in expression:

        # If character is a number or letter
        if ch.isalnum():
            result = result + ch

        # If opening bracket
        elif ch == '(':
            stack.push(ch)

        # If closing bracket
        elif ch == ')':
            while not stack.is_empty() and stack.peek() != '(':
                result = result + stack.pop()

            stack.pop()

        # If operator
        else:
            while (not stack.is_empty() and
                   precedence(stack.peek()) >= precedence(ch)):
                result = result + stack.pop()

            stack.push(ch)

    # Remove remaining operators
    while not stack.is_empty():
        result = result + stack.pop()

    return result


if __name__ == "__main__":
    expression = "A+B*C"
    postfix = infix_to_postfix(expression)
    print("Infix:", expression)
    print("Postfix:", postfix)