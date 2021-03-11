import pandas as pd
import docplex.cp.model as cp


# Precedence operations matrix
preced_op = pd.read_excel("PrecedenceOperationsMatrix_GA.xlsx")
preced_op = preced_op.set_index('Operations')

# Calls the CP modelling from IBM CPLEX
feasible_model = cp.CpoModel(name="ILP Model")
valid_ops = [1, 2, 3, 5, 7, 10, 11, 13, 14, 15, 16, 17, 20, 21]

# Create a binary variable P = 1 if operation p is in the position j of the
# sequence
P_var = {
    (p, j): feasible_model.binary_var(name="P_{0}_{1}".format(p, j))
    for p in valid_ops
    for j in range(1, len(valid_ops) + 1)
}

# Create a dictionary of precedence operations
preced_oper = {
    (p1, p2): preced_op.loc[p2, p1]
    for p1 in preced_op.index
    for p2 in preced_op.columns
}


# Constraint 1: states that each sequence position must have only one
# operation at a time
for j in range(1, len(valid_ops) + 1):
    feasible_model.add(
        feasible_model.sum(
            P_var[p, j]
            for p in valid_ops
        ) == 1
    )

# Constraint 2: states that each operation must be in one position sequence
# at a time
for p in valid_ops:
    feasible_model.add(
        feasible_model.sum(
            P_var[p, j]
            for j in range(1, len(valid_ops) + 1)
        ) == 1
    )

# Constraint 3: states that
feasible_model.add(feasible_model.sum(P_var[p, j]
                                      for p in valid_ops
                                      for j in range(1, len(valid_ops) + 1)

                                      ) == len(valid_ops)

                   )

for p1 in valid_ops:
    for p2 in valid_ops:
        for j2 in range(1, len(valid_ops) + 1):
            feasible_model.add(
                feasible_model.sum(P_var[p1, j1] for j1 in range(1, j2)
                                   ) >= P_var[p2, j2] * preced_oper[p1, p2])


# Calls the CPO solver from IBM CPLEX
# The start_search function find all possible solutions based on the established
# constraints
# SearchType: Define the type of CP search
# SolutionLimit: states maximun number of solutions found to get an output (if
# no limit is defined, the solver will keep looking for solutions and it can
# take a longer time)
solutions = feasible_model.start_search(
    SearchType='DepthFirst',
    SolutionLimit=200)

# Creating a dictionnary in which key is a tuple (i, j) stating the operation
# and the value is 1 or 0.

P_value = {}
all_possible_op = []
for sol in solutions:

    for p in valid_ops:
        for j in range(1, len(valid_ops) + 1):
            P_value[p, j] = sol.get_value(P_var[p, j])

    newDict = {key: value for (
        key, value) in P_value.items() if value == 1}

    op_sequence = newDict.keys()

    # Here the dictionnary is filtered: only keys with values = 1 are selected
    operat = [0] * len(valid_ops)
    for index, value in enumerate(operat, 1):
        for q, el in enumerate(op_sequence, 1):
            if index == int(el[1]):
                operat[index-1] = el[0]
    try:
        # Output the list of all possible operations sequence respecting the stated
        # constraints. PS: here the max length will be 200, because this SolutionLimit
        # was stated in the function start_search

        all_possible_op.append(operat)
    except Exception:
        print("Memory limit reached. Exporting results...")
        break



