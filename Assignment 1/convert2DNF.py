import sys
import fileinput


# ------------------------------------------------------------------------------- #


def parseInput(wff):
    if type(wff) is str and wff not in ["and","or","if","iff","not"]:
        return wff
    if type(wff) is list and len(wff)==1 and wff[0] not in ["and","or","if","iff","not"]:
        return str(wff)
    if type(wff) is list and wff[0]=="not":
        return (["not"] + [parseInput(i) for i in wff[1:]])
    if type(wff) is list and len(wff)>2:
        op = len(wff)/2
        return([wff[op]] + [parseInput(i) for i in wff[0:op]] + [parseInput(i) for i in wff[op+1:]])

# ------------------------------------------------------------------------------- #

# If phi has the form P <-> Q, then:
  # Return CONVERT((P ^ Q) v (~P ^ ~Q))
def removeIFF(wff):
    result = []
    if type(wff) is str:
        return wff
    elif type(wff) is list and wff[0] == "iff":
        result.append("and")
        result.append(["if",removeIFF(wff[1]),removeIFF(wff[2])])
        result.append(["if",removeIFF(wff[2]),removeIFF(wff[1])])
        return result
    else:
        result.append(wff[0])
        result += (removeIFF(i) for i in wff[1:])
        return result

# ------------------------------------------------------------------------------- #

# If alpha has the form P -> Q, then:
  # Return CONVERT(~P v Q)
def removeIMPLIES(wff):
    if type(wff) is str:
        return wff
    elif type(wff) is list and wff[0] == "if":
        return(["or",
                ["not",
                 removeIMPLIES(wff[1])],
                removeIMPLIES(wff[2])])
    else:
        return([wff[0]] + [removeIMPLIES(i) for i in wff[1:]])

# ------------------------------------------------------------------------------- #

def doubleNegationElimination(wff):
    if type(wff) is str:
        return wff
    elif type(wff) is list and wff[0] == "not" and type(wff[1]) is list and wff[1][0] == "not":
        return(doubleNegationElimination(wff[1][1]))
    else:
        return([wff[0]] + [doubleNegationElimination(i) for i in wff[1:]])

# ------------------------------------------------------------------------------- #

def check_demorgan(wff):
    parsed_wff = demorgan(wff)
    if parsed_wff == wff:
        # No more ops possible
        return wff
    else:
        # For inner clauses
        return check_demorgan(parsed_wff)
 
# If alpha has the form ~(~P), then return CONVERT(P)   
def demorgan(wff):
    if type(wff) is str:
        return wff
    elif type(wff) is list and wff[0] == "not" and type(wff[1]) is list and wff[1][0] == "and":
        # If alpha has the form ~(P ^ Q), then return CONVERT(~P v ~Q)
        return(["or"] + [check_demorgan(["not", i]) for i in wff[1][1:]])
    elif type(wff) is list and wff[0] == "not" and type(wff[1]) is list and wff[1][0] == "or":
        # If alpha has the form ~(P v Q), then return CONVERT(~P ^ ~Q)
        return(["and"] + [check_demorgan(["not", i]) for i in wff[1][1:]])
    else:
        return ([wff[0]] + [check_demorgan(i) for i in wff[1:]])

# ------------------------------------------------------------------------------- #

# if alpha has the form (and,P,Q,R) then return (and,(and,P,Q),R)
# if alpha has the form (or,P,Q,R) then return (or,(or,P,Q),R)
def binaryize(wff): # ensures all connectives are binary (and / or)
    result = [];
    if type(wff) is str:
        return wff
    elif type(wff) is list and wff[0] == "and" and len(wff) > 3: # too long
        result.append("and");
        result.append(wff[1]);
        result.append(binaryize(["and"] + wff[2:]));
        # return(["and", wff[1], binaryize(["and"] + wff[2:])])
        return result;
    elif type(wff) is list and wff[0] == "or" and len(wff) > 3:
     # too long
        result.append("or");
        result.append(wff[1]);
        result.append(binaryize(["or"] + wff[2:]));
        # return(["or", wff[1], binaryize(["or"] + wff[2:])])
        return result;
    else:
        return([wff[0]] + [binaryize(i) for i in wff[1:]])
    
# ------------------------------------------------------------------------------- #

# if alpha has the form (and,(or,P,Q),R) then return (or,(and,P,R),(and,Q,R))
def check_distributivity(wff):
    parsed_wff = distribute(wff)
    if parsed_wff == wff: 
        # No fuurther distribution possible
        return wff
    else:
        # Distribute inner clauses
        return check_distributivity(parsed_wff)
    

def distribute(wff): # only works on binary connectives
    if type(wff) is str:
        return wff
    elif type(wff) is list and wff[0] == "and" and type(wff[1]) is list and wff[1][0] == "or":
        # distribute wff[2] over wff[1]
        return(["or"] + [check_distributivity(["and", i, wff[2]]) for i in wff[1][1:]])
    elif type(wff) is list and wff[0] == "and" and type(wff[2]) is list and wff[2][0] == "or":
        # distribute wff[1] over wff[2]
        return(["or"] + [check_distributivity(["and", i, wff[1]]) for i in wff[2][1:]])
    else:
        return ([wff[0]] + [check_distributivity(i) for i in wff[1:]])

# ------------------------------------------------------------------------------- #

def check_orAssociativity(wff):
    parsed_wff = orAssociativity(wff)
    if parsed_wff == wff:
        # No more ops possible
        return wff
    else:
        # For inner clauses
        return check_orAssociativity(parsed_wff)

# Opposite of Binaryize 
def orAssociativity(wff):
    if type(wff) is str:
        return wff
    elif type(wff) is list and wff[0] == "or":
        result = ["or"]
        # iterate through disjuncts looking for "or" lists
        for i in wff[1:]:
            if type(i) is list and i[0] == "or":
                result = result + i[1:]
            else:
                result.append(i)
        return result
    else:
        return([wff[0]] + [orAssociativity(i) for i in wff[1:]])

# ------------------------------------------------------------------------------- #

def check_andAssociativity(wff):
    parsed_wff = andAssociativity(wff)
    if parsed_wff == wff:
        # No more ops possible
        return wff
    else:
        # For inner clauses
        return check_andAssociativity(parsed_wff)

# Opposite of Binaryize     
def andAssociativity(wff):
    if type(wff) is str:
        return wff
    elif type(wff) is list and wff[0] == "and":
        result = ["and"]
        # iterate through conjuncts looking for "and" lists
        for i in wff[1:]:
            if type(i) is list and i[0] == "and":
                result = result + i[1:]
            else:
                result.append(i)
        return result
    else:
        return([wff[0]] + [andAssociativity(i) for i in wff[1:]])

# ------------------------------------------------------------------------------- #

def removeDuplicateLiterals(wff):
    if type(wff) is str:
        return wff
    if wff[0] == "not":
        return wff
    if wff[0] == "or":
        return(["or"] + [removeDuplicateLiterals(i) for i in wff[1:]])
    if wff[0] == "and":
        remains = []
        for l in wff[1:]:
            if l not in remains:
                remains.append(l)
        if len(remains) == 1:
            return remainwff[0]
        else:
            return(["and"] + remains)

# ------------------------------------------------------------------------------- #

def removeDuplicateClauses(wff):
    if type(wff) is str:
        return wff
    if wff[0] == "not":
        return wff
    if wff[0] == "and":
        return wff
    if wff[0] == "or": #disjunction of clauses
        remains = []
        for c in wff[1:]:
            if unique(c, remains):
                remains.append(c)
        if len(remains) == 1:
            return remainwff[0]
        else:
            return(["or"] + remains)

# check for unique clauses
def unique(c, remains):
    for p in remains:
        if type(c) is str or type(p) is str:
            if c == p:
                return False
        elif len(c) == len(p):
            if len([i for i in c[1:] if i not in p[1:]]) == 0:
                return False
    return True

# ------------------------------------------------------------------------------- #     

def parseOutput(dnf):
    if type(dnf) is str: # must be a single positive literal
        return ["or", ["and", dnf]]
    elif dnf[0] == "not": # must be a single negative literal
        return ["or", ["and", dnf]]
    elif dnf[0] == "and": # a single clause
        return ["or", dnf]
    else:
        result = ["or"]
        for clause in dnf[1:]:
            if type(clause) == str:
                result.append(["and", clause])
            elif clause[0] == "not":
                result.append(["and", clause])
            else:
                result.append(clause)
        return result


# ------------------------------------------------------------------------------- #

def dnf(wff):
    wff = removeIFF(wff)
    wff = removeIMPLIES(wff)
    wff = check_demorgan(wff)
    wff = doubleNegationElimination(wff)
    wff = binaryize(wff)
    wff = check_distributivity(wff)
    wff = check_orAssociativity(wff)
    wff = check_andAssociativity(wff)
    wff = removeDuplicateLiterals(wff)
    wff = removeDuplicateClauses(wff)
    # wff = parseOutput(wff)
    wff = binaryize(wff)
    return wff

# ------------------------------------------------------------------------------- #

if __name__ == "__main__":

    sentences = fileinput.input()
    for l in sentences:
        wff = parseInput(eval(l.strip()))
        print repr(dnf(wff))