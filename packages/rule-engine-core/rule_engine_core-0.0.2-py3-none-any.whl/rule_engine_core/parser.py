"""
This module defines the Parser class, which is responsible for parsing the expression string of a rule or filter.
The expression string is a string of operands and operators.
The Parser class has the staticmethod:
    -> parse: parses the expression string and creates a prefix expression tree. It returns the root of the tree and raises RuntimeError if the expression is invalid.
"""
import logging
_logger = logging.getLogger(__name__)

def _replace_words_with_symbols(expression_str):
    """
    Replaces NOT by ! and AND by & and OR by | in the expression string.
    """
    expression_str = expression_str.replace("NOT", "!")
    expression_str = expression_str.replace("AND", "&")
    expression_str = expression_str.replace("OR", "|")
    return expression_str

import re

class Node:
    def __init__(self, value, left=None, right=None):
        """
        Represents a node in the expression tree.
        - value: a string representing an operator or operand.
        - left: the left child (None if not applicable).
        - right: the right child (None for leaves or unary operators).
        """
        self.value: str = value
        self.left: Node = left
        self.right: Node = right

    def __repr__(self):
        if self.left is None and self.right is None:
            return f"Node({self.value})"
        if self.right is None:
            return f"Node({self.value}, {self.left})"
        return f"Node({self.value}, {self.left}, {self.right})"

OPERATOR_SET = {'+', '-', '*', '/', '&', '|', '!', '<', '<=', '>', '>='}

class Parser:
    """
    A recursive descent parser for infix expressions that supports:
    - Parentheses: ( and )
    - Operands as numbers or identifiers (like abc)
    - Operators:
      * Unary: ! (logical not)
      * Binary arithmetic: +, -, *, /
      * Relational: <, <=, >, >=
      * Bitwise: & (and), | (or)
      
    Operator precedence (from highest to lowest):
      1. Unary: !
      2. Multiplicative: *, /
      3. Additive: +, -
      4. Comparison: <, <=, >, >=
      5. Bitwise AND: &
      6. Bitwise OR: |
    """
    def __init__(self, text: str):
        self.text = text
        self.tokens = self.tokenize(text)
        self.pos = 0

    def tokenize(self, text: str):
        # Define token specifications.
        token_spec = [
            ('NUMBER',   r'-?\d+(\.\d+)?'),         # Integer or decimal number
            ('RELOP',    r'(<=|>=|<|>)'),          # Relational operators
            ('IDENT',    r'[A-Za-z_]\w*'),         # Identifiers (operands)
            ('OP',       r'[+\-*/&|!]'),           # Other operators
            ('LPAREN',   r'\('),                  # Left Parenthesis
            ('RPAREN',   r'\)'),                  # Right Parenthesis
            ('SKIP',     r'\s+'),                 # Skip whitespace
            ('MISMATCH', r'.'),                   # Any other character
        ]
        token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
        tokens = []
        for mo in re.finditer(token_regex, text):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUMBER':
                tokens.append(('NUMBER', value))
            elif kind == 'RELOP':
                tokens.append(('RELOP', value))
            elif kind == 'IDENT':
                tokens.append(('IDENT', value))
            elif kind == 'OP':
                tokens.append(('OP', value))
            elif kind == 'LPAREN':
                tokens.append(('LPAREN', value))
            elif kind == 'RPAREN':
                tokens.append(('RPAREN', value))
            elif kind == 'SKIP':
                continue
            else:
                raise RuntimeError(f"Unexpected token: {value}")
        return tokens

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None, expected_value=None):
        token = self.peek()
        if token is None:
            return None
        if expected_type and token[0] != expected_type:
            raise RuntimeError(f"Expected token type '{expected_type}', got '{token[0]}' with value '{token[1]}'")
        if expected_value and token[1] != expected_value:
            raise RuntimeError(f"Expected token value '{expected_value}', got '{token[1]}'")
        self.pos += 1
        return token

    def parse_expression(self):
        # Top-level rule: start with the lowest precedence, bitwise OR.
        return self.parse_bitwise_or()

    def parse_bitwise_or(self):
        node = self.parse_bitwise_and()
        while True:
            token = self.peek()
            if token and token[0] == 'OP' and token[1] == '|':
                self.consume('OP', '|')
                right = self.parse_bitwise_and()
                node = Node('|', node, right)
            else:
                break
        return node

    def parse_bitwise_and(self):
        node = self.parse_comparison()
        while True:
            token = self.peek()
            if token and token[0] == 'OP' and token[1] == '&':
                self.consume('OP', '&')
                right = self.parse_comparison()
                node = Node('&', node, right)
            else:
                break
        return node

    def parse_comparison(self):
        node = self.parse_additive()
        token = self.peek()
        # Allow at most one comparison operator (non-associative)
        if token and token[0] == 'RELOP':
            op = token[1]
            self.consume('RELOP', op)
            right = self.parse_additive()
            node = Node(op, node, right)
        return node

    def parse_additive(self):
        node = self.parse_multiplicative()
        while True:
            token = self.peek()
            if token and token[0] == 'OP' and token[1] in ('+', '-'):
                op = token[1]
                self.consume('OP', op)
                right = self.parse_multiplicative()
                node = Node(op, node, right)
            else:
                break
        return node

    def parse_multiplicative(self):
        node = self.parse_unary()
        while True:
            token = self.peek()
            if token and token[0] == 'OP' and token[1] in ('*', '/'):
                op = token[1]
                self.consume('OP', op)
                right = self.parse_unary()
                node = Node(op, node, right)
            else:
                break
        return node

    def parse_unary(self):
        token = self.peek()
        if token and token[0] == 'OP' and token[1] == '!':
            self.consume('OP', '!')
            operand = self.parse_unary()
            return Node('!', operand)
        return self.parse_primary()

    def parse_primary(self):
        token = self.peek()
        if token is None:
            raise RuntimeError("Unexpected end of expression")
        if token[0] == 'NUMBER' or token[0] == 'IDENT':
            self.consume(token[0])
            return Node(token[1])
        elif token[0] == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expression()
            if self.peek() is None or self.peek()[0] != 'RPAREN':
                raise RuntimeError("Missing closing parenthesis")
            self.consume('RPAREN')
            return node
        else:
            raise RuntimeError(f"Unexpected token: {token}")

    @staticmethod
    def parse(expr: str) -> Node:
        """
        Parses the given infix expression string and returns the root 
        of the generated expression tree.
        Raises RuntimeError if the expression is invalid.
        """
        expr = _replace_words_with_symbols(expr)
        parser = Parser(expr)
        node = parser.parse_expression()
        if parser.pos != len(parser.tokens):
            errMsg = f"Invalid expression: Extra tokens present. Parser pos{parser.pos} and tokens  {parser.tokens}"
            _logger.error(errMsg)
            raise RuntimeError(errMsg)
        return node
        
