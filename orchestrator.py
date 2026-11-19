"""Runs the specialist pipeline and records activity."""

from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
import pandas as pd

from agents import (DataQualityAgent, OrderRiskAgent, RevenueAgent,
                    FraudAgent, InventoryAgent, FinanceAgent, ExecutiveAgent)


def run_pipeline(df: pd.DataFrame, progress_callback=None):
    pipeline_start = perf_counter()
    activity = []
    outputs = {}

    def run(name, agent, payload):
        if progress_callback:
            progress_callback(name, "running")
        start = perf_counter()
        result = agent.run(payload)
        result["agent"] = name
        result["duration"] = round(perf_counter() - start, 4)
        activity.append(result)
        if progress_callback:
            progress_callback(name, result["status"])
        return name, result

    _, quality = run("Data Quality", DataQualityAgent(), {"data": df})
    outputs["Data Quality"] = quality
    missing = quality["key_results"].get("missing_columns", [])
    if missing:
        cleaned = df
    else:
        cleaned = quality["key_results"]["clean_data"]

    # Parallel risk and revenue analysis
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(run, "Order Risk", OrderRiskAgent(), {"data": cleaned}),
            pool.submit(run, "Revenue", RevenueAgent(), {"data": cleaned}),
        ]
        for future in futures:
            name, result = future.result()
            outputs[name] = result

    for name, agent in [
        ("Fraud", FraudAgent()),
        ("Inventory", InventoryAgent()),
        ("Finance", FinanceAgent()),
    ]:
        _, result = run(name, agent, {"data": cleaned})
        outputs[name] = result

    _, executive = run("Executive Decision", ExecutiveAgent(),
                       {"data": cleaned, "agent_outputs": outputs})
    outputs["Executive Decision"] = executive

    return {
        "outputs": outputs,
        "activity": sorted(activity, key=lambda x: x["agent"]),
        "total_time": round(perf_counter() - pipeline_start, 4),
        "cleaned_data": cleaned,
    }
