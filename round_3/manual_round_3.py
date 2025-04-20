import numpy as np

# Range	% Votes	Estimated Midpoint
# Sub 250	13%	240
# 250–270	18%	260
# 271–290	37%	280.5
# 291–310	11%	300.5
# 311–320	21%	315.5

# Simulation parameters
num_turtles = 1000
average_second_bid = 281.1  # Average based on poll

max_profit = 0
best_first_bid = 0
best_second_bid = 0

def calculate_flipper_profit(first_bid, second_bid, trials=1000):
    global max_profit, best_first_bid, best_second_bid

    total_profit = 0
    for _ in range(trials):
        # Generate turtle reserve prices using bimodal uniform distribution
        # Due to different bimodal ranges, the first range is 4/11 turtles and second is 7/11 turtles
        low_range = np.random.uniform(160, 200, num_turtles * 4 // 11)
        high_range = np.random.uniform(250, 320, num_turtles * 7 // 11)
        reserve_prices = np.concatenate((low_range, high_range))
        np.random.shuffle(reserve_prices)

        # First bid logic: turtles accept if bid > reserve and reserve in [160, 200]
        first_accepts = (reserve_prices <= 200) & (first_bid > reserve_prices)
        first_accepted = np.sum(first_accepts)

        # Second bid logic: turtles accept if bid > reserve and reserve in [250, 320]
        # Also must be above average, or apply scale if under
        second_candidates = ~first_accepts  # Turtles not caught by first bid
        second_accepts = (reserve_prices <= 320) & (reserve_prices >= 250) & second_candidates

        # Actual trade condition
        second_trade_full = (second_bid > reserve_prices) & second_accepts & (second_bid >= average_second_bid)
        second_trade_scaled = (second_bid > reserve_prices) & second_accepts & (second_bid < average_second_bid)

        second_accepted_full = np.sum(second_trade_full)

        # Apply profit scaling for under-average second bids
        scale_factor = ((320 - average_second_bid) / (320 - second_bid)) ** 3 if second_bid < average_second_bid else 1
        second_accepted_scaled = np.sum(second_trade_scaled) * scale_factor

        total_flippers = first_accepted + second_accepted_full + second_accepted_scaled

        cost = (first_accepted * first_bid) + (second_accepted_full * second_bid) + (
                    second_accepted_scaled * second_bid)
        revenue = total_flippers * 320
        profit = revenue - cost

        output = {
            "Total Turtles": num_turtles,
            "First Bid Accepted": first_accepted,
            "Second Bid Accepted (Full)": second_accepted_full,
            # Higher than both the turtle reserve price and archipelago avg
            "Second Bid Accepted (Scaled)": second_accepted_scaled,  # Higher than reserve but lower than avg
            "Total Flippers Acquired": total_flippers,
            "Total Cost": cost,
            "Total Revenue": revenue,
            "Total Profit": profit,
            "Scale Factor Applied": scale_factor
        }

        if profit > max_profit:
            max_profit = profit
            best_first_bid = first_bid
            best_second_bid = second_bid

        print(output)
        # accumulate profit:
        total_profit += profit
    avg_profit = total_profit / trials
    if avg_profit > max_profit:
        max_profit = avg_profit
        best_first_bid = first_bid
        best_second_bid = second_bid


for f_b in range(160, 200):
    for s_b in range(250, 320):
        calculate_flipper_profit(f_b, s_b)

print(max_profit)
print(best_first_bid)
print(best_second_bid)

# 55262
# 199
# 283

# 1000 trials
# 55692
# 199
# 284