import re

gramar_regex = r"^<([A-Z]+)>\s*::=((\s*([a-zε]*)(<([A-Z])>)*([a-zε]*)\s*\|?)+)$"
production_regex = r"^\s*([a-zε]*)(<([A-Z]+)>)*([a-zε]*)\s*$"


def generate_grammar_sentence(word):
    grammar = {}
    for i, letter in enumerate(word):
        grammar[i + 1] = {
            "productions": {
                letter: {i + 2}
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
            productions[groups[0]].add(groups[2])
        except KeyError:
            productions[groups[0]] = {groups[2]}
    return {
        "productions": productions,
        "is_final": is_final
    }


def convert_non_terminals(productions, non_terminals):
    productions = productions.copy()
    for production, nterminals in productions.items():
        productions[production] = set(
            map(lambda nt: non_terminals.index(nt) + 1, nterminals))
    return productions


def remove_useless_expressions(grammar):
    filtered_grammar = {}
    used_expressions = {1}
    for expression in grammar.values():
        for non_terminals in expression["productions"].values():
            used_expressions = used_expressions.union(non_terminals)

    for index, expression in grammar.items():
        if index in used_expressions:
            filtered_grammar[index] = expression
        else:
            continue

    return filtered_grammar

def get_alive_expressions(grammar):
    ending_expressions = []
    for index, expression in grammar.items():
        if (expression["is_final"]):
            ending_expressions.append(index)

    new_ending_found = True
    while (new_ending_found):
        new_ending_found = False
        for index, expression in grammar.items():
            if (index in ending_expressions):
                continue

            for letter, non_terminals in expression["productions"].items():
               intersection = set(ending_expressions) & set(non_terminals)
               if len(intersection):
                   ending_expressions.append(index)
                   new_ending_fround = True

    return set(ending_expressions)


def remove_dead_expressions(grammar):
    alive_expressions = get_alive_expressions(grammar)
    filtered_grammar = {}

    for index, expression in grammar.items():
        if index not in alive_expressions:
            continue
        
        productions = {}
        for i, non_terminals in expression["productions"].items():
            filtered = set(filter(lambda x: x in alive_expressions, non_terminals))
            if len(filtered):
                productions[i] = filtered
        
        expression["productions"] = productions
        filtered_grammar[index] = expression

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
    grammar = remove_dead_expressions(grammar)

    return grammar


def is_expression(raw):
    return bool(re.match(gramar_regex, raw))      


def is_sentence(raw):
    return not is_expression(raw)
