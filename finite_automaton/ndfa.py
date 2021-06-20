from terminaltables import AsciiTable

def add_grammar(ndfa, grammar):
    ndfa = ndfa.copy()
    grammar = grammar.copy()
    first = grammar[1]
    del grammar[1]

    try:
        shift = sorted(ndfa.keys()).pop() - 1
    except IndexError:
        shift = 0

    try:
        ndfa[1]["is_final"] |= first["is_final"]

        for letter, non_terminals in first["productions"].items():
            non_terminals = set(map(lambda x: x + shift, non_terminals))
            productions = ndfa[1]["productions"]
            try:
                productions[letter] = productions[letter].union(non_terminals)
            except KeyError:
                productions[letter] = non_terminals
    except KeyError:
        ndfa[1] = first

    for index, expression in grammar.items():
        for letter, non_terminals in expression["productions"].items():
            expression["productions"][letter] = set(
                map(lambda x: x + shift, non_terminals))
        ndfa[index + shift] = expression

    return ndfa


def generate_NDFA(grammars):
    ndfa = {}
    for grammar in grammars:
        ndfa = add_grammar(ndfa, grammar)

    return ndfa


def NDFA_table(ndfa):
    header = ['/']
    for index, expressions in ndfa.items():
        for letter in expressions["productions"].keys():
            try:
                header.index(letter)
            except ValueError:
                header.append(letter)
    rows = [header]

    for index, expression in ndfa.items():
        row = []
        for column in header:
            if column == '/':
                row.append(
                (chr(index + 63) if index != 1 else "S") + (
                    "*" if expression["is_final"] else ""
                ))
                continue

            try:
                row.append(", ".join([chr(i + 63) for i in expression["productions"][column]]))
            except KeyError:
                row.append('-')
        rows.append(row)

    return AsciiTable(rows).table
        

    
