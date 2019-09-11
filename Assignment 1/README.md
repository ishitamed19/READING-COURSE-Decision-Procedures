# ASSIGNMENT 1

### Implement the following:

1. Given a well-formed formula, convert it to CNF and DNF
2. Given a formula in DNF, check if it's satisfiable or not
3. Given a formula in CNF. check if it's satisfiable or not

### Operators
- "and"
- "or"
- "if"
- "iff"
- "not"

### Example

To execute `python <program_name>.py`

#### See Screenshots

<img src="https://raw.githubusercontent.com/ishitamed19/READING-COURSE-Decision-Procedures/master/Assignment%201/Screenshot%202019-09-11%20at%207.13.12%20PM.png">

<img src="https://raw.githubusercontent.com/ishitamed19/READING-COURSE-Decision-Procedures/master/Assignment%201/Screenshot%202019-09-11%20at%207.13.32%20PM.png">

Sample input to CNF/DNF convert-
 `[["p","and","r"],"if",[["not","p"],"or","r"]]`
 
 Output from convert2CNF.py
 `['and', ['or', ['not', 'p'], ['not', 'r'], 'r']]`
  * list beginning with 'or' represents a single clause - if only one literal present in it, then unit clause
 
 Output from convert2DNF.py
  `['or', ['and', ['not', 'p']], ['and', ['not', 'r']], ['and', 'r']]`
  * list beginning with 'and' represents a single clause - if only one literal present in it, then unit clause
 
Input to dpll.py should be in the same format as the output from convert2CNF.py
Input to satDNF.py should be in the same format as the output from convert2DNF.py

Output from dpll.py
  `['SAT', 'p=false']`

Output from satDNF.py
  `['SAT', 'p=false']`
