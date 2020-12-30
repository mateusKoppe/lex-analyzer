from terminaltables import AsciiTable

def add_grammar(_ndfa, _grammar):
    ndfa = _ndfa.copy()
    grammar = _grammar.copy()
    final = grammar["final"]
    del grammar["final"]
    first = grammar[1]
    del grammar[1]

    try:
        shift = sorted(ndfa.keys()).pop() - 1
    except IndexError:
        shift = 0

    try:
        ndfa[1]
    except KeyError:
        ndfa[1] = {
            "productions": {},
            "is_final": False
        }

    for expression in first:
        leter = expression[0]
        non_terminal = expression[1]
        try:
            ndfa[1]["productions"][leter].append(non_terminal + shift)
        except KeyError:
            ndfa[1]["productions"][leter] = [non_terminal + shift]

    try:
        if (final == 1):
            ndfa[1]["is_final"] = True
    except KeyError:
        pass

    for index, expressions in grammar.items():
        ndfa[index + shift] = {
            "productions": {},
            "is_final": final == index
        }
        for expression in expressions:
            leter = expression[0]
            non_terminal = expression[1]
            try:
                ndfa[index +
                     shift]["productions"][leter].append(non_terminal + shift)
            except KeyError:
                ndfa[index + shift]["productions"][leter] = [non_terminal + shift]

    return ndfa


def generate_NDFA(grammars):
    ndfa = {}
    for grammar in grammars:
        ndfa = add_grammar(ndfa, grammar)

    return ndfa


def NDFA_table(ndfa):
    header = ['/']
    for index, expressions in ndfa.items():
        for letter, non_terminals in expressions["productions"].items():
            try:
                letterIndex = header.index(letter)
            except ValueError:
                header.append(letter)
    rows = [header]

    for index, expression in ndfa.items():
        row = []
        for column in header:
            if column == '/':
                row.append(chr(index + 64) + (
                    "*" if expression["is_final"] else ""
                ))
                continue

            try:
                row.append(", ".join([chr(i + 64) for i in expression["productions"][column]]))
            except KeyError:
                row.append('')
        rows.append(row)

    return AsciiTable(rows).table
        

    