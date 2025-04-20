import csv
import matplotlib.pyplot as plt

from round_1.datamodel import TradingState, OrderDepth
from algorithm_round_1 import Trader

cash = 0
position = 0
realized_pnl = 0
timestamps = []
realized_pnl_values = []
unrealized_pnl_values = []
product_name = "RAINFOREST_RESIN"
orders_count = 0

def get_mid_price(order_depth):
    best_bid = max(order_depth.buy_orders.keys(), default=0)
    best_ask = min(order_depth.sell_orders.keys(), default=0)
    if best_bid and best_ask:
        return (best_bid + best_ask) / 2
    return 0

def simulate_trading_from_csv(csv_path, trader):
    global cash, position, realized_pnl, orders_count
    trader_data = ""

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            timestamp = int(row['timestamp'])
            product = row['product']

            # Reconstruct order book
            order_depth = OrderDepth()
            for i in range(1, 4):
                bid_price = row[f'bid_price_{i}']
                bid_volume = row[f'bid_volume_{i}']
                ask_price = row[f'ask_price_{i}']
                ask_volume = row[f'ask_volume_{i}']

                # Only convert to int if valid data exists
                if bid_price and bid_volume:
                    order_depth.buy_orders[int(bid_price)] = int(bid_volume)

                if ask_price and ask_volume:
                    order_depth.sell_orders[int(ask_price)] = int(ask_volume)

            # Create the TradingState object for this iteration
            state = TradingState(
                traderData=trader_data,
                timestamp=timestamp,
                listings={},
                order_depths={product: order_depth},
                own_trades={},
                market_trades={},
                position={product: position},
                observations=None
            )

            # Run the trader
            orders_by_product, conversions, trader_data = trader.run(state)
            # Get the rainforest trades
            orders = orders_by_product.get(product, [])

            for order in orders:
                print(order)
                if order.quantity > 0:
                    for ask_price in sorted(order_depth.sell_orders):
                        available_volume = order_depth.sell_orders[ask_price]
                        fill_qty = min(order.quantity, available_volume)
                        cash -= fill_qty * ask_price
                        position += fill_qty
                        order.quantity -= fill_qty
                        if order.quantity <= 0:
                            break
                elif order.quantity < 0:  # Less than 0 means sell
                    for bid_price in sorted(order_depth.buy_orders, reverse=True):
                        available_volume = order_depth.buy_orders[bid_price]
                        fill_qty = min(-order.quantity, available_volume)
                        cash += fill_qty * bid_price
                        position -= fill_qty
                        order.quantity += fill_qty
                        if order.quantity >= 0:
                            break


            mid_price = get_mid_price(order_depth)

            # Moolah made
            realized_pnl = cash + (position * mid_price)

            # if we were to sell at the current market price
            unrealized_pnl = position * mid_price

            timestamps.append(timestamp)
            realized_pnl_values.append(realized_pnl)
            unrealized_pnl_values.append(unrealized_pnl)

    print(f"Final Realized PnL: {realized_pnl:.2f}, Final Unrealized PnL: {unrealized_pnl:.2f}")
    print(f"Final Position: {position}, Cash: {cash:.2f}")

    # Plot
    plt.figure(figsize=(12, 5))
    plt.plot(timestamps, realized_pnl_values, label="Realized PnL", color='green')
    # plt.plot(timestamps, unrealized_pnl_values, label="Unrealized PnL", color='red')
    plt.xlabel("Timestamp")
    plt.ylabel("PnL")
    plt.title(f"Realized PnL for {product_name}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


trader = Trader()
simulate_trading_from_csv("round-1-island-bottle-data/prices_round_1_day_0.csv", trader)

