# PROMPTS & AI INTERACTION LOG (MBA EDITION)

**Project Title:** Agent Gatekeeper for Amazon India (MBA Edition)  
**Student / Developer:** Aryan Thakur  
**Enrolment Number:** PGD202566017  
**Organization / Domain:** Amazon India  
**Date:** November 2026  

---

## 1. Phase 1: Base Gatekeeper System Prompts

*(Archived from initial release)*
- Specification of the 7 initial security rules: Revocation, Unknown Agent, View Order, Low-value limits, High-value ceilings, Reversals, and Velocity limits.
- Implementation of client-side `localStorage` persistence and Amazon India branding.

---

## 2. Phase 2: MBA Guide Upgrade Prompts

### Prompt 2.1: Master MBA Requirements Prompt
```text
Modify this existing Amazon India Agent Gatekeeper project to match my MBA Guide 100%:

Keep same 7 agents and same rules - ID missing = BLOCK, Amount >5000 = ASK CUSTOMER.

Now add:
1. Create data/generate_data.py that creates 200 synthetic Amazon orders in data/synthetic_amazon_orders.csv with columns: order_id, customer_id, product, order_amount, has_id_proof, refund_requested, previous_refunds, stock_available. Label it SYNTHETIC DEMONSTRATION DATA.
Inject these problems: ORD 1-20 = ID missing + high amount = BLOCK, ORD 21-40 = ID present + >5000 = ASK CUSTOMER, ORD 41-60 = CUST_007 repeat refunds = Fraud.
2. Add SYNTHETIC DEMONSTRATION DATA banner on every page.
3. Add Approval Centre - Approve / Reject / Reset saved in SQLite. App must NEVER do real refund/payment.
4. Python does all calculations, Gemini only interprets.
5. Add tests with 3 hand-calculated cases - ID missing = BLOCK, 6500 + ID = ASK, 2000 + ID = APPROVE.

First give me plan only, no code yet. Wait for my approval.
```

### Prompt 2.2: Approval and Build Order Instruction
```text
APPROVED. Start coding now. Build in this order: 1. data/generate_data.py, 2. engine, 3. UI + Approval Centre, 4. tests. Go.
```

---

## 3. Engineering Decisions & Code Architecture

### 1. Data Pipeline (`data/generate_data.py`)
- Generated exactly 200 synthetic orders in `data/synthetic_amazon_orders.csv`.
- Injected specific distributions:
  * ORD 1–20: `has_id_proof = False`, `order_amount > 5000` $\rightarrow$ `BLOCK`.
  * ORD 21–40: `has_id_proof = True`, `order_amount > 5000` $\rightarrow$ `ASK CUSTOMER`.
  * ORD 41–60: `customer_id = 'CUST_007'`, `previous_refunds >= 4`, `refund_requested = True` $\rightarrow$ `BLOCK (FRAUD)`.
  * ORD 61–200: Baseline clean distribution ($\le 5000$ with ID, low-value refunds, stock edge cases).
- Prepended CSV with `# SYNTHETIC DEMONSTRATION DATA - FOR MBA ACADEMIC EVALUATION ONLY`.

### 2. Separation of Concerns Architecture
- **`engine/gatekeeper_engine.py`:** Pure Python deterministic evaluation. Computes all boolean identity verification, amount comparisons, stock checks, and fraud scoring.
- **`engine/gemini_interpreter.py`:** Interprets Python's calculated output into natural language audit notes and customer SMS drafts. Zero arithmetic or policy decisions performed by the AI.

### 3. Approval Centre & Hard Safety Invariant
- **`engine/db.py`:** SQLite database storing `approval_queue` and `audit_logs`.
- Hardcoded safety check:
  ```python
  SIMULATION_MODE = True
  NEVER_DO_REAL_PAYMENT_OR_REFUND = True
  ```
  Approve / Reject / Reset workflows mutate SQLite rows only and never call external payment endpoints.

### 4. Test Suite Execution (`tests/test_gatekeeper.py`)
Tested against 7 unit tests:
1. `test_hand_case_1_id_missing_blocks` $\rightarrow$ **PASS** (`BLOCK`)
2. `test_hand_case_2_amount_6500_with_id_asks_customer` $\rightarrow$ **PASS** (`ASK CUSTOMER`)
3. `test_hand_case_3_amount_2000_with_id_approves` $\rightarrow$ **PASS** (`ALLOW`)
4. `test_fraud_cust_007` $\rightarrow$ **PASS** (`BLOCK (FRAUD)`)
5. `test_revoked_agent` $\rightarrow$ **PASS** (`BLOCK`)
6. `test_unknown_agent` $\rightarrow$ **PASS** (`BLOCK`)
7. `test_safety_protocol` $\rightarrow$ **PASS** (`NEVER_DO_REAL_PAYMENT == True`)
