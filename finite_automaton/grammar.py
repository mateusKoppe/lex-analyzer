import re

gramar_regex = r"^<([A-Z]+)>\s*::=((\s*([a-zε]*)(<([A-Z])>)*([a-zε]*)\s*\|?)+)$"
production_regex = r"^\s*([a-zε]*)(<([A-Z]+)>)*([a-zε]*)\s*$"


def generate_grammar_sentence(word):
    grammar = {}
    for i, letter in enumerate(word):
        grammar[i + 1] = {
            "productions": {
                letter: [i + 2]
            },
            "is_final": False
        }
    grammar[len(word)+1] = {
        "productions": {},
        "is_final": True
    }
    return grammar


def get_non_terminals(lines):
    non_terminals = []
    for line in lines:
        groups = re.search(gramar_regex, line).groups()
        non_terminals.append(groups[0])
    return non_terminals


def generate_expression(line):
    productions_raw = re.search(gramar_regex, line).group(2).split("|")
    productions = {}
    is_final = False
    for raw in productions_raw:
        groups = re.search(production_regex, raw).groups()
        if (groups[0] == "ε"):
            is_final = True
            continue
        try:
            productions[groups[0]].append(groups[2])
        except KeyError:
            productions[groups[0]] = [groups[2]]
    return {
        "productions": productions,
        "is_final": is_final
    }


def convert_non_terminals(productions, non_terminals):
    productions = productions.copy()
    for production, nterminals in productions.items():
        productions[production] = list(
            map(lambda nt: non_terminals.index(nt) + 1, nterminals))
    return productions


def remove_useless_expressions(grammar):
    filtered_grammar = {}
    used_expressions = [1]
    for expression in grammar.values():
        for non_terminals in expression["productions"].values():
            for non_terminal in non_terminals:
                try:
                    used_expressions.index(non_terminal)
                except ValueError:
                    used_expressions.append(non_terminal)

    for index, expression in grammar.items():
        try:
            used_expressions.index(index)
            filtered_grammar[index] = expression
        except ValueError:
            continue

    return filtered_grammar

def generate_grammar_expression(lines):
    non_terminals = get_non_terminals(lines)
    grammar = {}
    for line in lines:
        name = re.search(gramar_regex, line).group(1)
        expression = generate_expression(line)
        expression["productions"] = convert_non_terminals(
            expression["productions"], non_terminals)
        name_number = non_terminals.index(name)+1
        grammar[name_number] = expression

    grammar = remove_useless_expressions(grammar)

    return grammar


def is_expression(raw):
    return bool(re.match(gramar_regex, raw))      


def is_sentence(raw):
    return not is_expression(raw)
