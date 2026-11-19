from .base_agent import BaseAgent


class InventoryAgent(BaseAgent):
    name = "Inventory"

    def calculate(self, payload):
        df = payload["data"]
        out = df[~df["stock_available"].astype(bool)]
        return {"out_of_stock_orders": int(len(out)), "order_ids": out["order_id"].head(20).tolist()}
