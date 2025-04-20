from typing import List
import jsonpickle
from datamodel import OrderDepth, TradingState, Order
import statistics


class Trader:
    def get_mid_price(self, order_depth):
        best_bid = max(order_depth.buy_orders.keys(), default=0)
        best_ask = min(order_depth.sell_orders.keys(), default=0)
        if best_bid and best_ask:
            return (best_bid + best_ask) / 2
        return 0

    def run(self, state: TradingState):
        MAX_WINDOW_LENGTH = 200
        # MEAN REVERSION STRAT
        # Keep a rolling window of the mean and trade around that
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of
        # orders to be sent
        print("traderData: " + state.traderData)
        trader_data = jsonpickle.decode(state.traderData) if state.traderData else {}

        print("Observations: " + str(state.observations))
        result = {}
        for product in state.order_depths:

            if product == "RAINFOREST_RESIN":
                if "pricing_window" not in trader_data.keys():
                    trader_data["pricing_window"] = {product: []}
                else:
                    if len(trader_data["pricing_window"][product]) >= MAX_WINDOW_LENGTH:
                        trader_data["pricing_window"][product].pop(0)

                order_depth: OrderDepth = state.order_depths[product]
                # Add price to window
                trader_data["pricing_window"][product].append(self.get_mid_price(order_depth))
                orders: List[Order] = []

                bid_threshold = 9998  # Participant should calculate this value
                ask_threshold = 10002
                # Makes it worse lmao
                # if len(trader_data["pricing_window"]) != 0:
                #     mean_price = sum(trader_data["pricing_window"][product]) / len(trader_data["pricing_window"][product])
                #     spread = 2
                #     bid_threshold = mean_price - spread
                #     ask_threshold = mean_price + spread

                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                    len(order_depth.sell_orders)))

                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = min(list(order_depth.sell_orders.items()))
                    if int(best_ask) <= bid_threshold:
                        print("BUY RAINFOREST RESIN", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))  # Buy all available

                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = max(list(order_depth.buy_orders.items()))
                    if int(best_bid) >= ask_threshold:
                        print("SELL RAINFOREST RESIN", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))  # Sell all available

                result[product] = orders

            if product == "KELP":
                if "kelp_prices" not in trader_data:
                    trader_data["kelp_prices"] = []

                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                # Update price history
                trader_data["kelp_prices"].append(mid_price)
                if len(trader_data["kelp_prices"]) > 50:
                    trader_data["kelp_prices"].pop(0)

                prices = trader_data["kelp_prices"]

                orders = []

                if len(prices) >= 30:  # Enough data
                    sma = sum(prices) / len(prices)
                    std_dev = statistics.stdev(prices)

                    upper_threshold = sma + 3 * std_dev
                    lower_threshold = sma - 3 * std_dev

                    # BREAKOUT logic
                    if mid_price > upper_threshold:
                        # Upward momentum breakout
                        if len(order_depth.buy_orders) > 0:
                            best_bid, bid_volume = max(order_depth.buy_orders.items())
                            print("BREAKOUT DOWN! SELL", bid_volume, "@", best_bid)
                            orders.append(Order(product, best_bid, -bid_volume))

                    elif mid_price < lower_threshold:
                        # Downward momentum breakout
                        if len(order_depth.sell_orders) > 0:
                            best_ask, ask_volume = min(order_depth.sell_orders.items())
                            print("BREAKOUT UP! BUY", -ask_volume, "@", best_ask)
                            orders.append(Order(product, best_ask, -ask_volume))

                result[product] = orders

            if product == "SQUID_INK":
                order_depth: OrderDepth = state.order_depths[product]

                total_bid_volume = sum(order_depth.buy_orders.values())
                total_ask_volume = sum(order_depth.sell_orders.values())

                imbalance = total_bid_volume - abs(total_ask_volume)
                orders: List[Order] = []

                # Tweak this threshold as needed
                imbalance_threshold = 10

                bid_threshold = 1900  # Participant should calculate this value
                ask_threshold = 2100

                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = min(list(order_depth.sell_orders.items()))
                    if int(best_ask) <= bid_threshold:
                        print("BUY SQUID INK", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))  # Buy all available

                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = max(list(order_depth.buy_orders.items()))
                    if int(best_bid) >= ask_threshold:
                        print("SELL SQUID INK", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))  # Sell all available

                result[product] = orders

            if product == "PICNIC_BASKET1":
                prices_index = "picnic_basket1_prices"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max 200-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 200:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 1.5  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                result[product] = orders

            if product == "PICNIC_BASKET2":
                prices_index = "picnic_basket2_prices"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max 200-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 200:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 1.5  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                result[product] = orders

            if product == "CROISSANTS":
                prices_index = "croissants_prices"
                prev_mavg50_index = "prev_croissants_prices_mavg50"
                prev_mavg200_index = "prev_croissants_prices_mavg200"

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                if prev_mavg50_index not in trader_data:
                    trader_data[prev_mavg50_index] = None
                if prev_mavg200_index not in trader_data:
                    trader_data[prev_mavg200_index] = None

                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                # Append and maintain max 200-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 200:
                    prices.pop(0)

                orders = []

                # Only act if we have enough data
                if len(prices) >= 50:
                    mavg_50 = sum(prices[-50:]) / 50
                else:
                    mavg_50 = mid_price

                if len(prices) >= 200:
                    mavg_200 = sum(prices[-200:]) / 200
                else:
                    mavg_200 = mid_price


                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 2  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                # Save current SMA values for next round
                trader_data[prev_mavg50_index] = mavg_50
                trader_data[prev_mavg200_index] = mavg_200

                result[product] = orders

            if product == "DJEMBES":
                prices_index = "djemes_prices"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max 200-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 200:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 1.5  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                result[product] = orders

            if product == "JAMS":
                prices_index = "jams_prices"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max 200-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 200:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 1.5  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                result[product] = orders

        traderData = jsonpickle.encode(
            trader_data)  # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.

        conversions = 1
        return result, conversions, traderData
