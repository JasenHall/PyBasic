import enum

# Language KEYWORDS
KEYWORDS = [
    "IF",
    "LET",
    "PRINT",
    "GOTO",
    "FOR",
    "THEN",
    "NEXT",
    "ELSE",
    "ENDIF",
    "INPUT",
    "LIST",
    "NEW",
    "RUN",
    "LOAD",
    "SAVE",
    "REM",
    "RND"
]


class Tokentype(enum.Enum):
    # TOKEN types
    INTEGER = "INTEGER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    EOF = "EOF"
    EQUALS = "EQUALS"
    SEMI = "SEMI"
    THEN = "THEN"
    ELSE = "ELSE"
    LET = "LET"
    PRINT = "PRINT"
    IF = "IF"
    GOTO = "GOTO"
    FOR = "FOR"
    NEXT = "NEXT"
    ENDIF = "ENDIF"
    LT = "LT"
    LTE = "LTE"
    GT = "GT"
    GTE = "GTE"
    NE = "NE"
    COLON = "COLON"
    INPUT = "INPUT"
    LIST = "LIST"
    NEW = "NEW"
    RUN = "RUN"
    SAVE = "SAVE"
    LOAD = "LOAD"
    REM = "REM"
    RND = "RND"


class Token:
    def __init__(self, type, val):
        self.value = val
        self.type = type


class Lexer:
    def __init__(self):
        self.text = None
        self.pos = 0
        self.current_char = None

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def identifier(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ""
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        return result

    def string(self):
        """Return a string consumed from the input."""
        result = ""
        self.advance()  # move past the quote identifier
        while self.current_char is not None and self.current_char is not '"':
            result += self.current_char
            self.advance()
        self.advance()  # move past the closing quote identifier
        return result

    def peek(self):
        """Peek at the next character without advancing"""
        return self.text[self.pos+1]

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(Tokentype.INTEGER, self.integer())

            if self.current_char.isalpha():  # must start with alpha char
                value = self.identifier()
                if value.upper() in KEYWORDS:
                    return Token(Tokentype(value.upper()), value.upper())
                else:
                    return Token(Tokentype.IDENTIFIER, value)

            if self.current_char == '"':  # double quote for string identity
                return Token(Tokentype.STRING, self.string())

            if self.current_char == '+':
                self.advance()
                return Token(Tokentype.PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(Tokentype.MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(Tokentype.MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(Tokentype.DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(Tokentype.LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(Tokentype.RPAREN, ')')

            if self.current_char == '=':
                self.advance()
                return Token(Tokentype.EQUALS, '=')

            if self.current_char == ';':
                self.advance()
                return Token(Tokentype.SEMI, ';')

            if self.current_char == ':':
                self.advance()
                return Token(Tokentype.COLON, ':')

            if self.current_char == ">":
                if self.peek() == "=":
                    self.advance()
                    self.advance()
                    return Token(Tokentype.GTE, ">=")
                else:
                    self.advance()
                    return Token(Tokentype.GT, ">")

            if self.current_char == "<":
                if self.peek() == "=":
                    self.advance()
                    self.advance()
                    return Token(Tokentype.LTE, "<=")
                elif self.peek() == ">":
                    self.advance()
                    self.advance()
                    return Token(Tokentype.NE, "<>")
                else:
                    self.advance()
                    return Token(Tokentype.LT, "<")

            self.error()

        return Token(Tokentype.EOF, None)

    def tokenize(self, text):
        """ Return a list of tokens from the input"""
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        token_list = []
        token = self.get_next_token()
        while token.type is not Tokentype.EOF:
            token_list.append(token)
            token = self.get_next_token()
        token_list.append(token)   # append the EOF token
        return token_list
