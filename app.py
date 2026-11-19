import os
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from orchestrator import run_pipeline
from engine.db import init_db, get_all_orders, update_approval_status
from utils.reports import build_excel_report, build_pdf_report


DATA_PATH = Path(__file__).parent / "data" / "synthetic_amazon_orders.csv"
SYNTHETIC_BANNER = "SYNTHETIC DEMONSTRATION DATA — education only; no real payments or refunds"

st.set_page_config(page_title="Agent Gatekeeper", layout="wide")
st.markdown(
    "<div style='background:#b12704;color:white;padding:10px;text-align:center;"
    "font-weight:700;'>⚠️ SYNTHETIC DEMONSTRATION DATA — MBA Evaluation System</div>",
    unsafe_allow_html=True,
)
st.title("Amazon India Agent Gatekeeper")
st.caption("Student: Aryan Thakur | Enrolment: PGD202566017 | Host: Amazon India")

init_db()

menu = st.sidebar.radio(
    "Navigation",
    ["Executive Overview", "Upload Data", "Agent Activity Centre",
     "Specialist Findings", "Executive Decision Report", "Approval Centre"],
)

@st.cache_data
def load_synthetic():
    lines = [line for line in DATA_PATH.read_text(encoding="utf-8").splitlines()
             if not line.startswith("#")]
    return pd.read_csv(pd.io.common.StringIO("\n".join(lines)))


if "analysis" not in st.session_state:
    st.session_state.analysis = run_pipeline(load_synthetic())

analysis = st.session_state.analysis
df = analysis["cleaned_data"]

if menu == "Upload Data":
    st.subheader("Upload Data")
    uploaded = st.file_uploader("Upload a CSV", type=["csv"])
    if uploaded:
        try:
            candidate = pd.read_csv(uploaded)
            required = {"order_id", "customer_id", "order_amount", "has_id_proof",
                        "refund_requested", "previous_refunds", "stock_available"}
            missing = sorted(required - set(candidate.columns))
            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            else:
                candidate["has_id_proof"] = candidate["has_id_proof"].astype(str).str.lower().isin(["true", "1", "yes"])
                candidate["refund_requested"] = candidate["refund_requested"].astype(str).str.lower().isin(["true", "1", "yes"])
                candidate["stock_available"] = candidate["stock_available"].astype(str).str.lower().isin(["true", "1", "yes"])
                if st.button("Run analysis"):
                    st.session_state.analysis = run_pipeline(candidate)
                    st.success("Analysis completed.")
        except Exception as exc:
            st.error(f"Upload could not be parsed: {exc}")

elif menu == "Executive Overview":
    st.subheader("Executive Overview")
    outputs = analysis["outputs"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows analysed", len(df))
    c2.metric("Total order value", f"Rs. {outputs['Revenue']['key_results']['total_order_value']:,.2f}")
    c3.metric("Missing-ID orders", outputs["Order Risk"]["key_results"]["missing_id_orders"])
    c4.metric("Suspected fraud", outputs["Fraud"]["key_results"]["suspected_fraud_orders"])

    chart_df = df.copy()
    chart_df["risk_segment"] = chart_df.apply(
        lambda r: "Missing ID" if not r["has_id_proof"]
        else ("High value" if r["order_amount"] > 5000
              else ("Out of stock" if not r["stock_available"] else "Standard")),
        axis=1,
    )
    fig = px.histogram(chart_df, x="risk_segment", color="risk_segment",
                       title="Orders by risk segment")
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Agent Activity Centre":
    st.subheader("Agent Activity Centre")
    for item in analysis["activity"]:
        with st.expander(f"{item['agent']} — {item['status']} ({item['duration']} s)", expanded=False):
            st.write("Key results:")
            st.json({k: v for k, v in item["key_results"].items()
                     if k != "clean_data"}, expanded=True)

elif menu == "Specialist Findings":
    st.subheader("Specialist Findings")
    selected = st.selectbox("Agent", ["Order Risk", "Revenue", "Fraud", "Inventory", "Finance", "Data Quality"])
    st.json(analysis["outputs"][selected]["key_results"])

elif menu == "Executive Decision Report":
    st.subheader("Executive Decision Report")
    executive = analysis["outputs"]["Executive Decision"]["key_results"]
    for index, rec in enumerate(executive["recommendations"], start=1):
        st.markdown(f"### {index}. {rec['title']}")
        st.write(rec["description"])
        st.caption(f"Priority: {rec['priority']} | Expected impact: {rec['expected_impact']}")
    st.subheader("Conflicts")
    st.write(executive["conflicts"] or ["No material disagreement detected."])
    st.subheader("Assumptions")
    st.write("\n".join(f"- {item}" for item in executive["assumptions"]))

    excel_file = build_excel_report(analysis)
    pdf_file = build_pdf_report(analysis)
    c1, c2 = st.columns(2)
    c1.download_button("Download Excel", excel_file,
                       "management_report.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    c2.download_button("Download PDF", pdf_file,
                       "management_report.pdf", "application/pdf")

elif menu == "Approval Centre":
    st.subheader("Approval Centre")
    orders = get_all_orders(200)
    pending = [o for o in orders if o["approval_status"] == "PENDING_REVIEW"]
    st.caption(f"{len(pending)} orders pending human approval")

    for order in pending:
        c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
        c1.write(f"{order['order_id']} — Rs. {order['order_amount']:,.2f}")
        c2.write(order["customer_id"])
        if c3.button("Approve", key=f"a-{order['order_id']}"):
            update_approval_status(order["order_id"], "APPROVE")
            st.rerun()
        if c4.button("Reject", key=f"r-{order['order_id']}"):
            update_approval_status(order["order_id"], "REJECT")
            st.rerun()
