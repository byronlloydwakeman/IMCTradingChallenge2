containers = [(1, 10, 1), (2, 80, 6), (3, 37, 3), (4, 90, 10), (5, 31, 2), (6, 17, 1), (7, 50, 4), (8, 20, 2), (9, 73, 4), (10, 89, 8)]


def calculate_expected_reward(multiplier, inhabitants):
    expected_reward = (multiplier * 10000) / (inhabitants + 1)
    return expected_reward

results = []
for container in containers:
    index, m, i = container
    results.append((index, calculate_expected_reward(m, i)))

print(sorted(results, key=lambda x: x[1]))
