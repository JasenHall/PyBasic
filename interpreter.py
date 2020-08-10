SYMBOLS = ["+", "-", "*", "/", "="]

from tokenizer import Tokentype

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
        if self.current_token.type == content:
            self.advance()
        else:
            self.error()

    def error(self, msg="Syntax Error"):
        raise SyntaxError(msg)

    def advance(self):
        if self.position < len(self.token_stream):
            self.current_token = self.token_stream[self.position]
            self.position += 1

    def interpret(self, code):
        self.token_stream = code
        self.position = 0
        self.advance()
        self.compileStatement()

    # ######################### processing methods ##################################
    def compileStatement(self):
        # statement*
        # letStatement|ifStatement|whileStatement
        self.result = None
        val = self.current_token.value
        self.consume(Tokentype(val))
        if val  == "LET":
            self.compileLet()
        elif val == "PRINT":
            self.compilePrint()
        elif val == "IF":
            self.compileIf()


    def compileLet(self):
        # 'let' Identifier ('['expression']')? '=' expression ';'
        name = self.current_token.value
        self.consume(Tokentype.IDENTIFIER)
        self.consume(Tokentype.EQUALS)
        result = self.compileExpression()
        self.symboltable.update({name: result})

    def compilePrint(self):
        # 'print'  expression (';' expression )*
        result = self.compileExpression()
        string = result
        while self.current_token.value == ";":
            self.consume(Tokentype.SEMI)
            result = self.compileExpression()
            string += result
        print(string if string else "")

    def compileIf(self):
        # 'IF' expr 'THEN' statement* ( 'ELSE' statement*) 'ENDIF'
        result = self.compileExpression()
        if result == True:
            self.consume(Tokentype.THEN)
            self.compileStatement()
        else:
            while self.current_token.type == Tokentype.ELSE:
                self.consume(Tokentype.ELSE)
                self.compileStatement()

    def compileExpression(self):
        # expression: term ( (PLUS|MINUS|=|<|>) term)*
        result = self.compileTerm()
        while self.current_token.type in (Tokentype.PLUS, Tokentype.MINUS, Tokentype.EQUALS):
            if self.current_token.type == Tokentype.PLUS:
                self.consume(Tokentype.PLUS)
                result += self.compileTerm()
            elif self.current_token.type == Tokentype.MINUS:
                self.consume(Tokentype.MINUS)
                result -= self.compileTerm()
            elif self.current_token.type == Tokentype.EQUALS:
                self.consume(Tokentype.EQUALS)
                result2 = self.compileTerm()
                return True if result == result2 else False
        return result

    def compileTerm(self):
        # term: factor ( (MUL|DIV) factor)*
        result = self.compileFactor()
        while self.current_token.type in (Tokentype.MUL, Tokentype.DIV):
            if self.current_token.type == Tokentype.MUL:
                self.consume(Tokentype.MUL)
                result *= self.compileFactor()
            elif self.current_token.type == Tokentype.DIV:
                self.consume(Tokentype.DIV)
                result /= self.compileFactor()
        return result

    def compileFactor(self):
        # factor: integer | identifier | string | (expr)
        token = self.current_token
        if token.type == Tokentype.INTEGER:
            self.consume(Tokentype.INTEGER)
            return token.value
        elif token.type == Tokentype.IDENTIFIER:
            self.consume(Tokentype.IDENTIFIER)
            if token.value in self.symboltable:
                result = self.symboltable.get(token.value)
                return result
            else:
                self.error("Variable not declared")
        elif token.type == Tokentype.STRING:
            self.consume(Tokentype.STRING)
            return token.value
        elif token.type == Tokentype.LPAREN:
            self.consume(Tokentype.LPAREN)
            result = self.compileExpression()
            self.consume(Tokentype.RPAREN)
            return result
