from .base_agent import BaseAgent


class FinanceAgent(BaseAgent):
    name = "Finance"

    def calculate(self, payload):
        df = payload["data"]
        risk_exposure = float(df[(df["order_amount"] > 5000) |
                                 (~df["has_id_proof"].astype(bool))]["order_amount"].sum())
        return {"gross_risk_exposure": risk_exposure}
