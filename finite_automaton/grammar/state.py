from __future__ import annotations
from os import stat
from typing import Dict, Set
import re

class State:
    GRAMMAR_REGEX = r"^<([A-Z_]+)>\s*::=((\s*([a-zε]*)(<([A-Z_]+)>)*([a-zε]*)\s*\|?)+)$"
    TOKEN_REGEX = r"^\s*([a-zε]*)(<([A-Z_]+)>)*([a-zε]*)\s*$"

    @classmethod
    def from_raw(cls, line):
        name = re.search(cls.GRAMMAR_REGEX, line).group(1)
        state = cls(name, False)
        productions_raw = re.search(cls.GRAMMAR_REGEX, line).group(2).split("|")
        for raw in productions_raw:
            groups = re.search(cls.TOKEN_REGEX, raw).groups()
            if (groups[0] == "ε"):
                state.is_final = True
                continue

            state.add_transition(groups[0], groups[2])

        return state

    def __init__(self, name: str, is_final: bool = True) -> None:
        self.name = name
        self.is_final = is_final
        self.transitions: Dict[str, Set[str]] = {}

    def add_transition(self, terminal: str, next_state: str):
        try:
            self.transitions[terminal].add(next_state)
        except KeyError:
            self.transitions[terminal] = { next_state }

    def forget_state(self, state):
        for transition in self.transitions.values():
            transition.discard(state)

    def concat(self, state: State):
        if self.name != state.name:
            raise Exception(f"Cannot concat state {self.name} with {state.name}, states need to have the same name.")

        self.is_final |= state.is_final
        for terminal, transition in state.transitions.items():
            try:
                self.transitions[terminal].update(transition)
            except KeyError:
                self.transitions[terminal] = transition.copy()

    def copy(self) -> State:
        new_state = State(self.name, self.is_final)
        new_state.transitions = self.transitions.copy()
        for terminal, transition in new_state.transitions.items():
            new_state.transitions[terminal] = transition.copy()

        return new_state