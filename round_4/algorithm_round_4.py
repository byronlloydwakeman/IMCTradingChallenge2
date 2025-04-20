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

        print("traderData: " + state.traderData)
        trader_data = jsonpickle.decode(state.traderData) if state.traderData else {}
        observation_data = state.observations if state.observations else {}
        conversions_observations = observation_data.conversionObservations if observation_data.conversionObservations else {}

        print("Observations: " + str(observation_data))
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

            # if product == "PICNIC_BASKET1":
            #     if "picnic_basket1_prices" not in trader_data:
            #         trader_data["picnic_basket1_prices"] = []
            #
            #     if "prev_pb1_mavg50" not in trader_data:
            #         trader_data["prev_pb1_mavg50"] = None
            #     if "prev_pb1_mavg200" not in trader_data:
            #         trader_data["prev_pb1_mavg200"] = None
            #
            #     order_depth = state.order_depths[product]
            #     mid_price = self.get_mid_price(order_depth)
            #
            #     # Append and maintain max 200-length history
            #     prices = trader_data["picnic_basket1_prices"]
            #     prices.append(mid_price)
            #     if len(prices) > 200:
            #         prices.pop(0)
            #
            #     orders = []
            #
            #     # Only act if we have enough data
            #     if len(prices) >= 50:
            #         mavg_50 = sum(prices[-50:]) / 50
            #     else:
            #         mavg_50 = mid_price
            #
            #     if len(prices) >= 200:
            #         mavg_200 = sum(prices[-200:]) / 200
            #     else:
            #         mavg_200 = mid_price
            #
            #     prev_50 = trader_data["prev_pb1_mavg50"]
            #     prev_200 = trader_data["prev_pb1_mavg200"]
            #
            #     if prev_50 is not None and prev_200 is not None:
            #         if prev_50 < prev_200 and mavg_50 > mavg_200:
            #             if len(order_depth.buy_orders) > 0:
            #                 best_bid, bid_volume = max(order_depth.buy_orders.items())
            #                 print("GOLDEN CROSS on PICNIC_BASKET1! SO SELL?", bid_volume, "at", best_bid)
            #                 orders.append(Order(product, best_bid, -bid_volume))
            #
            #         elif prev_50 > prev_200 and mavg_50 < mavg_200:
            #             if len(order_depth.sell_orders) > 0:
            #                 best_ask, ask_volume = min(order_depth.sell_orders.items())
            #                 print("DEATH CROSS on PICNIC_BASKET1! SO BUY?", -ask_volume, "at", best_ask)
            #                 orders.append(Order(product, best_ask, -ask_volume))
            #
            #     # Save current SMA values for next round
            #     trader_data["prev_pb1_mavg50"] = mavg_50
            #     trader_data["prev_pb1_mavg200"] = mavg_200
            #
            #     result[product] = orders

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

            # if product == "PICNIC_BASKET2":
            #     picnic_basket2_prices_index = "picnic_basket2_prices"
            #     prev_pb2_mavg50_index = "prev_pb2_mavg50"
            #     prev_pb2_mavg200_index = "prev_pb2_mavg200"
            #
            #     if picnic_basket2_prices_index not in trader_data:
            #         trader_data[picnic_basket2_prices_index] = []
            #
            #     if prev_pb2_mavg50_index not in trader_data:
            #         trader_data[prev_pb2_mavg50_index] = None
            #     if prev_pb2_mavg200_index not in trader_data:
            #         trader_data[prev_pb2_mavg200_index] = None
            #
            #     order_depth = state.order_depths[product]
            #     mid_price = self.get_mid_price(order_depth)
            #
            #     # Append and maintain max 200-length history
            #     prices = trader_data[picnic_basket2_prices_index]
            #     prices.append(mid_price)
            #     if len(prices) > 200:
            #         prices.pop(0)
            #
            #     orders = []
            #
            #     # Only act if we have enough data
            #     if len(prices) >= 50:
            #         mavg_50 = sum(prices[-50:]) / 50
            #     else:
            #         mavg_50 = mid_price
            #
            #     if len(prices) >= 200:
            #         mavg_200 = sum(prices[-200:]) / 200
            #     else:
            #         mavg_200 = mid_price
            #
            #     prev_50 = trader_data[prev_pb2_mavg50_index]
            #     prev_200 = trader_data[prev_pb2_mavg200_index]
            #
            #     if prev_50 is not None and prev_200 is not None:
            #         if prev_50 < prev_200 and mavg_50 > mavg_200:
            #             if len(order_depth.buy_orders) > 0:
            #                 best_bid, bid_volume = max(order_depth.buy_orders.items())
            #                 print("GOLDEN CROSS on PICNIC_BASKET1! SO SELL?", bid_volume, "at", best_bid)
            #                 orders.append(Order(product, best_bid, -bid_volume))
            #
            #         elif prev_50 > prev_200 and mavg_50 < mavg_200:
            #             if len(order_depth.sell_orders) > 0:
            #                 best_ask, ask_volume = min(order_depth.sell_orders.items())
            #                 print("DEATH CROSS on PICNIC_BASKET1! SO BUY?", -ask_volume, "at", best_ask)
            #                 orders.append(Order(product, best_ask, -ask_volume))
            #
            #
            #
            #     # Save current SMA values for next round
            #     trader_data[prev_pb2_mavg50_index] = mavg_50
            #     trader_data[prev_pb2_mavg200_index] = mavg_200
            #
            #     result[product] = orders

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

                prev_50 = trader_data[prev_mavg50_index]
                prev_200 = trader_data[prev_mavg200_index]

                # if prev_50 is not None and prev_200 is not None:
                #     if prev_50 < prev_200 and mavg_50 > mavg_200:
                #         if len(order_depth.buy_orders) > 0:
                #             best_bid, bid_volume = max(order_depth.buy_orders.items())
                #             print("GOLDEN CROSS on PICNIC_BASKET1! SO SELL?", bid_volume, "at", best_bid)
                #             orders.append(Order(product, best_bid, -bid_volume))
                #
                #     elif prev_50 > prev_200 and mavg_50 < mavg_200:
                #         if len(order_depth.sell_orders) > 0:
                #             best_ask, ask_volume = min(order_depth.sell_orders.items())
                #             print("DEATH CROSS on PICNIC_BASKET1! SO BUY?", -ask_volume, "at", best_ask)
                #             orders.append(Order(product, best_ask, -ask_volume))

                bid_threshold = 4310  # Participant should calculate this value
                ask_threshold = 4330

                # SMA
                # if len(trader_data[prices_index]) != 0:
                #     mean_price = sum(trader_data[prices_index]) / len(trader_data[prices_index])
                #     spread = 10
                #     bid_threshold = mean_price - spread
                #     ask_threshold = mean_price + spread
                #
                # if len(order_depth.sell_orders) != 0:
                #     best_ask, ask_volume = min(order_depth.sell_orders.items())
                #     if int(best_ask) <= bid_threshold:  # breakout upward
                #         print("BUY breakout", str(-ask_volume) + "x", best_ask)
                #         orders.append(Order(product, best_ask, -ask_volume))
                #
                # if len(order_depth.buy_orders) != 0:
                #     best_bid, bid_volume = max(order_depth.buy_orders.items())
                #     if int(best_bid) <= ask_threshold: # breakout downward
                #         print("SELL breakout", str(bid_volume) + "x", best_bid)
                #         orders.append(Order(product, best_bid, -bid_volume))

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

            if product == "VOLCANIC_ROCK":
                prices_index = "volcanic_rock"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max x-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 50:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 0.8  # You can tweak this to make the strategy more/less aggressive

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

            if product == "VOLCANIC_ROCK_VOUCHER_10000":
                prices_index = "volcanic_rock_voucher_10000"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max x-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 50:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 0.8  # You can tweak this to make the strategy more/less aggressive

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

            if product == "VOLCANIC_ROCK_VOUCHER_10250":
                prices_index = "volcanic_rock_voucher_10250"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max x-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 50:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 0.8  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(
                                Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(
                                Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                result[product] = orders

            if product == "VOLCANIC_ROCK_VOUCHER_10500":
                prices_index = "volcanic_rock_voucher_10500"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max x-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 50:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 0.8  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(
                                Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(
                                Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                result[product] = orders

            if product == "VOLCANIC_ROCK_VOUCHER_9500":
                prices_index = "volcanic_rock_voucher_9500"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max x-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 50:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 0.8  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(
                                Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(
                                Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                result[product] = orders

            if product == "VOLCANIC_ROCK_VOUCHER_9750":
                prices_index = "volcanic_rock_voucher_9750"
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Append and maintain max x-length history
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 50:
                    prices.pop(0)

                orders = []

                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                # Mean Reversion Strategy
                if len(trader_data[prices_index]) >= 20:
                    mean_price = sum(prices) / len(prices)
                    variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
                    std_dev = variance ** 0.5

                    z_score = 0.8  # You can tweak this to make the strategy more/less aggressive

                    if len(order_depth.sell_orders) > 0:
                        best_ask, ask_volume = min(order_depth.sell_orders.items())
                        if best_ask < mean_price - z_score * std_dev:
                            print(
                                f"BUY (mean reversion): {ask_volume} @ {best_ask}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(
                                Order(product, best_ask, min(ask_volume, 10)))  # Cap volume to reduce risk

                    if len(order_depth.buy_orders) > 0:
                        best_bid, bid_volume = max(order_depth.buy_orders.items())
                        if best_bid > mean_price + z_score * std_dev:
                            print(
                                f"SELL (mean reversion): {bid_volume} @ {best_bid}, mean={mean_price:.2f}, std={std_dev:.2f}")
                            orders.append(
                                Order(product, best_bid, -min(bid_volume, 10)))  # Cap volume to reduce risk

                result[product] = orders

            if product == "MACARON":
                prices_index = "macaron_prices"
                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                orders = []

                # Parameters
                CSI = 41
                z_score = 1.5
                position_limit = 75
                max_trade_size = 10  # To avoid big slippage and storage costs
                position = state.position.get(product, 0)
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                # Track prices for mean reversion
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 200:
                    prices.pop(0)

                mean_price = sum(prices) / len(prices)
                std_dev = (sum((p - mean_price) ** 2 for p in prices) / len(prices)) ** 0.5 if len(prices) > 1 else 1

                # Get market data
                best_ask, ask_volume = min(order_depth.sell_orders.items()) if order_depth.sell_orders else (None, 0)
                best_bid, bid_volume = max(order_depth.buy_orders.items()) if order_depth.buy_orders else (None, 0)

                # Get sunlight index
                sunlight_index = state.observations.get("sunlight", 100)  # Default high if not present
                print(f"sunlight {sunlight_index}")

                if sunlight_index < CSI:
                    # Bullish regime – expect price to go up, go long
                    if best_ask is not None and position < position_limit:
                        buy_volume = min(max_trade_size, ask_volume, position_limit - position)
                        orders.append(Order(product, best_ask, buy_volume))

                    # # Optionally sell at inflated prices
                    # if best_bid is not None and best_bid > mean_price + z_score * std_dev and position > -position_limit:
                    #     sell_volume = min(max_trade_size, bid_volume, position + position_limit)
                    #     orders.append(Order(product, best_bid, -sell_volume))

                else:
                    # Neutral regime – mean reversion
                    if best_ask is not None and best_ask < mean_price - z_score * std_dev and position < position_limit:
                        buy_volume = min(max_trade_size, ask_volume, position_limit - position)
                        orders.append(Order(product, best_ask, buy_volume))

                    if best_bid is not None and best_bid > mean_price + z_score * std_dev and position > -position_limit:
                        sell_volume = min(max_trade_size, bid_volume, position + position_limit)
                        orders.append(Order(product, best_bid, -sell_volume))

                result[product] = orders

            if "MAGNIFICENT_MACARONS" in conversions_observations:
                prices_index = "macaron_prices"
                if prices_index not in trader_data:
                    trader_data[prices_index] = []

                orders = []

                # === Parameters ===
                CSI = 60.0  # Adjust based on observed correlation
                position_limit = 75
                max_trade_size = 10
                z_score = 0.7

                position = state.position.get(product, 0)
                order_depth = state.order_depths[product]
                mid_price = self.get_mid_price(order_depth)

                # === Price history tracking ===
                prices = trader_data[prices_index]
                prices.append(mid_price)
                if len(prices) > 200:
                    prices.pop(0)

                mean_price = sum(prices) / len(prices)
                std_dev = (sum((p - mean_price) ** 2 for p in prices) / len(prices)) ** 0.5 if len(prices) > 1 else 1

                # === Orderbook data ===
                best_ask, ask_volume = min(order_depth.sell_orders.items()) if order_depth.sell_orders else (None, 0)
                best_bid, bid_volume = max(order_depth.buy_orders.items()) if order_depth.buy_orders else (None, 0)

                # === Observations: Sunlight + Sugar ===
                macarons_data = conversions_observations.get("MAGNIFICENT_MACARONS")
                sunlight_index = macarons_data.sunlightIndex
                sugar_price = macarons_data.sugarPrice
                transport_fee = macarons_data.transportFees
                import_tariff = macarons_data.importTariff
                export_tariff = macarons_data.exportTariff

                print(f"[MACARON] sun={sunlight_index:.2f}, sugar={sugar_price:.2f}, mid={mid_price:.2f}")

                # === Adjusted Prices for Import & Export ===
                effective_ask = best_ask + transport_fee + import_tariff if best_ask is not None else None
                effective_bid = best_bid - transport_fee - export_tariff if best_bid is not None else None

                # === Buy Logic (Importing) ===
                # if sunlight_index < CSI and sugar_price < 200:
                #     if best_ask is not None and position < position_limit:
                #         # If importing cost is below expected fair value
                #         if effective_ask < mean_price:
                #             buy_volume = min(max_trade_size, ask_volume, position_limit - position)
                #             orders.append(Order(product, best_ask, buy_volume))
                #             print(f"BUY: Bullish + low import cost @ {best_ask} (effective {effective_ask:.2f}) x{buy_volume}")
                #
                # else:
                    # Mean reversion buy (adjusted for import cost)
                if best_ask is not None and effective_ask < mean_price - z_score * std_dev and position < position_limit:
                    buy_volume = min(max_trade_size, ask_volume, position_limit - position)
                    orders.append(Order(product, best_ask, buy_volume))
                    print(f"BUY: Mean reversion @ {best_ask} (effective {effective_ask:.2f}) x{buy_volume}")

                # Mean reversion sell (adjusted for export cost)
                if best_bid is not None and effective_bid > mean_price + z_score * std_dev and position > -position_limit:
                    sell_volume = min(max_trade_size, bid_volume, position + position_limit)
                    orders.append(Order(product, best_bid, -sell_volume))
                    print(f"SELL: Mean reversion @ {best_bid} (effective {effective_bid:.2f}) x{sell_volume}")

                result[product] = orders

        traderData = jsonpickle.encode(
            trader_data)  # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.

        conversions = 1
        return result, conversions, traderData
