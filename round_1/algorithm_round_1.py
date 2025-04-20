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
            # if product == "KELP":
            #     if "kelp_prices" not in trader_data:
            #         trader_data["kelp_prices"] = []
            #
            #     if "prev_mavg50" not in trader_data:
            #         trader_data["prev_mavg50"] = None
            #     if "prev_mavg200" not in trader_data:
            #         trader_data["prev_mavg200"] = None
            #
            #     if "sum_200" not in trader_data:
            #         trader_data["sum_200"] = 0.0
            #     if "sum_50" not in trader_data:
            #         trader_data["sum_50"] = 0.0
            #
            #     order_depth: OrderDepth = state.order_depths[product]
            #     mid_price = self.get_mid_price(order_depth)
            #
            #     prices = trader_data["kelp_prices"]
            #     len_prices = len(prices)
            #
            #     # Update rolling sums BEFORE adding new price
            #     if len_prices >= MAX_WINDOW_LENGTH:
            #         old_price = prices.pop(0)
            #         trader_data["sum_200"] -= old_price
            #         if len_prices >= 50:
            #             trader_data["sum_50"] -= old_price
            #
            #     prices.append(mid_price)
            #     trader_data["sum_200"] += mid_price
            #     if len_prices > 150:  # Only start 50-day sum when we’ve got enough data
            #         trader_data["sum_50"] += mid_price
            #
            #     mavg_200 = trader_data["sum_200"] / 200 if len_prices > 0 else mid_price
            #     mavg_50 = trader_data["sum_50"] / 50 if len_prices >= 50 else mid_price
            #
            #     orders: List[Order] = []
            #
            #     # --- Cross detection ---
            #     prev_50 = trader_data["prev_mavg50"]
            #     prev_200 = trader_data["prev_mavg200"]
            #
            #     if prev_50 is not None and prev_200 is not None:
            #         # Bullish crossover: 50 crosses ABOVE 200
            #         if prev_50 < prev_200 and mavg_50 > mavg_200:
            #             if len(order_depth.sell_orders) > 0:
            #                 best_ask, ask_volume = min(order_depth.sell_orders.items())
            #                 print("📈 BULLISH CROSSOVER! BUY", -ask_volume, "at", best_ask)
            #                 orders.append(Order(product, best_ask, -ask_volume))
            #
            #         # Bearish crossover: 50 crosses BELOW 200
            #         if prev_50 > prev_200 and mavg_50 < mavg_200:
            #             if len(order_depth.buy_orders) > 0:
            #                 best_bid, bid_volume = max(order_depth.buy_orders.items())
            #                 print("📉 BEARISH CROSSOVER! SELL", bid_volume, "at", best_bid)
            #                 orders.append(Order(product, best_bid, -bid_volume))
            #
            #     # Store current for next round
            #     trader_data["prev_mavg50"] = mavg_50
            #     trader_data["prev_mavg200"] = mavg_200
            #
            #
            #     # Momentum / Breakout bands
            #     # We use the mid-price and the mean and max of historical prices
            #     # We buy or sell to see if the highest high or the lowest low has been broken
            #     # if len(order_depth.sell_orders) != 0:
            #     #     best_ask, ask_volume = min(order_depth.sell_orders.items())
            #     #     if best_ask > highest_price:  # breakout upward
            #     #         print("BUY breakout", str(-ask_volume) + "x", best_ask)
            #     #         orders.append(Order(product, best_ask, -ask_volume))
            #     #
            #     # if len(order_depth.buy_orders) != 0:
            #     #     best_bid, bid_volume = max(order_depth.buy_orders.items())
            #     #     if best_bid < lowest_price:  # breakout downward
            #     #         print("SELL breakout", str(bid_volume) + "x", best_bid)
            #     #         orders.append(Order(product, best_bid, -bid_volume))
            #
            #     trader_data["kelp_prices"].append(mid_price)
            #
            #     # Reversal
            #     # std_dev = 2
            #     # if len(trader_data["kelp_prices"]) > 2:
            #     #     std_dev = statistics.stdev(trader_data["kelp_prices"])
            #     #
            #     # if len(order_depth.sell_orders) != 0:
            #     #     best_ask, ask_volume = min(order_depth.sell_orders.items())
            #     #     if mid_price + std_dev < best_ask:
            #     #         print("BUY reversal", str(-ask_volume) + "x", best_ask)
            #     #         orders.append(Order(product, best_ask, -ask_volume))
            #     #
            #     # if len(order_depth.buy_orders) != 0:
            #     #     best_bid, bid_volume = max(order_depth.buy_orders.items())
            #     #     if mid_price - std_dev > best_bid:
            #     #         print("SELL reversal", str(bid_volume) + "x", best_bid)
            #     #         orders.append(Order(product, best_bid, -bid_volume))
            #
            #     # SMA
            #     # if len(trader_data["kelp_prices"]) != 0:
            #     #     mean_price = sum(trader_data["kelp_prices"]) / len(trader_data["kelp_prices"])
            #     #     spread = 2
            #     #     bid_threshold = mean_price - spread
            #     #     ask_threshold = mean_price + spread
            #     #
            #     # if len(order_depth.sell_orders) != 0:
            #     #     best_ask, ask_volume = min(order_depth.sell_orders.items())
            #     #     if int(best_ask) <= bid_threshold:  # breakout upward
            #     #         print("BUY breakout", str(-ask_volume) + "x", best_ask)
            #     #         orders.append(Order(product, best_ask, -ask_volume))
            #     #
            #     # if len(order_depth.buy_orders) != 0:
            #     #     best_bid, bid_volume = max(order_depth.buy_orders.items())
            #     #     if int(best_bid) <= ask_threshold: # breakout downward
            #     #         print("SELL breakout", str(bid_volume) + "x", best_bid)
            #     #         orders.append(Order(product, best_bid, -bid_volume))
            #
            #     result[product] = orders
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

                # if imbalance > imbalance_threshold and len(order_depth.sell_orders) > 0:
                #     best_ask, ask_volume = min(order_depth.sell_orders.items())
                #     print("BUY on imbalance", str(-ask_volume) + "x", best_ask)
                #     orders.append(Order(product, best_ask, -ask_volume))
                #
                # elif imbalance < -imbalance_threshold and len(order_depth.buy_orders) > 0:
                #     best_bid, bid_volume = max(order_depth.buy_orders.items())
                #     print("SELL on imbalance", str(bid_volume) + "x", best_bid)
                #     orders.append(Order(product, best_bid, -bid_volume))

                result[product] = orders

        traderData = jsonpickle.encode(
            trader_data)  # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.

        conversions = 1
        return result, conversions, traderData
