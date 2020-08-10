import tokenizer
from interpreter import Interpreter

ST = {}


def parse(text, i):
    # tokenize source stream
    source = tokenizer.mytokenize(text)
    #interpret token code
    return i.compileStatement(source)



def repl():
    print('PyBasic v0.1 (c) 2020 Gently Solutions Ltd')
    print('Type "exit" to quit.')
    i = Interpreter()
    while True:
        try:
            source = input("> ")
            if source.upper() == "EXIT":
                break
            try:
                parse(source, i)
            except SyntaxError as e:
                print(e)
        except (RuntimeError, IndexError) as e:
            print("IndexError: %s" % e)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")

if __name__ == '__main__':
    repl()