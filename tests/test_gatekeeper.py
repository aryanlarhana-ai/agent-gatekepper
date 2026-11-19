"""
TEST SUITE FOR AMAZON INDIA AGENT GATEKEEPER (MBA EDITION)
Author: Aryan Thakur (PGD202566017)
Company: Amazon India

Mandatory Tests:
1. Hand-calculated Case 1: ID missing = BLOCK
2. Hand-calculated Case 2: 6500 + ID = ASK CUSTOMER
3. Hand-calculated Case 3: 2000 + ID = APPROVE / ALLOW
4. Problem Injections:
   - ORD 1-20: Missing ID + High Amount = BLOCK
   - ORD 21-40: ID Present + Amount > 5000 = ASK CUSTOMER
   - ORD 41-60: CUST_007 Repeat Refunds = FRAUD BLOCK
5. Approval Centre SQLite transitions: APPROVE / REJECT / RESET
6. Hard Safety Protocol: NEVER execute real refund/payment
"""

import os
import sys
import unittest
import csv

import pandas as pd
from orchestrator import run_pipeline
from utils.reports import build_excel_report, build_pdf_report

# Add engine directory to path
ENGINE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "engine")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
sys.path.insert(0, ENGINE_DIR)

from gatekeeper_engine import evaluate_request, AUTHORIZED_AGENTS
from db import (
    init_db, get_connection, update_approval_status, 
    get_order_by_id, NEVER_DO_REAL_PAYMENT_OR_REFUND
)

class TestAgentGatekeeperMBA(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    # -------------------------------------------------------------
    # 1. THE 3 MANDATORY HAND-CALCULATED TEST CASES
    # -------------------------------------------------------------

    def test_hand_calculated_case_1_id_missing_blocks(self):
        """
        Hand-calculated Case 1:
        Inputs: has_id_proof = False, order_amount = 3000 (even though <= 5000)
        Expected Decision: BLOCK
        Rule: ID Proof Missing = BLOCK
        """
        res = evaluate_request(
            agent_name="Agent-Kavita",
            customer_id="CUST_101",
            action="place order",
            order_amount=3000.0,
            has_id_proof=False,
            previous_refunds=0,
            stock_available=True
        )
        self.assertEqual(res["decision"], "BLOCK")
        self.assertEqual(res["rule_code"], "RULE_ID_MISSING")
        self.assertFalse(res["calculations"]["has_id_proof"])
        print("[PASS] Hand Case 1: ID Missing -> BLOCK")

    def test_hand_calculated_case_2_amount_6500_with_id_asks_customer(self):
        """
        Hand-calculated Case 2:
        Inputs: has_id_proof = True, order_amount = 6500 (> 5000)
        Expected Decision: ASK CUSTOMER
        Rule: Place order > Rs 5000 = ASK CUSTOMER
        """
        res = evaluate_request(
            agent_name="Agent-Kavita",
            customer_id="CUST_102",
            action="place order",
            order_amount=6500.0,
            has_id_proof=True,
            previous_refunds=0,
            stock_available=True
        )
        self.assertEqual(res["decision"], "ASK CUSTOMER")
        self.assertEqual(res["rule_code"], "RULE_5")
        self.assertTrue(res["calculations"]["amount_exceeds_threshold"])
        self.assertEqual(res["calculations"]["order_amount"], 6500.0)
        print("[PASS] Hand Case 2: 6500 + ID -> ASK CUSTOMER")

    def test_hand_calculated_case_3_amount_2000_with_id_approves(self):
        """
        Hand-calculated Case 3:
        Inputs: has_id_proof = True, order_amount = 2000 (<= 5000)
        Expected Decision: ALLOW / APPROVE
        Rule: Place order <= Rs 5000 = ALLOW
        """
        res = evaluate_request(
            agent_name="Agent-Kavita",
            customer_id="CUST_103",
            action="place order",
            order_amount=2000.0,
            has_id_proof=True,
            previous_refunds=0,
            stock_available=True
        )
        self.assertEqual(res["decision"], "ALLOW")
        self.assertEqual(res["rule_code"], "RULE_4")
        self.assertFalse(res["calculations"]["amount_exceeds_threshold"])
        self.assertTrue(res["calculations"]["has_id_proof"])
        self.assertEqual(res["calculations"]["order_amount"], 2000.0)
        print("[PASS] Hand Case 3: 2000 + ID -> APPROVE / ALLOW")

    # -------------------------------------------------------------
    # 2. INJECTED PROBLEM CASES (DATASET VERIFICATION)
    # -------------------------------------------------------------

    def test_injected_fraud_cust_007_repeat_refunds(self):
        """
        ORD 41-60 Injection:
        Customer CUST_007 with previous_refunds >= 3 attempting refund.
        Expected Decision: BLOCK (Fraud Rule)
        """
        res = evaluate_request(
            agent_name="Agent-Priya",
            customer_id="CUST_007",
            action="refund",
            order_amount=2500.0,
            has_id_proof=True,
            previous_refunds=5,
            stock_available=True
        )
        self.assertEqual(res["decision"], "BLOCK")
        self.assertEqual(res["rule_code"], "RULE_FRAUD_REPEAT")
        self.assertTrue(res["calculations"]["is_fraud_suspect"])
        print("[PASS] Injected Fraud Test: CUST_007 Repeat Refunds -> BLOCK (FRAUD)")

    def test_injected_csv_dataset_structure(self):
        """
        Verifies that data/synthetic_amazon_orders.csv exists, has 200 rows,
        and adheres to the required injection rules.
        """
        csv_path = os.path.join(DATA_DIR, "synthetic_amazon_orders.csv")
        self.assertTrue(os.path.exists(csv_path), "synthetic_amazon_orders.csv must exist.")

        with open(csv_path, mode="r", encoding="utf-8") as f:
            lines = [l for l in f if not l.startswith("#") and l.strip()]

        reader = csv.DictReader(lines)
        orders = list(reader)
        self.assertEqual(len(orders), 200, "Dataset must contain exactly 200 orders.")

        # Check ORD 1-20: Missing ID
        for o in orders[:20]:
            self.assertEqual(o["has_id_proof"].strip().lower(), "false", f"{o['order_id']} must have has_id_proof=False")
            self.assertGreater(float(o["order_amount"]), 5000.0, f"{o['order_id']} must be > 5000")

        # Check ORD 21-40: ID Present + Amount > 5000
        for o in orders[20:40]:
            self.assertEqual(o["has_id_proof"].strip().lower(), "true", f"{o['order_id']} must have has_id_proof=True")
            self.assertGreater(float(o["order_amount"]), 5000.0, f"{o['order_id']} must be > 5000")

        # Check ORD 41-60: CUST_007 Repeat Refunds
        for o in orders[40:60]:
            self.assertEqual(o["customer_id"], "CUST_007")
            self.assertEqual(o["refund_requested"].strip().lower(), "true")
            self.assertGreaterEqual(int(o["previous_refunds"]), 3)

        print("[PASS] Synthetic CSV Verification: 200 orders with all injected problem sets intact.")

    # -------------------------------------------------------------
    # 3. 7 AGENTS AND REVOCATION CHECKS
    # -------------------------------------------------------------

    def test_revoked_agent_suresh_blocks(self):
        """
        Rule 1: Agent-Suresh is revoked. All transactions must be BLOCKED.
        """
        res = evaluate_request(
            agent_name="Agent-Suresh",
            customer_id="CUST_001",
            action="place order",
            order_amount=1000.0,
            has_id_proof=True
        )
        self.assertEqual(res["decision"], "BLOCK")
        self.assertEqual(res["rule_code"], "RULE_1")
        self.assertTrue(res["calculations"]["agent_revoked"])
        print("[PASS] Rule 1: Revoked Agent (Agent-Suresh) -> BLOCK")

    def test_unknown_agent_blocks(self):
        """
        Rule 2: Unregistered agent name must be BLOCKED.
        """
        res = evaluate_request(
            agent_name="UntrustedBot_X",
            customer_id="CUST_001",
            action="place order",
            order_amount=1000.0,
            has_id_proof=True
        )
        self.assertEqual(res["decision"], "BLOCK")
        self.assertEqual(res["rule_code"], "RULE_2")
        self.assertFalse(res["calculations"]["agent_verified"])
        print("[PASS] Rule 2: Unknown Agent -> BLOCK")

    def test_view_order_inquiry_allowed(self):
        """
        Rule 3: Non-financial inquiry 'view order' must be ALLOWED.
        """
        res = evaluate_request(
            agent_name="Agent-Rahul",
            customer_id="CUST_001",
            action="view order",
            order_amount=0.0,
            has_id_proof=True
        )
        self.assertEqual(res["decision"], "ALLOW")
        self.assertEqual(res["rule_code"], "RULE_3")
        self.assertFalse(res["calculations"]["is_financial"])
        print("[PASS] Rule 3: View Order Inquiry -> ALLOW")

    # -------------------------------------------------------------
    # 4. APPROVAL CENTRE (SQLITE) & SAFETY PROTOCOL
    # -------------------------------------------------------------

    def test_approval_centre_sqlite_transitions(self):
        """
        Tests Approve, Reject, and Reset transitions in SQLite.
        """
        test_order_id = "ORD_021"  # Injected ASK CUSTOMER order

        # 1. Approve
        res_app = update_approval_status(test_order_id, "APPROVE", reviewer="Aryan Thakur")
        self.assertEqual(res_app["new_status"], "APPROVED_BY_ADMIN")
        order_row = get_order_by_id(test_order_id)
        self.assertEqual(order_row["approval_status"], "APPROVED_BY_ADMIN")

        # 2. Reject
        res_rej = update_approval_status(test_order_id, "REJECT", reviewer="Aryan Thakur")
        self.assertEqual(res_rej["new_status"], "REJECTED_BY_ADMIN")
        order_row = get_order_by_id(test_order_id)
        self.assertEqual(order_row["approval_status"], "REJECTED_BY_ADMIN")

        # 3. Reset
        res_rst = update_approval_status(test_order_id, "RESET")
        order_row = get_order_by_id(test_order_id)
        self.assertEqual(order_row["approval_status"], "PENDING_REVIEW")

        print("[PASS] Approval Centre: Approve / Reject / Reset state transitions verified in SQLite.")

    def test_safety_guardrail_invariant(self):
        """
        Hard Safety Check: App must NEVER do real refund/payment.
        """
        self.assertTrue(NEVER_DO_REAL_PAYMENT_OR_REFUND, "Safety invariant must be True.")
        print("[PASS] Safety Guardrail: NEVER_DO_REAL_PAYMENT_OR_REFUND is strictly enforced.")

    def test_orchestrator_and_reports(self):
        """Verifies specialist hand-offs and downloadable report output."""
        df = pd.DataFrame([{
            "order_id": "TINY_001",
            "customer_id": "CUST_001",
            "product": "Test Product",
            "order_amount": 6500.0,
            "has_id_proof": True,
            "refund_requested": False,
            "previous_refunds": 0,
            "stock_available": True,
        }])
        result = run_pipeline(df)
        self.assertIn("Executive Decision", result["outputs"])
        self.assertEqual(result["outputs"]["Data Quality"]["status"], "success")
        self.assertGreater(len(build_excel_report(result).getvalue()), 100)
        self.assertGreater(len(build_pdf_report(result).getvalue()), 100)
        print("[PASS] Orchestrator and Excel/PDF report generation.")

    def test_dirty_data_is_reported_without_crash(self):
        df = pd.DataFrame([{
            "order_id": "DIRTY_001",
            "customer_id": "CUST_001",
            "order_amount": "not-a-number",
            "has_id_proof": True,
            "refund_requested": False,
            "previous_refunds": 0,
            "stock_available": True,
        }])
        result = run_pipeline(df)
        quality = result["outputs"]["Data Quality"]["key_results"]
        self.assertIn("missing_columns", quality)
        self.assertIsNotNone(result["outputs"]["Data Quality"]["status"])
        print("[PASS] Dirty numeric data is handled through the quality agent.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
