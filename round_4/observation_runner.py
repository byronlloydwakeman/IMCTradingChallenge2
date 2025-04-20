import csv
import jsonpickle
from dataclasses import dataclass
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from algorithm_round_4 import Trader  # Ensure this imports your actual `Trader` class

# === Step 1: Parse CSV Observation Data ===
def load_observation_data_from_csv(csv_path: str) -> List[dict]:
    observations = []
    with open(csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            obs = {
                "MAGNIFICENT_MACARONS": {
                    "bidPrice": float(row["bidPrice"]),
                    "askPrice": float(row["askPrice"]),
                    "transportFees": float(row["transportFees"]),
                    "exportTariff": float(row["exportTariff"]),
                    "importTariff": float(row["importTariff"]),
                    "sugarPrice": float(row["sugarPrice"]),
                    "sunlightIndex": float(row["sunlightIndex"])
                }
            }
            observations.append({
                "conversionObservations": obs
            })
    return observations

# === Step 3: Simulate TradingState per timestep ===
def simulate_trader_on_observations(csv_file_path: str):
    observations = load_observation_data_from_csv(csv_file_path)
    trader = Trader()
    dummy_position = {"MACARON": 0}
    dummy_trader_data = {}
    dummy_own_trades = {}
    dummy_market_trades = {}

    for timestamp, obs in enumerate(observations):
        mid_price = (obs["conversionObservations"]["MAGNIFICENT_MACARONS"]["bidPrice"] +
                     obs["conversionObservations"]["MAGNIFICENT_MACARONS"]["askPrice"]) / 2

        state = TradingState(
            traderData=jsonpickle.encode(dummy_trader_data),
            timestamp=timestamp * 100,  # match format
            listings={},
            order_depths={"MAGNIFICENT_MACARONS": ""},
            own_trades=dummy_own_trades,
            market_trades=dummy_market_trades,
            position=dummy_position,
            observations=jsonpickle.encode(obs)
        )

        result = trader.run(state)
        print(f"[t={state.timestamp}] Orders: {result.get('MACARON', [])}")

simulate_trader_on_observations("round_4_data/round-4-island-data-bottle/observations_round_4_day_1.csv")
