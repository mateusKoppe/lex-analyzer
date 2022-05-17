from collections import deque
from typing import Dict, List
import re
from terminaltables import AsciiTable

from finite_automaton.state import State

class NDFA:
    @classmethod
    def from_token(cls, word: str):
        ndfa = cls()
        
        state_final = State(word.upper())
        last_created_state = state_final
        created = 1
        for letter in reversed(word):
            ndfa.add_state(last_created_state)
            name = f"{word.upper()}_{len(word) - created}"
            state = State(name, False)
            state.add_transition(letter, last_created_state.name)
            last_created_state = state
            
            created += 1

        ndfa.start_grammar(last_created_state)

        return ndfa

    @classmethod
    def from_grammar(cls, lines: List[str]):
        ndfa = cls()
        
        lines_deque = deque(lines)

        initial_state = State.from_raw(lines_deque.popleft())
        ndfa.start_grammar(initial_state)

        for line in lines_deque:
            state = State.from_raw(line)
            ndfa.add_state(state)

        ndfa.remove_endless_expressions()

        return ndfa

    def get_ended_expressions(self):
        ending_expressions = set([state.name for state in self.states.values() if state.is_final])

        new_ending_found = True
        while (new_ending_found):
            new_ending_found = False
            for index, state in self.states.items():
                if (index in ending_expressions):
                    continue

                for non_terminals in state.transitions.values():
                    intersection = set(ending_expressions) & set(non_terminals)
                    if len(intersection):
                        ending_expressions.add(index)
                        new_ending_found = True

        return ending_expressions


    def remove_endless_expressions(self):
        states = set(self.states.keys())
        dead_states = states - self.get_ended_expressions()
        
        for dead_state in dead_states:
            self.forget_state(dead_state)

    def forget_state(self, dead_state: str):
        del self.states[dead_state]
        for state in self.states.values():
            state.forget_state(dead_state)


    @staticmethod
    def is_expression(raw):
        return bool(re.match(State.GRAMMAR_REGEX, raw))      


    @staticmethod
    def is_sentence(raw):
        return not NDFA.is_expression(raw)

    def __init__(self):
        self.initial_state = None
        self.states: Dict[str, State] = {} 

    def start_grammar(self, state: State):
        state.name = "START"
        self.add_state(state)
        self.initial_state = state

    def add_state(self, state: State):
        if state.name in self.states:
            raise Exception(f"State {state.name} already exist")

        self.states[state.name] = state

    def add_transition(self, from_state: str, to_state: str, terminal: str):
        self.states[from_state].add_transition(terminal, to_state)

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