"""
Simple Infix to Postfix Conversion and Evaluation
===================================================
Written from scratch using basic Python — no libraries needed.

Used in CivicSense to calculate Priority Score for complaints.

Formula (Infix):   ( priority_weight * 3 + status_weight * 2 ) / 5
After Conversion:  priority_weight 3 * status_weight 2 * + 5 /

Step 1 — infix_to_postfix()   : converts infix string to postfix
Step 2 — evaluate_postfix()   : evaluates the postfix and returns result
Step 3 — calc_priority_score(): puts it together for complaints
"""


# ─────────────────────────── Basic Stack ───────────────────────────

class SimpleStack:
    """A simple stack using a Python list (Last In, First Out)."""

    def __init__(self):
        self.items = []           # list to hold stack elements

    def push(self, item):
        """Add item to top of stack."""
        self.items.append(item)

    def pop(self):
        """Remove and return item from top of stack."""
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        """Look at top item without removing it."""
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        """Return True if stack has no items."""
        return len(self.items) == 0

    def to_list(self):
        """Return stack contents as a list (bottom to top)."""
        return list(self.items)


# ─────────────────────────── Operator Precedence ───────────────────────────

# Higher number = higher precedence (done first)
PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
}


# ─────────────────────────── Step 1: Infix to Postfix ──────────────────────

def infix_to_postfix(expression):
    """
    Convert an infix expression to postfix using a Stack.

    Rules:
      - If token is a number  -> add directly to output
      - If token is '('       -> push to stack
      - If token is ')'       -> pop from stack to output until '(' found
      - If token is operator  -> pop operators of higher/equal precedence first,
                                 then push current operator
      - At the end            -> pop all remaining operators from stack to output

    Returns:
      postfix_string  (str)  -- the postfix expression
      steps           (list) -- each step: { token, stack, output, action }
    """
    output = []         # list of tokens in postfix order
    stack  = SimpleStack()
    steps  = []         # log of every step for display

    # split by spaces: "( 3 + 5 )" becomes ['(', '3', '+', '5', ')']
    tokens = expression.split()

    for token in tokens:

        # CASE 1: Number (operand) — add directly to output
        if is_number(token):
            output.append(token)
            action = "Number '{}' added to output".format(token)

        # CASE 2: Opening bracket — push to stack
        elif token == '(':
            stack.push(token)
            action = "Found '(' pushed to stack"

        # CASE 3: Closing bracket — pop until matching '('
        elif token == ')':
            while not stack.is_empty() and stack.peek() != '(':
                output.append(stack.pop())
            stack.pop()     # discard the '('
            action = "Found ')' popped operators until '('"

        # CASE 4: Operator (+, -, *, /, ^)
        elif token in PRECEDENCE:
            # Pop operators that have higher or equal precedence from stack first
            while (
                not stack.is_empty() and
                stack.peek() in PRECEDENCE and
                PRECEDENCE[stack.peek()] >= PRECEDENCE[token]
            ):
                output.append(stack.pop())
            stack.push(token)
            action = "Operator '{}' pushed to stack".format(token)

        else:
            action = "Unknown token '{}' skipped".format(token)

        # Record this step
        steps.append({
            "token":  token,
            "stack":  stack.to_list(),
            "output": list(output),
            "action": action,
        })

    # DRAIN: Pop any remaining operators from stack to output
    while not stack.is_empty():
        op = stack.pop()
        output.append(op)
        steps.append({
            "token":  "-",
            "stack":  stack.to_list(),
            "output": list(output),
            "action": "Stack drain popped '{}' to output".format(op),
        })

    postfix_string = " ".join(output)
    return postfix_string, steps


# ─────────────────────────── Step 2: Evaluate Postfix ──────────────────────

def evaluate_postfix(postfix_string):
    """
    Evaluate a postfix expression using a Stack.

    Rules:
      - If token is a number    -> push it onto the stack
      - If token is an operator -> pop two numbers, apply operator, push result

    Returns:
      result     (float) -- the final answer
      eval_steps (list)  -- each step: { token, stack, action }
    """
    stack      = SimpleStack()
    eval_steps = []

    tokens = postfix_string.split()

    for token in tokens:

        # CASE 1: Number -> push onto stack
        if is_number(token):
            stack.push(float(token))
            eval_steps.append({
                "token":  token,
                "stack":  stack.to_list(),
                "action": "Push {}".format(token),
            })

        # CASE 2: Operator -> pop two, calculate, push result
        elif token in PRECEDENCE:
            b = stack.pop()     # second operand (popped first)
            a = stack.pop()     # first operand  (popped second)
            result = apply_operator(token, a, b)
            stack.push(result)
            eval_steps.append({
                "token":  token,
                "stack":  stack.to_list(),
                "action": "{} {} {} = {}".format(a, token, b, result),
            })

    final_result = stack.pop()
    return final_result, eval_steps


# ─────────────────────────── Helper: Apply Operator ────────────────────────

def apply_operator(op, a, b):
    """Apply a math operator to two numbers."""
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        return a / b if b != 0 else 0
    elif op == '^':
        return a ** b
    return 0


# ─────────────────────────── Helper: Is Number? ────────────────────────────

def is_number(token):
    """Check if a string is a valid number (int or float)."""
    try:
        float(token)
        return True
    except (ValueError, TypeError):
        return False


# ─────────────────────────── Step 3: Priority Score ────────────────────────

# Map priority strings to numeric weights
PRIORITY_WEIGHTS = {
    "High":   3,
    "Medium": 2,
    "Low":    1,
}

# Map status strings to numeric weights
STATUS_WEIGHTS = {
    "Pending":     3,
    "In Progress": 2,
    "Approved":    2,
    "Resolved":    1,
    "Rejected":    0,
}


def calc_priority_score(priority, status):
    """
    Calculate urgency score for a complaint using Infix to Postfix evaluation.

    Formula (Infix): ( priority_weight * 3 + status_weight * 2 ) / 5

    Example — High + Pending:
      pw = 3, sw = 3
      Infix:   ( 3 * 3 + 3 * 2 ) / 5
      Postfix: 3 3 * 3 2 * + 5 /
      Result:  ( 9 + 6 ) / 5 = 15 / 5 = 3.0  --> CRITICAL

    Returns a dict with infix, postfix, steps, score, label, level.
    """
    # Look up numeric weights
    pw = PRIORITY_WEIGHTS.get(priority, 2)   # priority weight
    sw = STATUS_WEIGHTS.get(status, 1)       # status weight

    # Build the infix expression as a spaced string
    infix_expr = "( {} * 3 + {} * 2 ) / 5".format(pw, sw)

    # Step 1: Convert infix to postfix
    postfix_expr, conversion_steps = infix_to_postfix(infix_expr)

    # Step 2: Evaluate the postfix expression
    raw_result, eval_steps = evaluate_postfix(postfix_expr)

    # Round to 2 decimal places
    score = round(raw_result, 2)

    # Determine urgency label from score
    if score >= 2.8:
        label = "CRITICAL"
        level = "critical"
    elif score >= 2.0:
        label = "HIGH"
        level = "high"
    elif score >= 1.4:
        label = "MEDIUM"
        level = "medium"
    else:
        label = "LOW"
        level = "low"

    return {
        "priority":         priority,
        "status":           status,
        "priority_weight":  pw,
        "status_weight":    sw,
        "infix":            infix_expr,
        "postfix":          postfix_expr,
        "conversion_steps": conversion_steps,
        "eval_steps":       eval_steps,
        "score":            score,
        "label":            label,
        "level":            level,
    }


# ─────────────────────────── Quick Demo ────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        ("High",   "Pending"),
        ("High",   "In Progress"),
        ("Medium", "Pending"),
        ("Low",    "Resolved"),
    ]

    for priority, status in test_cases:
        result = calc_priority_score(priority, status)
        print("\nPriority: {}  |  Status: {}".format(priority, status))
        print("  Infix   : {}".format(result['infix']))
        print("  Postfix : {}".format(result['postfix']))
        print("  Score   : {}  [{}]".format(result['score'], result['label']))
