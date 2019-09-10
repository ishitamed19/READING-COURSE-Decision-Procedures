import sys
import fileinput

# ------------------------------------------------------------------------------- #

def complementingLiteralsPresent(clause):
	unique = []
	for literal in clause[1:]:
		if type(literal) is str and literal in unique:
			return True
		if type(literal) is str and literal not in unique:
			unique.append(literal)
		if type(literal) is list and literal[1] in unique:
			return True
		if type(literal) is list and literal[1] not in unique:
			unique.append(literal[1])
	return False

# ------------------------------------------------------------------------------- #

def satDNF(dnf):
	for clause in dnf[1:]:
		if(complementingLiteralsPresent(clause)):
			continue
		else:
			return clause
	return False

# ------------------------------------------------------------------------------- #

def formatOutput(result):
	if result == False:
		return ["UNSAT"]
	else:
		mod = ["SAT"]
		for v in result[1:]:
			if type(v) is str:
				mod.append(v + "=true")
			else:
				mod.append(v[1] + "=false")
		return mod

# ------------------------------------------------------------------------------- #

def parseInput(dnf):
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

if __name__ == "__main__":

    sentences = fileinput.input()
    for l in sentences:
        print repr(formatOutput(satDNF(parseInput(eval(l.strip())))))