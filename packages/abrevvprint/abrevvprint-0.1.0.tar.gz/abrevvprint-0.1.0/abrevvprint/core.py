 # t ==all lang== Print ==all lang== t #
def p(msg, opcionalArg="", opcionalArg2=""):
    if opcionalArg != "":
        if opcionalArg2 != "":
            print(msg, opcionalArg, opcionalArg2)
        else:
            print(msg, opcionalArg)
    else:
        print(msg)
# t ==ptBr== Print com formatação ==ptBr== t #
# t ==enUs== Print with format ==enUs== t #
def pf(msg, opcionalArg="", opcionalArg2=""):
    if opcionalArg != "":
        if opcionalArg2 != "":
            print(f"{msg}", opcionalArg, opcionalArg2)
        else:
            print(f"{msg}", opcionalArg)
    else:
        print(f"{msg}")

# t ==ptBr== Print de erro ==ptBr== t #
# t ==enUs== Error print ==enUs== t #
def pe(msg, opcionalArg="", opcionalArg2=""):
    if opcionalArg != "":
        if opcionalArg2 != "":
            print(f"Error: {msg}, {opcionalArg}, {opcionalArg2}")
        else:
            print(f"Error: {msg}, {opcionalArg}")
    else:
        print(f"Error: {msg}")