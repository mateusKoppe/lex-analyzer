import sys
from lex_analyzer.analyzer import Analyzer
from lex_analyzer.grammar import Grammar

try:
    file_name = sys.argv[1]
except:
    print("Missing grammar argument")
    exit()

try:
    source_file = sys.argv[2]
except:
    print("Missing source argument")
    exit()

def get_lines():
    file = open(file_name, "r")
    lines = file.readlines()
    file.close()
    return list(map(lambda line: line[:len(line) - 1], lines))
    
def generate_nfa(lines):
    # TODO: first line could be a grammar
    nfa = Grammar()
    for line in lines:
        nfa.concat(Grammar.from_regex_rule())

    return nfa

nfa = generate_nfa(get_lines())

print("### Grammar ###")
print(nfa.asci_table())

print("### DFA ###")
dfa = Grammar.NFA_to_DFA(nfa)
print(dfa.asci_table())

file = open(source_file, "r")
input = file.read()
file.close()

analyzer = Analyzer(dfa)
print(analyzer.run(input))