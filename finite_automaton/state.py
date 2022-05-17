from typing import Dict, Set
import re

class State:
    GRAMMAR_REGEX = r"^<([A-Z]+)>\s*::=((\s*([a-zε]*)(<([A-Z]+)>)*([a-zε]*)\s*\|?)+)$"
    TOKEN_REGEX = r"^\s*([a-zε]*)(<([A-Z]+)>)*([a-zε]*)\s*$"

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
