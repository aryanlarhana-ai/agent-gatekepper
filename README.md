# Agent Gatekeeper for Amazon India (MBA Edition)

**Student Name:** Aryan Thakur  
**Enrolment Number:** PGD202566017  
**Host Organization:** Amazon India  
**Program:** Post Graduate Diploma (PGD) / MBA  
**Web Application:** Streamlit dashboard at [app.py](app.py)  
**GitHub Repository:** https://github.com/aryanlarhana-ai/agent-gatekepper
**GitHub Pages Demo:** https://aryanlarhana-ai.github.io/agent-gatekepper/

---

## ⚠️ MANDATORY SAFETY & DEMONSTRATION NOTICE
> **SYNTHETIC DEMONSTRATION DATA ONLY**  
> This application is strictly an academic demonstration and policy simulation tool.  
> It contains **ZERO** live payment or refund integrations. All approvals, rejections, and resets update local SQLite records only.

---

## 📌 Executive Summary of New Features Added

1. **Synthetic Data Pipeline (`data/generate_data.py`)**:
   - Generates 200 realistic Amazon orders saved to `data/synthetic_amazon_orders.csv`.
   - Columns: `order_id`, `customer_id`, `product`, `order_amount`, `has_id_proof`, `refund_requested`, `previous_refunds`, `stock_available`.
   - Labeled with `# SYNTHETIC DEMONSTRATION DATA - FOR MBA ACADEMIC EVALUATION ONLY`.
   - **Injected Problem Sets:**
     * **ORD 001–020:** Missing ID proof + high amount ($\rightarrow$ **`BLOCK`**).
     * **ORD 021–040:** Verified ID + order amount $>$ ₹5,000 ($\rightarrow$ **`ASK CUSTOMER`**).
     * **ORD 041–060:** `CUST_007` repeat refund abuse ($\ge 4$ refunds) ($\rightarrow$ **`BLOCK (FRAUD)`**).
     * **ORD 061–200:** Operational baseline mix ($\le$ ₹5,000 with ID proof, low-value refunds, stock edge cases).

2. **Persistent Demonstration Banner**:
   - High-contrast warning banner affixed to the top of every screen:  
     `⚠️ SYNTHETIC DEMONSTRATION DATA — MBA Evaluation System. Real payments or refunds are NEVER executed.`

3. **Human-in-the-Loop Approval Centre (SQLite)**:
   - Dedicated dashboard view managing orders escalated to `ASK CUSTOMER`.
   - **Approve:** Advances pending orders to `APPROVED_BY_ADMIN` with reviewer name and timestamp.
   - **Reject:** Marks transaction as `REJECTED_BY_ADMIN`.
   - **Reset:** Reverts order or entire queue back to baseline state for repeated evaluation.
   - Database schema: `data/gatekeeper_approval.db` (`approval_queue` and `audit_logs`).

4. **Strict Separation of Concerns**:
   - **Python Engine (`engine/gatekeeper_engine.py`):** Calculates 100% of mathematical limits, boolean comparisons, inventory checks, and policy rules.
   - **Gemini AI (`engine/gemini_interpreter.py`):** Operates strictly as a natural language interpreter for compliance summaries and customer notifications. Does zero math.

5. **Automated Test Suite with 3 Hand-Calculated Scenarios (`tests/test_gatekeeper.py`)**:
   - **Case 1:** `has_id_proof = False`, Amount = ₹3,000 $\rightarrow$ **`BLOCK`** *(ID Missing overrides amount)*.
   - **Case 2:** `has_id_proof = True`, Amount = ₹6,500 $\rightarrow$ **`ASK CUSTOMER`** *(Exceeds ₹5,000 ceiling)*.
   - **Case 3:** `has_id_proof = True`, Amount = ₹2,000 $\rightarrow$ **`APPROVE / ALLOW`** *(Within limits with verified ID)*.
   - Plus automated tests for `CUST_007` fraud, Revoked Agent, Unknown Agent, and Safety Invariants.

---

## 🛡️ The 7 Authorized Agents & Policy Rules

### The 7 Agents:
1. `Agent-Kavita` (Order Processing - Active)
2. `Agent-Vikram` (Replenishment Automation - Active)
3. `Agent-Suresh` (Customer Support - **REVOKED** with timestamp)
4. `Agent-Priya` (Refund Processing - Active)
5. `Agent-Aarav` (Returns & Logistics - Active)
6. `Agent-Rahul` (Inquiry & Tracking - Active)
7. `Agent-Ananya` (Dispute Management - Active)

### The 7 Security Rules:
- **Rule 1:** Revoked agent $\rightarrow$ **`BLOCK`**
- **Rule 2:** Unknown agent $\rightarrow$ **`BLOCK`**
- **Rule 3:** ID proof missing $\rightarrow$ **`BLOCK`**
- **Rule 4:** Place order $\le$ ₹5,000 with ID $\rightarrow$ **`ALLOW`**
- **Rule 5:** Place order $>$ ₹5,000 with ID $\rightarrow$ **`ASK CUSTOMER`**
- **Rule 6:** Return or refund requested $\rightarrow$ **`ASK CUSTOMER`**
- **Rule 7:** More than 3 money actions in a day $\rightarrow$ **`ASK CUSTOMER`**
- **Fraud Rule:** `CUST_007` or $\ge 3$ prior refunds $\rightarrow$ **`BLOCK (FRAUD)`**

---

## 🚀 How to Run

### Setup
```powershell
py -m pip install -r requirements.txt
py data/generate_data.py
py -m unittest tests/test_gatekeeper.py -v
py -m streamlit run app.py
```

Open `http://localhost:8501`.

## Publish on GitHub Pages

The GitHub Pages version of the dashboard is live at:

https://aryanlarhana-ai.github.io/agent-gatekepper/

The GitHub Actions workflow deploys `github_pages.html` and the synthetic CSV after every push to `main`. To update the live interface, edit `github_pages.html`; to update the sample dataset, edit the CSV. Commit and push to `main`; the URL stays the same. Check the **Actions** tab for deployment status.

This static dashboard mirrors the Streamlit sections using browser JavaScript. GitHub Pages cannot run `app.py`, Python agents, Gemini API calls, or SQLite. Upload analysis is in-browser and approval state is saved in browser localStorage. The Python Streamlit dashboard and its backend still require a Python-capable host.

Copy `.env.example` to `.env` if Gemini narratives are required. The application runs without a key.

## Architecture

- `agents/`: data-quality, order-risk, revenue, fraud, inventory, finance and executive agents.
- `orchestrator.py`: sequential and parallel agent execution.
- `engine/gatekeeper_engine.py`: deterministic policy calculations.
- `engine/db.py`: SQLite approval and audit records.
- `app.py`: Streamlit dashboard.
- `utils/reports.py`: Excel and PDF reports.
- `data/generate_data.py`: reproducible synthetic 200-order dataset.

## Safety

The app records simulated decisions only. It never moves real money or calls a payment/refund integration.
