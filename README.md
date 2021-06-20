# deterministic-finite-automaton
Get the deterministic finite automaton for each grammar and tokens you define.

## Getting Started

Using a virtual environment (optional):
```bash
python -m venv venv
source ./venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage 
It is possible to use tokens and grammars as the input for this package.

Tokens:
```
if
else
```

Grammar example:
```
<S> ::= a<A> | e<A> | i<A> | o<A> | u<A>
<A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | ε
```


Example:
```bash
# Running using examples/input.txt as input
python main.py < examples/input.txt

# the output will be
### NDFA ###
+----+------+------+---+---+---+---+---+---+
| /  | i    | e    | a | o | u | f | l | s |
+----+------+------+---+---+---+---+---+---+
| S  | G, A | G, C | G | G | G | - | - | - |
| A  | -    | -    | - | - | - | B | - | - |
| B* | -    | -    | - | - | - | - | - | - |
| C  | -    | -    | - | - | - | - | D | - |
| D  | -    | -    | - | - | - | - | - | E |
| E  | -    | F    | - | - | - | - | - | - |
| F* | -    | -    | - | - | - | - | - | - |
| G* | G    | G    | G | G | G | - | - | - |
+----+------+------+---+---+---+---+---+---+

### DFA ###
+----+---+---+---+---+---+---+---+---+
| /  | i | e | a | o | u | s | f | l |
+----+---+---+---+---+---+---+---+---+
| S  | H | I | G | G | G | - | - | - |
| B* | - | - | - | - | - | - | - | - |
| D  | - | - | - | - | - | E | - | - |
| E  | - | F | - | - | - | - | - | - |
| F* | - | - | - | - | - | - | - | - |
| G* | G | G | G | G | G | - | - | - |
| H* | G | G | G | G | G | - | B | - |
| I* | G | G | G | G | G | - | - | D |
+----+---+---+---+---+---+---+---+---+
```

## Testing
This project uses unittest, to run the tests run:
```bash
python -m unittest discover -s tests
```
