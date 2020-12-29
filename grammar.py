import re

gramar_regex = r"^<([A-Z]+)>\s*::=((\s*([a-zε]*)(<([A-Z])>)*([a-zε]*)\s*\|?)+)$"
production_regex = r"^\s*([a-zε]*)(<([A-Z]+)>)*([a-zε]*)\s*$"


def generate_grammar_for_sentence(word):
    grammar = {}
    for i, letter in enumerate(word):
        grammar[i + 1] = [[letter, i + 2]]
    grammar[len(word)+1] = []
    grammar["final"] = len(word)+1
    return grammar


def get_non_terminals(lines):
    non_terminals = []
    for line in lines:
        groups = re.search(gramar_regex, line).groups()
        non_terminals.append(groups[0])
    return non_terminals


def generate_expression(line):
    productions_raw = re.search(gramar_regex, line).group(2).split("|")
    productions = []
    is_final = False
    for raw in productions_raw:
        groups = re.search(production_regex, raw).groups()
        if (groups[0] == "ε"):
            is_final = True
            continue
        productions.append([groups[0], groups[2]])
    return {
        "productions": productions,
        "is_final": is_final
    }


def convert_non_terminals(productions, non_terminals):
    return list(map(lambda p: [p[0], non_terminals.index(p[1]) + 1], productions))


def generate_grammar(lines):
    non_terminals = get_non_terminals(lines)
    grammar = {}
    for line in lines:
        name = re.search(gramar_regex, line).group(1)
        expression = generate_expression(line)
        formated_production = convert_non_terminals(
            expression["productions"], non_terminals)
        name_number = non_terminals.index(name)+1
        grammar[name_number] = formated_production
        if (expression["is_final"]):
            grammar["final"] = name_number

    return grammar
