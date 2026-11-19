from .base_agent import BaseAgent


class RevenueAgent(BaseAgent):
    name = "Revenue"

    def calculate(self, payload):
        df = payload["data"]
        total = float(df["order_amount"].sum())
        average = float(df["order_amount"].mean()) if len(df) else 0.0
        return {"total_order_value": total, "average_order_value": average}
