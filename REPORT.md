# PROJECT REPORT: AGENT GATEKEEPER FOR AMAZON INDIA

**Course / Academic Program:** Post Graduate Diploma (PGD)  
**Student Name:** Aryan Thakur  
**Enrolment Number:** PGD202566017  
**Host Organization / Domain:** Amazon India (`Amazon.in`)  
**Submission Date:** November 2026  
**Application Repository:** `d:\agent-gatekeeper\index.html`  

---

## 1. Executive Summary

As autonomous Artificial Intelligence (AI) agents increasingly represent customers and automate customer service tasks—such as viewing order histories, placing replenishment orders, handling product returns, and initiating refunds—e-commerce platforms face severe security, financial, and governance challenges. Without strict perimeter controls, rogue, compromised, or uncalibrated agents can trigger unauthorized transactions, drain account balances, or execute high-velocity fraudulent operations.

**Agent Gatekeeper for Amazon India** is an enterprise-grade, single-page policy gateway designed and implemented by **Aryan Thakur (PGD202566017)** for **Amazon India**. The system enforces deterministic authorization boundaries on autonomous agent actions using a 7-rule security policy engine. The application provides agent registry and timestamped revocation, request evaluation simulation, live decision outcomes (`ALLOW`, `ASK CUSTOMER`, `BLOCK`), and a persistent, searchable audit log stored securely in browser `localStorage`.

---

## 2. Problem Statement & Industrial Motivation

### 2.1 The Agentic E-Commerce Paradigm
Autonomous software agents operate with delegated customer authority. In an e-commerce ecosystem like Amazon India, an agent might:
1. Re-order household supplies when pantry sensors detect low stock.
2. Inquire about shipment tracking and view past purchase histories.
3. Initiate return requests for defective items and request refunds to original payment methods.

### 2.2 Security & Financial Vulnerabilities
Granting unbounded autonomy introduces critical attack vectors:
- **Revoked / Deprecated Agents:** An agent whose API keys were compromised or permissions rescinded might continue executing requests if revocation is not strictly checked at the gateway.
- **Shadow / Unknown Agents:** Unregistered third-party bots attempting actions on behalf of customers without authenticated trust.
- **Runaway Financial Drain:** An agent making large purchases or rapid micro-transactions that exceed intended customer budgets.
- **Unauthorized Financial Reversals:** Fraudulent returns or refunds processed without human oversight.

### 2.3 Regulatory Alignment in India
The Reserve Bank of India (RBI) mandates Two-Factor Authentication (2FA / OTP) and explicit consent mechanisms for electronic transactions and e-mandates exceeding specific financial thresholds. Agent Gatekeeper mirrors these regulatory principles by classifying decisions into three deterministic states:
- **ALLOW:** Safe, pre-authorized autonomous execution.
- **ASK CUSTOMER:** Step-up authentication required; customer confirmation or OTP mandatory before execution.
- **BLOCK:** Unconditional perimeter rejection due to security non-compliance.

---

## 3. System Architecture & Tech Stack

```
+---------------------------------------------------------------------------------+
|                         AGENT GATEKEEPER UI (Amazon.in)                         |
|  [Header: Aryan Thakur | PGD202566017]   [Telemetry Metrics Bar: ALLOW/ASK/BLOCK]|
+---------------------------------------+-----------------------------------------+
|        AGENT MANAGEMENT MODULE        |        REQUEST SIMULATION MODULE        |
|  - Register New Agent Form            |  - Customer Name & Action Dropdown      |
|  - Agent Status Table (Active/Revoked)|  - Agent Selector / Custom Unknown Agent|
|  - Revoke Button (Timestamp Saved)    |  - Dynamic Amount Field (INR ₹)         |
+---------------------------------------+-----------------------------------------+
                                    |
                                    v
                    +-------------------------------+
                    |    7-RULE POLICY ENGINE       |
                    |  (Deterministic Decision Tree)|
                    +---------------+---------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
| LIVE DECISION BANNER  |                       | AUDIT LOG ENGINE      |
| - ALLOW (Green)       |                       | - LocalStorage Store  |
| - ASK CUSTOMER (Amber)|                       | - Search & Filtering  |
| - BLOCK (Red)         |                       | - CSV Export Facility |
+-----------------------+                       +-----------------------+
```

### 3.1 Technology Selection
- **Frontend Core:** Pure HTML5, Modern CSS3 (Amazon India Design System), and Vanilla JavaScript (ES6+).
- **Zero Runtime Dependencies:** Requires no Node.js, npm packages, or external frameworks. Operates directly in any modern browser (`file:///` protocol supported).
- **Client-Side Persistence:** `localStorage` is used for high-performance, persistent state management across page reloads.

### 3.2 Visual Design System
The interface follows the official **Amazon India** design language:
- **Header:** Amazon Dark Slate (`#131921`) and Amazon Navy (`#232F3E`).
- **Brand Accents:** Amazon Smile Orange (`#FF9900`), Action Orange (`#E47911`), and Primary Button Yellow (`#FFD814`).
- **Decision Signaling:**
  - `ALLOW`: Amazon Success Green (`#067D62` / `#E7F4EE`)
  - `ASK CUSTOMER`: Amazon Warning Amber (`#C45500` / `#FFF4EB`)
  - `BLOCK`: Amazon Alert Crimson (`#BA0933` / `#FDF0F0`)

---

## 4. Policy Engine Specification (The 7 Rules)

The policy engine evaluates every incoming transaction through an ordered, deterministic hierarchy.

### 4.1 Formal Rule Definitions

| Rule ID | Rule Statement | Decision | Policy Justification |
|:---|:---|:---:|:---|
| **Rule 1** | **Revoked agent = BLOCK** | `BLOCK` | Identity revocation immediately invalidates all capabilities. The exact date-time of revocation is retrieved and rendered. |
| **Rule 2** | **Unknown agent = BLOCK** | `BLOCK` | Zero-Trust perimeter enforcement. Any agent ID not recognized in the authorized registry is halted. |
| **Rule 3** | **`view order` = ALLOW** | `ALLOW` | Non-financial read inquiry. Low risk; verified active agents can query order status without friction. |
| **Rule 4** | **`place order` $\le$ Rs 5000 = ALLOW** | `ALLOW` | Micro / standard replenishments within the automated spending limit of ₹5,000. |
| **Rule 5** | **`place order` $>$ Rs 5000 = ASK CUSTOMER** | `ASK CUSTOMER` | High-value order ceiling. Requires explicit customer authorization / OTP confirmation. |
| **Rule 6** | **`return` or `refund` = ASK CUSTOMER** | `ASK CUSTOMER` | Financial reversal safeguards. Reversals carry dispute and inventory risks, requiring customer approval. |
| **Rule 7** | **$>$ 3 money actions in a day = ASK CUSTOMER** | `ASK CUSTOMER` | Fraud velocity protection. If an agent executes a 4th or subsequent money action (`place order`, `return`, `refund`) on the same calendar day, customer step-up confirmation is enforced regardless of amount. |

### 4.2 Decision Pipeline Hierarchy
The rules are evaluated in the following priority:

1. **Check Agent Validity:**
   - Is agent marked as `REVOKED` in registry? $\rightarrow$ **Rule 1: BLOCK**
   - Is agent missing from registry? $\rightarrow$ **Rule 2: BLOCK**
2. **Check Inquiry Action:**
   - Is action `view order`? $\rightarrow$ **Rule 3: ALLOW**
3. **Financial Action Processing (`place order`, `return`, `refund`):**
   - Count agent's prior money actions recorded on today's calendar date:
     - If count $\ge 3$ $\rightarrow$ **Rule 7: ASK CUSTOMER** *(Velocity Limit Exceeded)*
     - If count $< 3$:
       - If action is `place order` and amount $\le 5000$ $\rightarrow$ **Rule 4: ALLOW**
       - If action is `place order` and amount $> 5000$ $\rightarrow$ **Rule 5: ASK CUSTOMER**
       - If action is `return` or `refund` $\rightarrow$ **Rule 6: ASK CUSTOMER**

---

## 5. Functional Modules Walkthrough

### 5.1 Student Identification Banner
Prominently anchored at the top-right of the Amazon India header:
- **Developer:** Aryan Thakur
- **Enrolment:** PGD202566017
- **Admin Status Badge:** Displayed with Amazon Orange accent.

### 5.2 Agent Registration & Revocation
- **Registration Form:** Input field accepting agent names/IDs (e.g., `Agent-Kavita`, `Bot-Priya`). Prevents duplicate registrations and sets `registeredAt` timestamp with status `ACTIVE`.
- **Authorized & Revoked Agents Table:** Displays Agent Name, Status Badge, Registration Timestamp, Revocation Timestamp, and Action Button.
- **Revocation Action:** Clicking the "Revoke Agent" button updates the status to `REVOKED`, captures `new Date().toISOString()`, and saves it to `localStorage`.

### 5.3 Request Simulator
- **Customer Name:** Standard text input.
- **Agent Selector:** Integrated `<select>` dropdown of known active/revoked agents, accompanied by a "Type Unknown Agent" checkbox toggle allowing custom inputs (e.g. `RogueBot_99`) to evaluate Rule 2.
- **Action Type Dropdown:** Contains `view order`, `place order`, `return`, `refund`.
- **Amount Field:** Formatted in INR (`₹`). Automatically disables with explanatory text when `view order` is selected.

### 5.4 Live Decision Display Banner
- Dynamically rendered container displaying the uppercase decision (`ALLOW`, `ASK CUSTOMER`, `BLOCK`).
- Displays the matching Rule Number (e.g., `Rule 4: place order Rs 5000 or less = ALLOW`).
- Provides a detailed contextual explanation including customer name, agent name, action, and transaction value.

### 5.5 Audit Log Table & State Persistence
- **Storage Keys:**
  - `amazon_gatekeeper_agents_v2`
  - `amazon_gatekeeper_audit_log_v2`
- **Audit Columns:** Date & Time, Customer Name, Agent Name, Action, Amount, Decision Badge, Rule Triggered, and Context Explanation.
- **Interactivity:**
  - Filter dropdown by Decision (`ALL`, `ALLOW`, `ASK CUSTOMER`, `BLOCK`).
  - Search box filtering across all text fields.
  - **Export CSV** generating a downloadable RFC-4180 compliant CSV file.
  - **Clear Audit Log** with confirmation protection.

---

## 6. Verification & Test Matrix

The system was verified against all 7 security rules, persistence requirements, and edge cases.

| Test Case | Scenario / Rule Tested | Input Data (Agent, Action, Amount) | Expected Decision | Actual Decision | Rule Applied | Status |
|:---:|:---|:---|:---:|:---:|:---:|:---:|
| **TC-01** | **Rule 1:** Revoked Agent | `Agent-Suresh` (Revoked), `place order`, ₹2,500 | `BLOCK` | `BLOCK` | Rule 1 | **PASS** |
| **TC-02** | **Rule 2:** Unknown Agent | `UntrustedBot_77` (Unregistered), `place order`, ₹1,500 | `BLOCK` | `BLOCK` | Rule 2 | **PASS** |
| **TC-03** | **Rule 3:** View Order Inquiry | `Agent-Kavita` (Active), `view order`, ₹0 | `ALLOW` | `ALLOW` | Rule 3 | **PASS** |
| **TC-04** | **Rule 4:** Place Order $\le$ ₹5,000 | `Agent-Vikram` (Active), `place order`, ₹3,499 | `ALLOW` | `ALLOW` | Rule 4 | **PASS** |
| **TC-05** | **Rule 5:** Place Order $>$ ₹5,000 | `Agent-Vikram` (Active), `place order`, ₹18,999 | `ASK CUSTOMER` | `ASK CUSTOMER` | Rule 5 | **PASS** |
| **TC-06** | **Rule 6:** Return Action | `Agent-Kavita` (Active), `return`, ₹2,100 | `ASK CUSTOMER` | `ASK CUSTOMER` | Rule 6 | **PASS** |
| **TC-07** | **Rule 6:** Refund Action | `Agent-Kavita` (Active), `refund`, ₹1,500 | `ASK CUSTOMER` | `ASK CUSTOMER` | Rule 6 | **PASS** |
| **TC-08** | **Rule 7:** $> 3$ Money Actions/Day | `Agent-VelocityTester`, 4th money action of ₹1,200 | `ASK CUSTOMER` | `ASK CUSTOMER` | Rule 7 | **PASS** |
| **TC-09** | **Persistence Verification** | Full browser reload / refresh | Logs retained in localStorage | Logs intact | All | **PASS** |
| **TC-10** | **Revocation Timestamp** | Click "Revoke" on active agent | Exact date & time recorded | Timestamp displayed | Rule 1 data | **PASS** |

---

## 7. Security, Governance & Compliance Analysis

### 7.1 Principle of Least Privilege & Zero Trust
The gatekeeper enforces Zero-Trust by default: an agent has no implicit trust. Every request is independently evaluated against identity validity, action classification, amount thresholds, and temporal frequency limits.

### 7.2 Non-Repudiation & Auditability
Every decision made by the gatekeeper is stamped with an ISO timestamp, logged with full input context, and stored immutably in client-side storage. The CSV export facility enables compliance officers to audit agent activity for forensic review.

### 7.3 Protection Against Compromised Agents
If an agent's credentials are breached or misconfigured:
- Immediate revocation shuts down all access across all accounts within milliseconds (Rule 1).
- Even while active, runaway micro-transactions are halted by Rule 7 after the 3rd daily financial action.

---

## 8. Conclusion & Future Roadmap

**Agent Gatekeeper for Amazon India** successfully demonstrates how automated governance can enforce strict safety boundaries around autonomous AI agents without sacrificing operational velocity. Developed by **Aryan Thakur (PGD202566017)**, the application satisfies all operational, functional, aesthetic, and architectural requirements.

### Future Enhancements
1. **Cryptographic Agent Attestation:** Integration of Mutual TLS (mTLS) or Signed JSON Web Tokens (JWT) for hardware-bound agent authentication.
2. **Push Notifications:** Direct integration with the Amazon Shopping mobile app to deliver real-time push alerts with biometric authorization when `ASK CUSTOMER` is triggered.
3. **Dynamic ML Risk Scoring:** Enhancing static threshold rules with behavioral machine learning models that score anomaly probabilities based on customer purchasing history.
