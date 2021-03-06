"""
Interpreter.py

"""
from tokenizer import Tokentype, Lexer
import pickle
import random
import os

SYMBOLS = (
    Tokentype.PLUS,
    Tokentype.MINUS,
    Tokentype.EQUALS,
    Tokentype.GT,
    Tokentype.GTE,
    Tokentype.LT,
    Tokentype.LTE,
    Tokentype.NE,
)


class Loop:
    def __init__(self, start, end, line, step=1):
        self.start = start
        self.end = end
        self.line = line
        self.step = step


class Interpreter:

    def __init__(self):
        self.symboltable = {}
        self.looptable = {}
        self.token_stream = None
        self.current_token = None
        self.position = 0  #
        self.result = None
        self.program = {}
        self.lexer = Lexer()
        self.debug = False
        self.steps = []
        self.linepos = 0

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

    def interpret(self):
        self.position = 0
        self.advance()
        self.compileStatement()

    def execute(self, text):
        # tokenize source stream
        self.token_stream = self.lexer.tokenize(text)
        # interpret token streamlist
        self.interpret()
        print("SYMBOL TABLE {}".format(self.symboltable)) if self.debug else False
        print("LOOP TABLE {}".format(self.looptable)) if self.debug else False
        # print("Program {}".format(self.program)) if self.debug else False

    def run(self):
        self.steps = sorted(self.program.keys())
        self.linepos = 0
        print("Program steps {}".format(self.steps)) if self.debug else False
        try:
            while self.linepos < len(self.steps):
                code = self.program.get(self.steps[self.linepos])
                print("Current line := {} Code to execute := {}".format(self.linepos, code)) if self.debug else False
                self.execute(code)
                self.linepos += 1
        except KeyboardInterrupt:
            print("** BREAK **")

    # ######################### processing methods ##################################
    def compileStatement(self):
        # statement ( : statement )*
        # letStatement|ifStatement|whileStatement|InputStatement|LIST
        self.result = None
        val = self.current_token.value
        if val == "LET":
            self.consume(Tokentype(val))
            self.compileLet()
        elif val == "PRINT":
            self.consume(Tokentype(val))
            self.compilePrint()
        elif val == "IF":
            self.consume(Tokentype(val))
            self.compileIf()
        elif val == "INPUT":
            self.consume(Tokentype(val))
            self.compileInput()
        elif val == "LIST":
            self.consume(Tokentype(val))
            self.compileList()
        elif val == "FOR":
            self.consume(Tokentype(val))
            self.compileFor()
        elif val == "NEXT":
            self.consume(Tokentype(val))
            self.compileNext()
        elif val == "RUN":
            self.consume(Tokentype(val))
            self.run()
        elif val == "GOTO":
            self.consume(Tokentype(val))
            self.compileGoto()
        elif val == "NEW":
            self.consume(Tokentype(val))
            self.steps = []
            self.linepos = 0
            self.program = self.symboltable = self.looptable = {}
        elif val == "CLEAR":
            self.consume(Tokentype(val))
            self.symboltable = self.looptable = {}
        elif val == "LOAD":
            self.consume(Tokentype(val))
            name = self.current_token.value
            self.consume(Tokentype.STRING)
            with open(name + ".bas", 'rb') as readfile:
                self.program = pickle.load(readfile)
                self.steps = []
                self.linepos = 0
        elif val == "SAVE":
            self.consume(Tokentype(val))
            name = self.current_token.value
            self.consume(Tokentype.STRING)
            with open(name + ".bas", 'wb') as writefile:
                pickle.dump(self.program, writefile)
        elif val == "REM":
            pass  # do nothing ignore remarks
        elif val == "DIM":
            self.consume(Tokentype(val))
            self.compileDim()
        elif val == "?":
            self.consume(Tokentype.DEBUG)
            print("Symbol Table {}".format(self.symboltable))
            print("Loop Table {}".format(self.looptable))
        else:
            self.error()
        while self.current_token.type != Tokentype.COLON and self.current_token.type != Tokentype.EOF:
            self.advance()
        if self.current_token.type == Tokentype.COLON:
            self.consume(Tokentype.COLON)
            self.compileStatement()

    def compileLet(self):
        # 'let' Identifier ('['expression']')? '=' expression ';'
        name = self.current_token.value
        pos = 0
        self.consume(Tokentype.IDENTIFIER)
        while self.current_token.type == Tokentype.LBRACK:
            self.consume(Tokentype.LBRACK)
            pos = self.compileExpression()
            self.consume(Tokentype.RBRACK)
        self.consume(Tokentype.EQUALS)
        result = self.compileExpression()
        if name in self.symboltable:
            items = self.symboltable.get(name)
        else:
            items = [0]  # create a list to manipulate
        if pos < len(items):
            items[pos] = result
        else:
            raise self.error("Subscript out of range")
        self.symboltable.update({name: items})

    def compileDim(self):
        # 'dim' Identifier '[' expression ']'
        name = self.current_token.value
        self.consume(Tokentype.IDENTIFIER)
        self.consume(Tokentype.LBRACK)
        result = self.compileExpression()
        self.consume(Tokentype.RBRACK)
        var = [0 for i in range(result)]
        self.symboltable.update({name: var})

    def compilePrint(self):
        # 'print'  expression (';' expression )*
        result = self.compileExpression()
        string = str(result)
        while self.current_token.value == ";":
            self.consume(Tokentype.SEMI)
            result = self.compileExpression()
            string += str(result)
        print(string if string else "")

    def compileIf(self):
        # 'IF' expr 'THEN' statement* ( 'ELSE' statement*) 'ENDIF'
        result = self.compileExpression()
        if result is True:
            self.consume(Tokentype.THEN)
            self.compileStatement()
        else:
            while self.current_token.type != Tokentype.ELSE and self.current_token.type != Tokentype.EOF:
                self.advance()
            if self.current_token.type == Tokentype.ELSE:
                self.consume(Tokentype.ELSE)
                self.compileStatement()

    def compileFor(self):
        # FOR identifier "=" expr "TO" expr (STEP expr)?
        name = self.current_token.value
        self.consume(Tokentype.IDENTIFIER)
        self.consume(Tokentype.EQUALS)
        e1 = self.compileExpression()
        self.consume(Tokentype.TO)
        e2 = self.compileExpression()
        step = 1  # default to 1, override if step is set
        while self.current_token.type == Tokentype.STEP:
            self.consume(Tokentype.STEP)
            step = self.compileExpression()
        if name not in self.looptable:
            self.symboltable.update({name: [e1]})
            self.looptable.update({name: Loop(e1, e2, self.linepos, step)})

    def compileNext(self):
        # Next identifier
        name = self.current_token.value
        self.consume(Tokentype.IDENTIFIER)
        if name in self.looptable:
            loop = self.looptable.get(name)
            val = self.symboltable.get(name)
            if val[0] < loop.end:
                self.symboltable.update({name: [val[0] + loop.step]})
                self.linepos = loop.line - 1  # deduct one to account for increment after execution
            else:
                self.looptable.pop(name)
        else:
            self.error("NEXT without FOR")

    def compileList(self):
        for lineno, code in sorted(self.program.items()):
            print("{} {}".format(lineno, code))

    def compileInput(self):
        # 'input' (prompt string) identifier
        prompt = "?"
        while self.current_token.type == Tokentype.STRING:
            prompt = self.compileFactor()
        name = self.current_token.value
        self.consume(Tokentype.IDENTIFIER)
        result = input(prompt)
        # a hack to cast numbers if the 1st char is a digit
        result = int(result) if result[0].isdigit() else result
        self.symboltable.update({name: result})

    def compileGoto(self):
        # 'goto' linenumber
        token = self.current_token
        self.consume(Tokentype.INTEGER)
        if token.value in self.steps:
            # reset linepos
            self.linepos = self.steps.index(
                token.value) - 1  # remove 1 to account for increment instruction after the goto is executed
        else:
            self.error("Line number does not exist")

    def compileExpression(self):
        # expression: term ( +|-|=|<|>|>=|<=|<> term)*
        result = self.compileTerm()
        while self.current_token.type in SYMBOLS:
            if self.current_token.type == Tokentype.PLUS:
                self.consume(Tokentype.PLUS)
                result += self.compileTerm()
            elif self.current_token.type == Tokentype.MINUS:
                self.consume(Tokentype.MINUS)
                result -= self.compileTerm()
            elif self.current_token.type == Tokentype.EQUALS:
                self.consume(Tokentype.EQUALS)
                return True if result == self.compileTerm() else False
            elif self.current_token.type == Tokentype.GT:
                self.consume(Tokentype.GT)
                return True if result > self.compileTerm() else False
            elif self.current_token.type == Tokentype.GTE:
                self.consume(Tokentype.GTE)
                return True if result >= self.compileTerm() else False
            elif self.current_token.type == Tokentype.LT:
                self.consume(Tokentype.LT)
                return True if result < self.compileTerm() else False
            elif self.current_token.type == Tokentype.LTE:
                self.consume(Tokentype.LTE)
                return True if result <= self.compileTerm() else False
            elif self.current_token.type == Tokentype.NE:
                self.consume(Tokentype.NE)
                return True if result != self.compileTerm() else False
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
        # factor: integer | identifier ('['expr']')? | string | (expr) | RND '(' integer ')'
        token = self.current_token
        if token.type == Tokentype.INTEGER:
            self.consume(Tokentype.INTEGER)
            return token.value
        elif token.type == Tokentype.RND:
            self.consume(Tokentype.RND)
            self.consume(Tokentype.LPAREN)
            token = self.current_token
            self.consume(Tokentype.INTEGER)
            val = token.value
            self.consume(Tokentype.RPAREN)
            return random.randint(1, val)
        elif token.type == Tokentype.IDENTIFIER:
            pos = 0
            self.consume(Tokentype.IDENTIFIER)
            while self.current_token.type == Tokentype.LBRACK:
                self.consume(Tokentype.LBRACK)
                pos = self.compileExpression()
                self.consume(Tokentype.RBRACK)
            if token.value in self.symboltable:
                items = self.symboltable.get(token.value)
                if pos < len(items):
                    return items[pos]
                else:
                    raise self.error("Subscript out of range")
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
