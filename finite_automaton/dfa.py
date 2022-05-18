from terminaltables import AsciiTable

from finite_automaton.nfa import NFA

class DFA:
    @staticmethod
    def from_NFA(nfa):
        dfa = DFA()
        states = DFA.eliminate_indeterminism(nfa.states)
        for key, expression in states.items():
            dfa.states[DFA.index_to_production_name(key)] = {
                **expression,
                "productions": {non_terminal: DFA.index_to_production_name(terminal.pop())
                    for non_terminal, terminal in expression["productions"].items()
                }
            }

        return dfa

    @staticmethod
    def index_to_production_name(num):
        # Because S should be moved to the first index
        letters = ["S", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "T", "U", "V", "W", "Y", "Z"]

        index = num - 1
        size = len(letters)
        if index < size:
            return letters[index]
        else:
            rigth_letter = letters[index % size]
            left = DFA.index_to_production_name(index // size)
            return left + rigth_letter

    @staticmethod
    def format_productions(nfa):
        dfa = {}
        for index, item in nfa.items():
            productions = dict(zip(
                item["productions"].keys(),
                list(map(
                    lambda x: list(map(DFA.index_to_production_name, sorted(x))),
                    item["productions"].values()
                ))
            ))
                
            dfa[DFA.index_to_production_name(index)] = {
                **item,
                "productions": productions
            }
        return dfa

    @staticmethod
    def merge_productions(nfa, productions):
        new_production = {"productions": {}, "is_final": False}
        for key in productions:
            production = nfa[key]
            new_production["is_final"] |= production["is_final"]
            new_production["from"] = set(productions)

            for non_terminal, terminals in production["productions"].items():
                new_terminals = new_production["productions"].get(non_terminal, set())
                new_terminals = new_terminals.union(terminals)
                new_production["productions"][non_terminal] = new_terminals

        return new_production

    def search_production_rule(nfa, productions):
        for key, items in nfa.items():
            if items.get("from", False) == set(productions):
                return key
        return None

    def eliminate_indeterminism(nfa):
        dfa = nfa.copy()

        has_change = False
        for key, items in nfa.items():
            for non_terminal, terminals in items["productions"].items():
                if len(terminals) > 1:
                    has_change = True
                    production_rule = DFA.search_production_rule(dfa, terminals)
                    if production_rule:
                        dfa[key]["productions"][non_terminal] = {production_rule}
                    else:
                        last_key = sorted(dfa.keys()).pop() + 1
                        dfa[last_key] = DFA.merge_productions(dfa, terminals)
                        dfa[key]["productions"][non_terminal] = {last_key}

        if has_change:
            return DFA.eliminate_indeterminism(dfa)


        for key, items in nfa.items():
            if dfa[key].get("from"):
                del dfa[key]["from"]


        return NFA.remove_useless_expressions(dfa)

    def __init__(self):
        self.states = {}

    def asci_table(self):
        header = ['/']
        for index, expressions in self.states.items():
            for letter in expressions["productions"].keys():
                try:
                    header.index(letter)
                except ValueError:
                    header.append(letter)
        rows = [header]

        for index, expression in self.states.items():
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
