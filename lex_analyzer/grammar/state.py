from __future__ import annotations
from os import stat
from typing import Dict, Set
import re

class StateIndeterministicRuleError(Exception):
    pass

class State:
    GRAMMAR_REGEX = r"^<([A-Z_]+)>\s*::=((\s*([a-zε]*)(<([A-Z_]+)>)*([a-zε]*)\s*\|?)+)$"
    TOKEN_REGEX = r"^\s*([a-zε]*)(<([A-Z_]+)>)*([a-zε]*)\s*$"

    @classmethod
    def from_raw(cls, line):
        name = re.search(cls.GRAMMAR_REGEX, line).group(1)
        state = cls(name)
        productions_raw = re.search(cls.GRAMMAR_REGEX, line).group(2).split("|")
        for raw in productions_raw:
            groups = re.search(cls.TOKEN_REGEX, raw).groups()
            if (groups[0] == "ε"):
                state.final_token = state.name
                continue

            state.add_transition(groups[0], groups[2])

        return state

    def __init__(self, name: str, final_token: str = None) -> None:
        self.name = name
        self.final_token = final_token
        self.transitions: Dict[str, Set[str]] = {}

    def add_transition(self, terminal: str, next_state: str):
        try:
            self.transitions[terminal].add(next_state)
        except KeyError:
            self.transitions[terminal] = { next_state }

    def add_deterministic_transition(self, terminal: str, next_state: str):
        if terminal in self.transitions:
            raise StateIndeterministicRuleError(f"transition to {terminal} already determined")
            
        self.add_transition(terminal, next_state)

    def set_transition(self, terminal: str, next_state: str):
        self.transitions[terminal] = { next_state }

    def get_transitions_by(self, terminal: str):
        try:
            return self.transitions[terminal]
        except KeyError:
            return set()

    def get_deterministic_transitions_by(self, terminal: str):
        transitions = self.get_transitions_by(terminal)
        if len(transitions) > 1:
            raise StateIndeterministicRuleError(f"State {self.name} has indeterminism for terminal {terminal}")
        elif len(transitions) == 0:
            return None
        return transitions.pop()

    def forget_state(self, state):
        for transition in self.transitions.values():
            transition.discard(state)

    def concat(self, state: State):
        if self.name != state.name:
            raise Exception(f"Cannot concat state {self.name} with {state.name}, states need to have the same name.")

        self.final_token = next((s for s in [self.final_token, state.final_token] if s), None)
        for terminal, transition in state.transitions.items():
            try:
                self.transitions[terminal].update(transition)
            except KeyError:
                self.transitions[terminal] = transition.copy()

    def copy(self) -> State:
        new_state = State(self.name, self.final_token)
        new_state.transitions = self.transitions.copy()
        for terminal, transition in new_state.transitions.items():
            new_state.transitions[terminal] = transition.copy()

        return new_state

    def pretty_output(self) -> str:
        if self.final_token:
            token_output = "*" if self.name == self.final_token else f"({self.final_token})*"
            return f"{self.name}{token_output}"
        return self.name
