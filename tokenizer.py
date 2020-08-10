import tokenize
from io import StringIO

KEYWORDS = ["IF","LET","PRINT","GOTO","FOR","THEN","NEXT","ELSE"]
INTEGER,SYMBOL, STRING, KEYWORD,IDENTIFIER = "INTEGER", "SYMBOL", "STRING", "KEYWORD", "IDENTIFIER"

class Token():
    def __init__(self, val, type):
        self.value = val
        self.type = type

def mytokenize(text):
    """ Why reinvent the wheel.
    Borrow the tokeniser logic from Python and modify the output to be a list of my own token objects"""
    tokens = tokenize.generate_tokens(StringIO(text).readline)
    toklist = []
    for tok in tokens:
        if tok.type == tokenize.NUMBER:
            toklist.append(Token(int(tok.string), "INTEGER"))
        elif tok.type == tokenize.OP:
            toklist.append(Token(tok.string, "SYMBOL"))
        elif tok.type == tokenize.STRING:
            toklist.append(Token(tok.string[1:-1], "STRING"))
        elif tok.type == tokenize.NAME:
            if tok.string.upper() in KEYWORDS:
                toklist.append(Token(tok.string.upper(), "KEYWORD"))
            else:
                toklist.append(Token(tok.string, "IDENTIFIER"))
        elif tok.type in [tokenize.NEWLINE, tokenize.ENDMARKER]:
            toklist.append(Token(tok.string, "EOF"))
            break
    return toklist



