# Round 2
snowballs = [1, 1.45, 0.52, 0.72]
pizza = [0.7, 1, 0.31, 0.48]
silicon_nugget = [1.95, 3.1, 1, 1.49]
sea_shell = [1.34, 1.98, 0.64, 1]

rates = [
    snowballs,
    pizza,
    silicon_nugget,
    sea_shell
]

starting_shells = 500

snowballs_index = 0
pizaa_index = 1
silicon_nugget_index = 2
shells_index = 3

indices = [
    snowballs_index,
    pizaa_index,
    silicon_nugget_index,
    shells_index
]

currencies = [
    "Snowballs",
    "Pizza",
    "Silicon Nugget",
    "Sea Shell"
]

n1results = []
n1results_string = []
n2results = []
n2results_string = []

# Starting
for index, shell_rate in enumerate(sea_shell):
    n1 = starting_shells * shell_rate
    n1results.append(n1 * rates[index][shells_index])
    n1results_string.append(currencies[index])
    for n2_index, n2_rate in enumerate(rates[index]):
        n2 = n1results[index] * n2_rate
        n2results.append(n2 * rates[index][indices[n2_index]])
        n2results_string.append(currencies[n2_index])

# print(n1results)
# print(n1results_string)
# print(n2results)
# print(n2results_string)

# Hamed's solution

import itertools

# Define the possible indices

# Generate combinations for arrays of size 3, 4, and 5
generated_indicies = []
for size in range(3, 7):
    for combo in itertools.product([0, 1, 2, 3], repeat=size - 2):
        # Ensure that all arrays start and end with the 3 index
        combo = (3,) + combo + (3,)
        generated_indicies.append(combo)

print(generated_indicies)

generated_results = []

for index, gen in enumerate(generated_indicies):
    temp = 1
    prev = gen[0]  # Shells array or whatever
    for el in gen:
        temp *= rates[prev][el]
        prev = el
    generated_results.append(temp)

print(max(generated_results))
print([currencies[i] for i in generated_indicies[generated_results.index(max(generated_results))]])