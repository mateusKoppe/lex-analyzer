from finite_automaton.grammar import Grammar

def get_inputs():
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    return lines


def generate_nfa(lines):
    # TODO: first line could be a grammar
    nfa = Grammar.from_token(lines[0])
    del lines[0]
    acc_lines = []
    for line in lines:
        if Grammar.is_expression(line):
            acc_lines.append(line)

        elif len(acc_lines) and not line:
            new_nfa = Grammar.from_raw_grammar(acc_lines)
            nfa.concat(new_nfa)
            
            acc_lines = []

        if line and Grammar.is_sentence(line):
            new_nfa = Grammar.from_token(line)
            nfa.concat(new_nfa)

    if len(acc_lines):
        new_nfa = Grammar.from_raw_grammar(acc_lines)
        nfa.concat(new_nfa)

    return nfa

nfa = generate_nfa(get_inputs())

print("### Grammar ###")
print(nfa.asci_table())

print("### DFA ###")
dfa = Grammar.NFA_to_DFA(nfa)
print(dfa.asci_table())
