# PROJECT REPORT: AGENT GATEKEEPER FOR AMAZON INDIA (MBA EDITION)

**Academic Program:** Post Graduate Diploma / MBA  
**Student Name:** Aryan Thakur  
**Enrolment Number:** PGD202566017  
**Host Organization:** Amazon India (`Amazon.in`)  
**Submission Date:** November 2026  
**Repository Location:** `d:\agent-gatekeeper\`  
**GitHub Repository:** https://github.com/aryanlarhana-ai/agent-gatekepper

---

## 1. Executive Summary

Autonomous AI agents are transforming e-commerce customer journeys, from autonomous order replenishment to instant customer support returns and refunds. However, unfettered agent autonomy introduces significant financial exposure, regulatory compliance breaches (e.g., RBI 2-Factor Authentication and e-mandate guidelines in India), and vulnerability to rogue bots.

This report details the architectural enhancements made to **Agent Gatekeeper for Amazon India** to achieve **100% compliance with the MBA Project Guide**. Key additions include:
1. **Synthetic Demonstration Dataset (`data/generate_data.py`):** 200 synthetic Amazon orders in `data/synthetic_amazon_orders.csv` with mathematically injected edge cases.
2. **Persistent Demonstration Banner:** Universal notification indicating simulated, non-financial execution.
3. **Approval Centre (SQLite):** Human-in-the-loop review dashboard with Approve, Reject, and Reset workflows backed by SQLite (`data/gatekeeper_approval.db`), protected by a hard safety invariant preventing live payments.
4. **Strict Separation of Concerns:** Pure Python engine executes all calculations and rule evaluations; Gemini operates strictly as a natural language interpreter.
5. **Comprehensive Automated Test Suite (`tests/test_gatekeeper.py`):** Verified against 3 mandatory hand-calculated scenarios, fraud patterns, and safety invariants.

---

## 2. Synthetic Dataset Generation & Problem Injection

The generation script `data/generate_data.py` creates a balanced corpus of 200 Amazon India orders across 8 required columns:
`order_id, customer_id, product, order_amount, has_id_proof, refund_requested, previous_refunds, stock_available`.

The dataset explicitly labels every entry with `# SYNTHETIC DEMONSTRATION DATA - FOR MBA ACADEMIC EVALUATION ONLY`.

### Problem Injections Specification:

| Order Range | Injected Condition | Quantitative Trigger | Target Policy Outcome |
|:---:|:---|:---|:---:|
| **ORD 001–020** | **Missing ID Proof + High Value** | `has_id_proof = False`, `order_amount` $\in$ [₹6,000, ₹22,000] | **`BLOCK`** (Rule: ID Proof Missing) |
| **ORD 021–040** | **ID Present + High Value** | `has_id_proof = True`, `order_amount` $\in$ [₹5,200, ₹28,000] | **`ASK CUSTOMER`** (Rule: Amount $>$ ₹5,000) |
| **ORD 041–060** | **Repeat Refund Abuse** | `customer_id = 'CUST_007'`, `previous_refunds` $\ge 4$, `refund_requested = True` | **`BLOCK (FRAUD)`** (Fraud Risk Scoring) |
| **ORD 061–200** | **Baseline & Operational Mix** | Clean orders $\le$ ₹5,000 with ID, standard refunds, stock-out edge cases | **`APPROVE`** / **`ASK CUSTOMER`** |

---

## 3. Human-in-the-Loop Approval Centre (SQLite)

### 3.1 Architectural Hardening: The Safety Protocol
In e-commerce operations, a gatekeeper must never execute monetary disbursements in test or staging environments. The system enforces a hardcoded invariant:
```python
SIMULATION_MODE = True
NEVER_DO_REAL_PAYMENT_OR_REFUND = True
```
Every approval or rejection updates a local SQLite database (`data/gatekeeper_approval.db`). Live bank transfer APIs or payment gateway webhooks are structurally excluded.

### 3.2 Workflow State Transitions
- **`PENDING_REVIEW`:** Automatically assigned to any order resulting in `ASK CUSTOMER`.
- **`APPROVED_BY_ADMIN`:** Set when an authorized reviewer (Aryan Thakur) manually approves an escalated order. Captures reviewer name and ISO timestamp.
- **`REJECTED_BY_ADMIN`:** Set when an escalated order is declined.
- **`RESET`:** Reverts orders back to initial synthetic states for repeated demonstration.

---

## 4. Separation of Concerns: Python Calculates, Gemini Interprets

To eliminate AI hallucination in financial transactions, the architecture enforces strict separation of responsibilities:

```
[ Incoming Request ]
         │
         ▼
┌────────────────────────────────────────────────────────┐
│               PYTHON CALCULATION ENGINE                │
│  - Evaluates Amount vs. ₹5,000 ceiling                 │
│  - Verifies Boolean ID Proof flag                      │
│  - Checks Agent Revocation status                      │
│  - Calculates Previous Refunds count                   │
│  - Resolves Rule Code & Decision (BLOCK / ASK / ALLOW) │
└────────────────────────┬───────────────────────────────┘
                         │ Structured Dict Payload
                         ▼
┌────────────────────────────────────────────────────────┐
│                   GEMINI AI ENGINE                     │
│  - Zero Arithmetic performed                           │
│  - Formulates Natural Language Executive Audit Note    │
│  - Drafts Customer SMS / Push Notification             │
└────────────────────────────────────────────────────────┘
```

---

## 5. Automated Test Suite & Hand-Calculated Scenarios

The test suite in `tests/test_gatekeeper.py` executes against 7 distinct test cases. All tests passed with 100% success rate:

```text
Ran 7 tests in 0.001s
OK
```

### Hand-Calculated Test Cases Matrix:

| Test Identifier | Test Description | Input Parameters | Deterministic Math / Rule | Expected Decision | Actual Decision | Status |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| **Hand Case 1** | **ID Missing** | `amount = 3000`, `has_id = False` | ID proof missing overrides amount $\le 5000$ | **`BLOCK`** | `BLOCK` | **PASS** |
| **Hand Case 2** | **High Value + ID** | `amount = 6500`, `has_id = True` | $6500 > 5000$ ceiling threshold | **`ASK CUSTOMER`** | `ASK CUSTOMER` | **PASS** |
| **Hand Case 3** | **Standard + ID** | `amount = 2000`, `has_id = True` | $2000 \le 5000$ with verified ID | **`ALLOW / APPROVE`** | `ALLOW` | **PASS** |
| **Edge Case 4** | **CUST_007 Fraud** | `CUST_007`, `refunds = 5` | Prior refund count $\ge 3$ triggers fraud | **`BLOCK (FRAUD)`** | `BLOCK` | **PASS** |
| **Edge Case 5** | **Revoked Agent** | `Agent-Suresh` (Revoked) | Agent status = `REVOKED` | **`BLOCK`** | `BLOCK` | **PASS** |
| **Edge Case 6** | **Unknown Agent** | `UntrustedBot_X` | Registry lookup failure | **`BLOCK`** | `BLOCK` | **PASS** |
| **Safety Case 7**| **Safety Invariant** | `NEVER_DO_REAL_PAYMENT` | Verify simulation flag is immutable True | **`TRUE`** | `TRUE` | **PASS** |

---

## 6. User Interface & Experience Enhancements

The updated single-page dashboard at [d:\agent-gatekeeper\index.html](file:///d:/agent-gatekeeper/index.html) features:
1. **Persistent Top Banner:** Prominently communicates synthetic academic status.
2. **Dual-Engine Inspection Panel:** Displays real-time calculations from Python on the left, and Gemini's natural language interpretation on the right.
3. **Approval Centre Tab:** Live table with Approve, Reject, and Reset buttons updating SQLite.
4. **Synthetic Orders Browser:** Interactive table of all 200 synthetic orders with quick filters for injected problem ranges (`ORD 1-20`, `ORD 21-40`, `ORD 41-60`) and 1-click loading into the simulator.
5. **Quick Test Presets:** Dedicated buttons for Hand Cases 1, 2, and 3 for instant examiner demonstration.

---

## 7. Conclusion

The updated **Agent Gatekeeper for Amazon India** satisfies all requirements of the MBA Guide:
- 200 synthetic orders generated in `data/synthetic_amazon_orders.csv` with the exact injected problem distributions.
- Top banner displayed on every view.
- Human-in-the-loop Approval Centre backed by SQLite with complete safety guarantees.
- Deterministic Python calculations separated strictly from Gemini's interpretation.
- Full automated test suite passing all hand-calculated cases.
