"""
Infix to Postfix conversion and evaluation for Civic Sense Management System.
Used for complaint filter/search expression handling and priority score calculation.

Phase 1 requirement: Applying the project's own Stack class for expression handling.
The Stack (from stack.py) is used as the operator/operand stack during conversion and
evaluation, demonstrating a real-world application of the Stack data structure.

Example expressions:
  Priority Score: ( complaints * 3 + urgency * 2 ) / total
  Filter: ( category == Garbage AND priority == High ) OR status == Pending
"""

# Use the project's own Stack class for expression handling (Phase 1 requirement)
from dsa.stack import Stack


class InfixPostfix:
    """Handles infix-to-postfix conversion and postfix evaluation using a stack."""

    PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    RIGHT_ASSOC = {'^'}

    @staticmethod
    def is_operand(ch):
        """Check if character is an operand (number or variable)."""
        return ch.isalnum() or ch == '.'

    @classmethod
    def infix_to_postfix(cls, expression):
        """
        Convert infix expression to postfix using the project's Stack class.
        Returns (postfix_string, step_log) where step_log shows stack state at each step.
        """
        output = []
        op_stack = Stack(max_size=200)  # Uses project's own Stack DSA class
        steps = []  # Log of (token, stack_state, output_state, action)
        tokens = cls._tokenize(expression)

        for token in tokens:
            action = ""
            if cls._is_number(token) or (token.isalpha() and token not in ('(', ')')):
                output.append(token)
                action = f"Operand '{token}' → Output"
            elif token == '(':
                op_stack.push(token)
                action = "Push '(' to stack"
            elif token == ')':
                while not op_stack.is_empty() and op_stack.peek() != '(':
                    output.append(op_stack.pop())
                if not op_stack.is_empty():
                    op_stack.pop()  # Remove '('
                action = "Pop until '(' found"
            elif token in cls.PRECEDENCE:
                while (not op_stack.is_empty() and
                       op_stack.peek() != '(' and
                       op_stack.peek() in cls.PRECEDENCE and
                       (cls.PRECEDENCE[op_stack.peek()] > cls.PRECEDENCE[token] or
                        (cls.PRECEDENCE[op_stack.peek()] == cls.PRECEDENCE[token] and
                         token not in cls.RIGHT_ASSOC))):
                    output.append(op_stack.pop())
                op_stack.push(token)
                action = f"Operator '{token}' → Stack"

            steps.append({
                "token": token,
                "stack": op_stack.to_list(),
                "output": output.copy(),
                "action": action,
            })

        # Drain remaining operators from the Stack
        while not op_stack.is_empty():
            op = op_stack.pop()
            output.append(op)
            steps.append({
                "token": "-",
                "stack": op_stack.to_list(),
                "output": output.copy(),
                "action": f"Pop remaining '{op}' → Output",
            })

        return " ".join(output), steps

    @classmethod
    def evaluate_postfix(cls, expression):
        """
        Evaluate a postfix expression with numeric values using the project's Stack class.
        Returns (result, step_log).
        """
        operand_stack = Stack(max_size=200)  # Uses project's own Stack DSA class
        steps = []
        tokens = expression.split()

        for token in tokens:
            if cls._is_number(token):
                operand_stack.push(float(token))
                steps.append({
                    "token": token,
                    "stack": operand_stack.to_list(),
                    "action": f"Push {token}",
                })
            elif token in cls.PRECEDENCE:
                if operand_stack.size() < 2:
                    return None, steps
                b = operand_stack.pop()
                a = operand_stack.pop()
                result = cls._apply_operator(token, a, b)
                if result is None:
                    return None, steps
                operand_stack.push(result)
                steps.append({
                    "token": token,
                    "stack": operand_stack.to_list(),
                    "action": f"{a} {token} {b} = {result}",
                })

        return operand_stack.pop() if not operand_stack.is_empty() else None, steps

    @staticmethod
    def _apply_operator(op, a, b):
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            return a / b if b != 0 else None
        elif op == '^':
            return a ** b
        return None

    @staticmethod
    def _tokenize(expression):
        """Split expression into tokens."""
        tokens = []
        current = ""
        for ch in expression:
            if ch == ' ':
                if current:
                    tokens.append(current)
                    current = ""
            elif ch in '()+-*/^':
                if current:
                    tokens.append(current)
                    current = ""
                tokens.append(ch)
            else:
                current += ch
        if current:
            tokens.append(current)
        return tokens

    @staticmethod
    def _is_number(s):
        """Check if string is a valid number."""
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def get_sample_expressions(cls):
        """Return sample expressions for demonstration."""
        return [
            "( 3 + 5 ) * 2",
            "10 + 2 * 3 - 1",
            "( 8 - 2 ) * ( 3 + 4 )",
            "5 ^ 2 + 3 * 4",
            "( ( 2 + 3 ) * 4 ) / 5",
        ]
