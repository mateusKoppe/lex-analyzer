from lex_analyzer.grammar import Grammar
from lex_analyzer.grammar.state import State

class Analyzer:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.current_state = None
        self.output_tokens = []

    def run(self, input: str):
        self.output_tokens = []
        self.current_state = self.grammar.initial_state
        for terminal in input:
            self.move_state(terminal)

        if self.current_state.final_token:
            self.output_tokens.append({"token": self.current_state.name})

        return self.output_tokens

    def move_state(self, terminal: str):
        next_state = self.grammar.get_transition_state(self.current_state, terminal)
        
        if not next_state and self.current_state.final_token:
            self.new_token_cycle()
            self.move_state(terminal)
            return
        elif not next_state and not self.current_state.final_token:
            raise Exception(f"Lexical error on terminal {terminal}")

        self.current_state = next_state

    def new_token_cycle(self):
        self.output_tokens.append({"token": self.current_state.name})
        self.current_state = self.grammar.initial_state

    def look_behind(self, terminal: str) -> State:
        state = self.grammar.get_transition_state(self.grammar.initial_state, terminal)

        