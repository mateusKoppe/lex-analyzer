from terminaltables import AsciiTable
from finite_automaton.grammar import remove_useless_expressions

def index_to_production_name(num):
    # Because S should be moved to the first index
    letters = ["S", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "T", "U", "V", "W", "Y", "Z"]

    index = num - 1
    size = len(letters)
    if index < size:
        return letters[index]
    else:
        rigth_letter = letters[index % size]
        left = index_to_production_name(index // size)
        return left + rigth_letter

def format_productions(ndfa):
    dfa = {}
    for index, item in ndfa.items():
        productions = dict(zip(
            item["productions"].keys(),
            list(map(
                lambda x: list(map(index_to_production_name, sorted(x))),
                item["productions"].values()
            ))
        ))
            
        dfa[index_to_production_name(index)] = {
            **item,
            "productions": productions
        }
    return dfa

def merge_productions(ndfa, productions):
    new_production = {"productions": {}, "is_final": False}
    for key in productions:
        production = ndfa[key]
        new_production["is_final"] |= production["is_final"]
        new_production["from"] = set(productions)

        for non_terminal, terminals in production["productions"].items():
            new_terminals = new_production["productions"].get(non_terminal, set())
            new_terminals = new_terminals.union(terminals)
            new_production["productions"][non_terminal] = new_terminals

    return new_production

def search_production_rule(ndfa, productions):
    for key, items in ndfa.items():
        if items.get("from", False) == set(productions):
            return key
    return None

def eliminate_indeterminism(ndfa):
    dfa = ndfa.copy()

    has_change = False
    for key, items in ndfa.items():
        for non_terminal, terminals in items["productions"].items():
            if len(terminals) > 1:
                has_change = True
                production_rule = search_production_rule(dfa, terminals)
                if production_rule:
                    dfa[key]["productions"][non_terminal] = {production_rule}
                else:
                    last_key = sorted(dfa.keys()).pop() + 1
                    dfa[last_key] = merge_productions(dfa, terminals)
                    dfa[key]["productions"][non_terminal] = {last_key}

    if has_change:
        return eliminate_indeterminism(dfa)


    for key, items in ndfa.items():
        if dfa[key].get("from"):
            del dfa[key]["from"]

    return remove_useless_expressions(dfa)


def generate_DFA(ndfa):
    dfa = eliminate_indeterminism(ndfa)
    formated_dfa = {}
    for key, expression in dfa.items():
        formated_dfa[index_to_production_name(key)] = {
            **expression,
            "productions": {non_terminal: index_to_production_name(terminal.pop())
                for non_terminal, terminal in expression["productions"].items()
            }
        }

    return formated_dfa

def DFA_table(dfa):
    header = ['/']
    for index, expressions in dfa.items():
        for letter in expressions["productions"].keys():
            try:
                header.index(letter)
            except ValueError:
                header.append(letter)
    rows = [header]

    for index, expression in dfa.items():
        row = []
        for column in header:
            if column == '/':
                row.append(index + ("*" if expression["is_final"] else ""))
                continue

            try:
                row.append(expression["productions"][column])
            except KeyError:
                row.append('-')
        rows.append(row)

    return AsciiTable(rows).table
