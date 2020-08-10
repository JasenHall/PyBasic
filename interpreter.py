INTEGER, SYMBOL, STRING, KEYWORD, IDENTIFIER = "INTEGER", "SYMBOL", "STRING", "KEYWORD", "IDENTIFIER"

SYMBOLS = ["+", "-", "*", "/", "="]


class Interpreter:

    def __init__(self):
        self.symboltable = {}
        self.token_stream = None
        self.current_token = None
        self.position = 0  #
        self.result = None

    # #### helper methods ######

    def consume(self, content):
        # consume a token and advance if the current token matches else error
        if self.current_token.type in content:
            self.advance()
        else:
            self.error()

    def error(self, msg="Syntax Error"):
        raise SyntaxError(msg)

    def advance(self):
        if self.position < len(self.token_stream):
            self.current_token = self.token_stream[self.position]
            self.position += 1

    # ######################### processing methods ##################################
    def compileStatement(self, source):
        # statement*
        # letStatement|ifStatement|whileStatement
        self.token_stream = source
        self.result = None
        self.position = 0
        self.advance()
        if self.current_token.value == "LET":
            self.consume(KEYWORD)
            self.compileLet()
            print("ok")
        elif self.current_token.value == "PRINT":
            self.consume(KEYWORD)
            self.compilePrint()
            print("ok")
        else:
            self.error()

    def compileLet(self):
        # 'let' Identifier ('['expression']')? '=' expression ';'
        name = self.current_token.value
        self.consume(IDENTIFIER)
        if self.current_token.value == "=":
            self.consume(SYMBOL)
        else:
            raise self.error()
        result = self.compileExpression()
        self.symboltable.update({name: result})

    def compilePrint(self):
        # 'print'  expression (';' expression )*
        result = self.compileExpression()
        string = result
        while self.current_token.value == ";":
            self.consume(SYMBOL)
            result = self.compileExpression()
            string += result
        print(string if string else "")

    def compileExpression(self):
        # expression: term ( (PLUS|MINUS) term)*
        result = self.compileTerm()
        while self.current_token.value in ("+", "-"):
            if self.current_token.value == "+":
                self.consume(SYMBOL)
                result += self.compileTerm()
            elif self.current_token.value == "-":
                self.consume(SYMBOL)
                result -= self.compileTerm()
        return result

    def compileTerm(self):
        # term: factor ( (MUL|DIV) factor)*
        result = self.compileFactor()
        while self.current_token.value in ("*", "/"):
            if self.current_token.value == "*":
                self.consume(SYMBOL)
                result *= self.compileFactor()
            elif self.current_token.value == "/":
                self.consume(SYMBOL)
                result /= self.compileFactor()
        return result

    def compileFactor(self):
        # factor: integer | identifier | string | (expr)
        token = self.current_token
        if token.type == INTEGER:
            self.consume(INTEGER)
            return token.value
        elif token.type == IDENTIFIER:
            self.consume(IDENTIFIER)
            if token.value in self.symboltable:
                result = self.symboltable.get(token.value)
                return result
            else:
                self.error("Variable not declared")
        elif token.type == STRING:
            self.consume(STRING)
            return token.value
        elif token.value == "(":
            self.consume(SYMBOL)
            result = self.compileExpression()
            self.consume(SYMBOL)
            return result
