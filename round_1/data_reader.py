import csv

from round_1.datamodel import OrderDepth, TradingState


def parse_csv_to_trading_state(csv_file_path):
    with open(csv_file_path, 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            product = row['product']
            timestamp = int(row['timestamp'])

            # Convert bids and asks into dictionaries
            buy_orders = {}
            sell_orders = {}

            for i in range(1, 4):
                bid_price = int(row[f'bid_price_{i}'])
                bid_volume = int(row[f'bid_volume_{i}'])
                if bid_volume != 0:
                    buy_orders[bid_price] = bid_volume

                ask_price = int(row[f'ask_price_{i}'])
                ask_volume = int(row[f'ask_volume_{i}'])
                if ask_volume != 0:
                    sell_orders[ask_price] = ask_volume

            # Build OrderDepth
            order_depth = OrderDepth()
            order_depth.buy_orders = buy_orders
            order_depth.sell_orders = sell_orders

            # Create trading state for this tick
            state = TradingState(
                traderData="",
                timestamp=timestamp,
                listings={},
                order_depths={product: order_depth},
                own_trades={},
                market_trades={},
                position={},
                observations=None  # You can customize this if needed
            )

            yield state
