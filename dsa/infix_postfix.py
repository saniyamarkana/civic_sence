"""
Infix to Postfix conversion and evaluation for Civic Sense Management System.
Used for complaint filter/search expression handling and priority score calculation.

Example expressions:
  Priority Score: ( complaints * 3 + urgency * 2 ) / total
  Filter: ( category == Garbage AND priority == High ) OR status == Pending
"""


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
        Convert infix expression to postfix.
        Returns (postfix_string, step_log) where step_log shows stack state at each step.
        """
        output = []
        stack = []
        steps = []  # Log of (token, stack_state, output_state, action)
        tokens = cls._tokenize(expression)

        for token in tokens:
            action = ""
            if cls._is_number(token) or (token.isalpha() and token not in ('(', ')')):
                output.append(token)
                action = f"Operand '{token}' → Output"
            elif token == '(':
                stack.append(token)
                action = "Push '(' to stack"
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()  # Remove '('
                action = "Pop until '(' found"
            elif token in cls.PRECEDENCE:
                while (stack and stack[-1] != '(' and
                       stack[-1] in cls.PRECEDENCE and
                       (cls.PRECEDENCE[stack[-1]] > cls.PRECEDENCE[token] or
                        (cls.PRECEDENCE[stack[-1]] == cls.PRECEDENCE[token] and
                         token not in cls.RIGHT_ASSOC))):
                    output.append(stack.pop())
                stack.append(token)
                action = f"Operator '{token}' → Stack"

            steps.append({
                "token": token,
                "stack": stack.copy(),
                "output": output.copy(),
                "action": action,
            })

        while stack:
            op = stack.pop()
            output.append(op)
            steps.append({
                "token": "-",
                "stack": stack.copy(),
                "output": output.copy(),
                "action": f"Pop remaining '{op}' → Output",
            })

        return " ".join(output), steps

    @classmethod
    def evaluate_postfix(cls, expression):
        """
        Evaluate a postfix expression with numeric values.
        Returns (result, step_log).
        """
        stack = []
        steps = []
        tokens = expression.split()

        for token in tokens:
            if cls._is_number(token):
                stack.append(float(token))
                steps.append({
                    "token": token,
                    "stack": stack.copy(),
                    "action": f"Push {token}",
                })
            elif token in cls.PRECEDENCE:
                if len(stack) < 2:
                    return None, steps
                b = stack.pop()
                a = stack.pop()
                result = cls._apply_operator(token, a, b)
                if result is None:
                    return None, steps
                stack.append(result)
                steps.append({
                    "token": token,
                    "stack": stack.copy(),
                    "action": f"{a} {token} {b} = {result}",
                })

        return stack[0] if stack else None, steps

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
