'''
    Code to implement decision heuristics - Jeroslow-Wang and VSIDS

    Authors - Het Shah, Ishita Mediratta

    Run using "python dpll.py"

    Sample Input -> [['!p'],['p','q'],['p']]
    Output -> 'UNSATISFIABLE'
'''

import argparse
import numpy as np
from itertools import compress
from numpy import sign, floor

#-----------------------------------------------------------------

def parseCNF(formula):
    '''
        Parses the string format into the DIMACS CNF format.
    '''
    no_of_clauses = len(formula)
    no_of_vars = 1
    symbols = {}

    for c in formula:
        for l in c:
            if(len(l)>1):
                if l[1] not in symbols:
                    symbols[l[1]] = no_of_vars;
                    no_of_vars = no_of_vars + 1;
                continue;
            else:
                if l[0] not in symbols:
                    symbols[l[0]] = no_of_vars;
                    no_of_vars = no_of_vars + 1;
                continue;

    clauses = []

    for c in formula:
        clause = []
        for l in c:
            if(len(l)>1):
                clause.append(-1*symbols[l[1]])
            else:
                clause.append(symbols[l[0]])
        clauses.append(clause)


    #print(clauses)

    return clauses

#-----------------------------------------------------------------

class Solver:
    def __init__(self, clauses,heuristic):
        '''
        Create CDCL Solver object and preprocess the CNF clauses.
        '''
        # Things we need to keep track of
        self.clauses = clauses
        self.literals = []  # List of literals
        self.decision = []  # Literal decisions (0, u, or 1)
        self.w1 = []  # List of watched literals, two per clause
        self.w2 = []
        self.iw1 = []  # List of indices of watched literals, two per clause
        self.iw2 = []
        self.wpos = []  # List of clauses containing positive version of this literal (one per literal)
        self.wneg = []  # Negative literal
        self.levels = []  # List of levels at which each decision was made
        self.polarity = []  # Literal VSIDS score
        self.level = 0  # Current decision level
        self.conflict_clause = []
        self.propagate_queue = []
        self.implied_by = []
        self.heuristic = heuristic
        # Preprocess
        self.preprocess()

    def preprocess(self):
        '''
        Set up variables/graph for CDCL solving.
        '''
        # Initialize all our tracking variables
        # NOTE: We assume all clauses have length > 0
        for i in range(len(self.clauses)):
            # Remove duplicates in the clause
            self.clauses[i] = list(set(self.clauses[i]))

            # It's fine to initialize the two watched 
            # literals to the first two literals in the clause
            # or the first literal in the clause if length = 1
            if len(self.clauses[i]) > 1:
                self.w1.append(self.clauses[i][0])
                self.w2.append(self.clauses[i][1])
                self.iw1.append(0)
                self.iw2.append(1)
                self.implied_by.append(-1)
            else:
                self.w1.append(self.clauses[i][0])
                self.w2.append(self.clauses[i][0])
                self.iw1.append(0)
                self.iw2.append(0)
                self.implied_by.append(-1)
            for lit in self.clauses[i]:
                if abs(lit) not in self.literals:
                    # We need to establish a new literal
                    # and all of its trappings
                    self.literals.append(abs(lit))
                    self.polarity.append(1)
                    self.decision.append(0)
                    self.levels.append(0)
                    self.implied_by.append(-1)
                    if lit > 0:
                        self.wpos.append([i])
                        self.wneg.append([])
                    else:
                        self.wpos.append([])
                        self.wneg.append([i])
                else:
                    j = self.literals.index(abs(lit))
                    self.polarity[j] += 1
                    if lit > 0:
                        self.wpos[j].append(i)
                    else:
                        self.wneg[j].append(i)
                        
    def print_state(self):
        '''
        Print the current state of the solver. For debugging.
        '''
        print('Clauses: ', self.clauses)
        print('Literals: ', self.literals)
        print('Decision:', self.decision)
        print('Watched 1: ', self.w1)
        print('Watched 2:', self.w2)
        print('Watched 1 Index: ', self.iw1)
        print('Watched 2 Index:', self.iw2)
        print('Watched positive: ', self.wpos)
        print('Watched negative: ', self.wneg)
        print('Levels: ', self.levels)
        print('Polarity: ', self.polarity)    
        
    def decide_literal(self):
        '''
        VSIDS/Jeroslow-Wang check for new literal.
        '''
        if self.heuristic == 'VSIDS':
          literals_sorted = [x for _,x in sorted(zip(self.polarity,self.literals))]
          literals_undecided = [x for x in literals_sorted if self.decision[self.literals.index(x)] == 0]
          lit = literals_undecided[-1]
          self.apply_literal(lit)
        elif self.heuristic == 'JW':
          counter = {}
          for clause in self.clauses:
              for literal in clause:
                  if literal in counter:
                      counter[literal] += 2 ** -len(clause)
                  else:
                      counter[literal] = 2 ** -len(clause)

          lit = max(counter, key=counter.get)
          self.apply_literal(lit)

    def resolve(self, clause):
        '''
        Used to resolve the conflict clause. See resolve rule in Handbook of Satisfiability,
        Chapter 4.
        '''
        decision_made = [x for x in clause if self.decision[self.literals.index(abs(x))] != 0]
        return list(set([x for x in decision_made if ((not ((x in clause) and (-x in clause))))]))
    
    def analyze_conflict(self):
        '''
        Analyze the conflict, return a conflict clause and a backtrack level.
        '''
        # Grab the literals we need to backtrack
        backtrack_idxs = [self.literals.index(abs(x)) for x in self.conflict_clause\
                              if (self.levels[self.literals.index(abs(x))] == self.level)]

        conflict = []
                    
        for idx in backtrack_idxs:
            if self.implied_by[idx] > 0:
                conflict.extend(self.clauses[self.implied_by[idx]])
                    
        conflict.extend(self.conflict_clause)

        learned_clause = self.resolve(conflict)

        levels = [self.levels[self.literals.index(abs(x))] for x in learned_clause]

        b = max(levels)
        if b == 0:
            b = -1
        return b, learned_clause
    
    def backtrack(self, b, learned_clause):
        '''
        Undo whatever created a conflict.
        '''
        # Add the learned clause to our clauses
        self.clauses.append(learned_clause)
        if len(learned_clause) > 1:
            self.w1.append(learned_clause[0])
            self.iw1.append(0)
            self.w2.append(learned_clause[1])
            self.iw2.append(1)
            self.implied_by.append(-1)
        else:
            self.w1.append(learned_clause[0])
            self.iw1.append(0)
            self.w2.append(learned_clause[0])
            self.iw2.append(0)
            self.implied_by.append(-1)
            
        temp_levels = [self.levels[self.literals.index(abs(x))] for x in learned_clause]
                
        # Update "pointers"
        clause_idx = len(self.clauses)-1
        for lit in learned_clause:
            lit_idx = self.literals.index(abs(lit))
            self.implied_by[lit_idx] = -1
            # Update the polarity
            self.polarity[lit_idx] += 1
            # Update the watched positives/negatives
            if lit > 0:
                self.wpos[lit_idx].append(clause_idx)
            else:
                self.wneg[lit_idx].append(clause_idx)
                
        # Undo variable assignments
        for level_idx in range(len(self.levels)):
            if self.levels[level_idx] >= b:
                self.levels[level_idx] = 0
                self.decision[level_idx] = 0
        
        # Set the level
        self.level = b
                
        # Flip the variables that need flipping
        for i in range(len(learned_clause)):
            if temp_levels[i] == b:
                self.apply_literal(learned_clause[i])
                
    def has_unassigned_literals(self):
        '''
        Checks if there is an undecided literal.
        '''
        return (True in [x == 0 for x in self.decision])
                
    def solve(self):
        '''
        Apply CDCL solver to self.clauses.
        '''
        if self.unit_propagation() == 'CONFLICT':
#             print('ALREADY?')
            return 'UNSATISFIABLE'
        self.level = 0
        polarity_count = 0
        while self.has_unassigned_literals():
            #self.print_state()
            self.level += 1
            self.decide_literal()
            while self.unit_propagation() == 'CONFLICT':
                polarity_count += 1
                if polarity_count > 49:
                    self.polarity = [int(floor(x/2)) for x in self.polarity]
                    polarity_count = 0
                
                b, c = self.analyze_conflict()
                
                if b < 0:
                    return 'UNSATISFIABLE'
                else:
                    # Implicitly sets self.level = b
                    self.backtrack(b, c)
        
        return 'SATISFIABLE'
    
    def get_model(self):
        '''
        Get the current solution. Obviously this has no meaning if self.solve()
        returned 'UNSATISFIED'.
        '''
        return [x*d for x,d in zip(self.literals,self.decision)]
    
    def apply_literal(self, lit):
        '''
        Let's update the literal and watched literals in the graph
        '''
        i = self.literals.index(abs(lit))
        self.decision[i] = sign(lit)
        self.levels[i] = self.level
        
        self.propagate_queue.insert(0,lit)

    def unit_propagation(self):
        '''
        Repeatedly apply UnitProp rule until no longer possible.
        '''

        #If we have unit clauses, make a decision, add them to the queue
        for i in range(len(self.clauses)):
            if (len(self.clauses[i]) == 1) and (self.decision[self.literals.index(abs(self.clauses[i][0]))] == 0):
                self.apply_literal(self.clauses[i][0])

        while len(self.propagate_queue) > 0:
            # Grab a literal from the queue
            lit = self.propagate_queue.pop()
            lit_idx = self.literals.index(abs(lit))
            
            # Find the clauses to consider
            watched = self.wneg[lit_idx]
            if lit < 0:
                watched = self.wpos[lit_idx]
            
            # Loop over said clauses
            for i in watched:
                i1 = self.literals.index(abs(self.w1[i]))
                i2 = self.literals.index(abs(self.w2[i]))
                s1 = sign(self.w1[i])
                s2 = sign(self.w2[i])
                d1 = self.decision[i1] * s1
                d2 = self.decision[i2] * s2
                
                if (d1 == 1) or (d2 == 1):
                    # Already satisfied, we're done
                    continue
                
                u = [x for x in self.clauses[i] if (((self.decision[self.literals.index(abs(x))] == 0) or (self.decision[self.literals.index(abs(x))]*sign(x) == 1)) and (x != self.w1[i]) and (x != self.w2[i]))]

                # If so, do it
                if (len(u) > 0) and ((d1 == -1) or (d2 == -1)):
                    if abs(lit) == abs(self.w1[i]):
                        self.w1[i] = u[0]
                        self.iw1[i] = self.clauses[i].index(u[0])
                    else:
                        self.w2[i] = u[0]
                        self.iw2[i] = self.clauses[i].index(u[0])
                elif ((d1 == -1) and (d2 == -1)):
                    self.conflict_clause = [self.w1[i], self.w2[i]]
                    return 'CONFLICT'
                elif ((d1 == 0) or (d2 == 0)) and not ((d1 == 0) and (d2 == 0)):
                    if d1 == 0:
                        self.apply_literal(self.clauses[i][self.iw1[i]])
                        self.implied_by[i1] = i
                    else:
                        self.apply_literal(self.clauses[i][self.iw2[i]])
                        self.implied_by[i2] = i
                else:
                    pass
            
        return 'SATISFIABLE'

#-----------------------------------------------------------------

'''
    Run "python dpll.py"

    Sample Input -> [['!p'],['p','q'],['p']]
    Output -> 'UNSATISFIABLE'
'''

if __name__ == "__main__":

    print("Enter a WFF in CNF:")
    sentence = input()
    print("Output:")
    DPLL = Solver(parseCNF(sentence),"JW")
    # DPLL = Solver(parseCNF(sentence),"VSIDS")
    print repr(DPLL.solve())