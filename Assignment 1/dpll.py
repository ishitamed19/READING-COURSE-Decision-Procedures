import sys
import fileinput

# ------------------------------------------------------------------------------- #

# at least one member of model in each clause
def allClausesTrue(cnf, model): 
    for clause in cnf[1:]: # skip the "and"
        if len([var for var in clause[1:] if var in model]) == 0:
            return False
    return True

# ------------------------------------------------------------------------------- #

# returns the compliment of each model literal
def complement_model(model): 
    comp_literals = []
    for literal in model:
        if type(literal) is str:
            comp_literals.append(["not", literal])
        else:
            comp_literals.append(literal[1])
    return comp_literals

# ------------------------------------------------------------------------------- #

# some clause cannot be satisfied
def someClausesFalse(cnf, model): 
    modelCompliments = complement_model(model)
    for clause in cnf[1:]:
        if len([var for var in clause[1:] if var not in modelCompliments]) == 0:
            return True
    return False

# ------------------------------------------------------------------------------- #

def pureLiteral(cnf, model): # finds 1 pure literal not already in model
    modelCompliments = complement_model(model)
    candidates = []
    for clause in cnf[1:]:
        if len([var for var in clause[1:] if var in model]) == 0:
            # clause not yet satisfied by model
            candidates = candidates + [var for var in clause[1:]]
    candidateCompliments = complement_model(candidates)
    pure = [var for var in candidates if var not in candidateCompliments]
    for var in pure:
        if var not in model and var not in modelCompliments:
            return var
    return False

# ------------------------------------------------------------------------------- #

def unitClause(cnf, model): # finds 1 literal not in model appearing by itself in a clause
    modelCompliments = complement_model(model)
    for clause in cnf[1:]:
        remaining = [var for var in clause[1:] if var not in modelCompliments]
        if len(remaining) == 1:
            if remaining[0] not in model:
                return remaining[0]
    return False

# ------------------------------------------------------------------------------- #

def pickSymbol(cnf, model): # finds a positive literal not in model or model compliments
    symbols = model + complement_model(model)
    for clause in cnf[1:]:
        for literal in clause[1:]:
            if type(literal) is str and literal not in symbols:
                return literal
    return False

# ------------------------------------------------------------------------------- #

def dpll(cnf, model):
    if [] in cnf: 
        # Empty Clause
        return False
    if allClausesTrue(cnf, model):
        return model
    if someClausesFalse(cnf, model):
        return False
    pure = pureLiteral(cnf, model)
    if pure:
        return dpll(cnf, model + [pure])
    unit = unitClause(cnf, model)
    if unit:
        return dpll(cnf, model + [unit])
    pick = pickSymbol(cnf, model)
    if pick:
        # try positive
        result = dpll(cnf, model + [pick])
        if result:
            return result
        else:
            # try negative
            result = dpll(cnf, model + [['not', pick]])
            if result:
                return result
            else:
                return False

# ------------------------------------------------------------------------------- #

def formatOutput(result):
    if result == False:
        return ["UNSAT"]
    else:
        mod = ["SAT"]
        for v in result:
            if type(v) is str:
                mod.append(v + "=true")
            else:
                mod.append(v[1] + "=false")
        return mod
            
# ------------------------------------------------------------------------------- #

# test example
# ex2 = ['and', ['or', ['not', 'P'], 'Q'], ['or', ['not', 'Q'], ['not', 'P']], ['or', 'P', ['not', 'Q']]]
        
# print formatOutput(dpll(ex2,[]))

if __name__ == "__main__":

    sentences = fileinput.input()
    for l in sentences:
        print repr(formatOutput(dpll(eval(l.strip()),[])))