from interpreter import Interpreter
import re


def repl():
    print('PyBasic v0.3 (c) 2020 Gently Solutions Ltd')
    print('Type "exit" to quit.')
    i = Interpreter()
    while True:
        source = input("> ")
        if source.upper() == "EXIT":
            break
        if source.upper() == "DEBUG ON":
            print("Debug flag turned on.")
            i.debug = True
            continue
        if source.upper() == "DEBUG OFF":
            print("Debug flag turned off.")
            i.debug = False
            continue
        regex = re.compile('^[0-9]+')
        result = regex.match(source)
        if result:
            lineno = int(result.group())
            code = source[result.end():]
            if code == "":
                i.program.pop(lineno, -1)  # delete code line
            else:
                # todo - think about how to process code before storing
                # should it be parsed and tokenized and grammatically checked ?
                i.program.update({lineno: code})  # insert plain code line
        else:
            try:
                i.execute(source)
            except IndexError as e:
                pass
            except SyntaxError as e:
                print(e)


if __name__ == '__main__':
    repl()
