containers = [(1, 10, 1), (2, 80, 6), (3, 37, 3), (4, 90, 10), (5, 31, 2), (6, 17, 1), (7, 50, 4), (8, 20, 2), (9, 73, 4), (10, 89, 8)]


def calculate_expected_reward(multiplier, inhabitants):
    expected_reward = (multiplier * 10000) / (inhabitants + 1)
    return expected_reward

results = []
for container in containers:
    index, m, i = container
    results.append((index, calculate_expected_reward(m, i)))

print(sorted(results, key=lambda x: x[1]))

# Round 2 distibution
# 10x mult 1 inhabitant 0.998%
# 80x 6 inhabitant 18.178%
# 37x 3 inhabitant 5.118%
# 17x 1 inhabitant 7.539%
# 90x 10 inhabitant 11.807%
# 31x 2 inhabitant 6.987%
# 50x 4 inhabitant 8.516%
# 20x 2 inhabitant 1.614%
# 73x 4 inhabitant 24.060%
# 89x 8 inhabitant 15.184%

# Round 4
# 80x 6 inhabitant
# 50x 4 inhabitant
# 83x 7 inhabitant
# 31x 2 inhabitant
# 60x 4 inhabitant
# 89x 8 inhabitant
# 10x 1 inhabitant
# 37x 3 inhabitant
# 70x 4 inhabitant
# 90x 10 inhabitant
# 17x 1 inhabitant
# 40x 3 inhabitant
# 73x 4 inhabitant
# 100x 15 inhabitant
# 20x 2 inhabitant
# 41x 3 inhabitant
# 79x 5 inhabitant
# 23x 2 inhabitant
# 47x 3 inhabitant
# 30x 2 inhabitant

# Results based on round 2 popularity
# Price	Inhabitants	Est. Players Choosing	EV (Seashells) per Player
# 10	1	~50	200.4
# 30	2	~50	100.0
# 23	2	~50	100.0
# 40	3	~50	66.67
# 47	3	~50	66.67
# 41	3	~50	66.67
# 20	2	~81	61.96
# 60	4	~50	50.0
# 70	4	~50	50.0
# 79	5	~50	40.0
# 83	7	~50	28.57
# 17	1	~377	26.53
# 31	2	~349	14.31
# 100	15	~50	13.33
# 37	3	~256	13.03
# 50	4	~426	5.87
# 73	4	~1,203	2.08
# 80	6	~909	1.83
# 90	10	~590	1.69
# 89	8	~759	1.65