from terminaltables import AsciiTable
import re

class NDFA:
    GRAMMAR_REGEX = r"^<([A-Z]+)>\s*::=((\s*([a-zε]*)(<([A-Z])>)*([a-zε]*)\s*\|?)+)$"
    TOKEN_REGEX = r"^\s*([a-zε]*)(<([A-Z]+)>)*([a-zε]*)\s*$"

    def __init__(self):
        self.states = {}
    

    @staticmethod
    def from_token(word):
        ndfa = NDFA()
        for i, letter in enumerate(word):
            ndfa.states[i + 1] = {
                "productions": {
                    letter: {i + 2}
                },
                "is_final": False
            }
        ndfa.states[len(word)+1] = {
            "productions": {},
            "is_final": True
        }

        return ndfa

    @staticmethod
    def from_grammar(lines):
        non_terminals = NDFA.get_non_terminals(lines)
        ndfa = NDFA()
        for line in lines:
            name = re.search(NDFA.GRAMMAR_REGEX, line).group(1)
            expression = NDFA.generate_expression(line)
            expression["productions"] = NDFA.convert_non_terminals(
                expression["productions"], non_terminals)
            name_number = non_terminals.index(name)+1
            ndfa.states[name_number] = expression

        ndfa.states = NDFA.remove_useless_expressions(ndfa.states)
        ndfa.states = NDFA.remove_dead_expressions(ndfa.states)

        return ndfa

    @staticmethod
    def generate_expression(line):
        productions_raw = re.search(NDFA.GRAMMAR_REGEX, line).group(2).split("|")
        productions = {}
        is_final = False
        for raw in productions_raw:
            groups = re.search(NDFA.TOKEN_REGEX, raw).groups()
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

    @staticmethod
    def get_non_terminals(lines):
        non_terminals = []
        for line in lines:
            groups = re.search(NDFA.GRAMMAR_REGEX, line).groups()
            non_terminals.append(groups[0])
        return non_terminals

    @staticmethod
    def convert_non_terminals(productions, non_terminals):
        productions = productions.copy()
        for production, nterminals in productions.items():
            productions[production] = set(
                map(lambda nt: non_terminals.index(nt) + 1, nterminals))
        return productions


    @staticmethod
    def remove_useless_expressions(grammar):
        filtered_grammar = {}
        used_expressions = {1}
        original_values = grammar.values()

        for expression in original_values:
            for non_terminals in expression["productions"].values():
                used_expressions = used_expressions.union(non_terminals)

        for index, expression in grammar.items():
            if index in used_expressions:
                filtered_grammar[index] = expression
            else:
                continue

        if len(original_values) != len(filtered_grammar.values()):
            return NDFA.remove_useless_expressions(filtered_grammar)

        return filtered_grammar

    @staticmethod
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

                for non_terminals in expression["productions"].values():
                    intersection = set(ending_expressions) & set(non_terminals)
                    if len(intersection):
                        ending_expressions.append(index)
                        new_ending_found = True

        return set(ending_expressions)


    @staticmethod
    def remove_dead_expressions(grammar):
        alive_expressions = NDFA.get_alive_expressions(grammar)
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


    @staticmethod
    def is_expression(raw):
        return bool(re.match(NDFA.GRAMMAR_REGEX, raw))      


    @staticmethod
    def is_sentence(raw):
        return not NDFA.is_expression(raw)

    def add_grammar(self, grammar):
        first = grammar[1]
        del grammar[1]

        try:
            shift = sorted(self.states.keys()).pop() - 1
        except IndexError:
            shift = 0

        try:
            self.states[1]["is_final"] |= first["is_final"]

            for letter, non_terminals in first["productions"].items():
                non_terminals = set(map(lambda x: x + shift, non_terminals))
                productions = self.states[1]["productions"]
                try:
                    productions[letter] = productions[letter].union(non_terminals)
                except KeyError:
                    productions[letter] = non_terminals
        except KeyError:
            self.states[1] = first

        for index, expression in grammar.items():
            for letter, non_terminals in expression["productions"].items():
                expression["productions"][letter] = set(
                    map(lambda x: x + shift, non_terminals))
            self.states[index + shift] = expression

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