# Agent Gatekeeper for Amazon India

**Developed by:** Aryan Thakur  
**Enrolment No:** PGD202566017  
**Platform:** Single Page Web Application (Amazon India Design System)  
**File Location:** `d:\agent-gatekeeper\index.html`

---

## 📌 Project Overview
**Agent Gatekeeper for Amazon India** is an intelligent security and policy gateway that validates, governs, and audits autonomous agent actions performed on customer accounts in the Amazon India ecosystem.

All data (Registered Agents, Revocation Timestamps, and Audit Logs) is persistently stored in `localStorage` so that nothing disappears upon browser refresh or tab closing.

---

## 🛡️ Policy Engine Rules (The 7 Rules)

| Rule # | Condition / Trigger | Decision | Behavior & Security Context |
|---|---|---|---|
| **Rule 1** | Revoked agent | `BLOCK` | Any agent marked as revoked is strictly forbidden from executing any operations. Revocation timestamp is recorded and presented. |
| **Rule 2** | Unknown agent | `BLOCK` | Unregistered / untrusted agents are blocked at the perimeter before accessing customer data. |
| **Rule 3** | `view order` | `ALLOW` | Read-only inquiry action. Permitted for all authorized, active agents without financial risk. |
| **Rule 4** | `place order` &le; &#8377;5,000 | `ALLOW` | Low-value automated checkout within acceptable risk limits for verified agents. |
| **Rule 5** | `place order` &gt; &#8377;5,000 | `ASK CUSTOMER` | High-value order exceeding automated threshold. Requires explicit OTP / customer verification. |
| **Rule 6** | `return` or `refund` | `ASK CUSTOMER` | Financial reversal actions. Escalated for customer consent and verification. |
| **Rule 7** | &gt; 3 money actions in a day | `ASK CUSTOMER` | Fraud velocity safeguard. When an agent attempts a 4th or subsequent money action (`place order`, `return`, `refund`) within the same day, customer authorization is required regardless of order amount. |

---

## ✨ Features & Architecture

1. **Header & Identification**:
   - Amazon India branding with dark navy navbar (`#131921`), amber accents, and clean layout.
   - Developer Name: **Aryan Thakur**
   - Enrolment Number: **PGD202566017**
   - Real-time metric pills for Active/Revoked agents and ALLOW / ASK CUSTOMER / BLOCK counts.

2. **Agent Management**:
   - **Register Agent Form**: Authorize new agents by name or ID.
   - **Authorized & Revoked Agents List**: Interactive table displaying Agent Name, Status badge (`Active` / `Revoked`), Registration Date-Time, and exact Revocation Date-Time.
   - **Revoke Agent Button**: Instantly updates status to `REVOKED` and stamps the current Date and Time into `localStorage`.
   - Option to reactivate if needed.

3. **Request Simulation & Evaluation**:
   - Customer Name input.
   - Agent Name selector (dropdown of known active/revoked agents OR toggle to test unknown/unregistered agents).
   - Action dropdown: `view order`, `place order`, `return`, `refund`.
   - Dynamic Amount field (disabled for `view order`, active with INR &#8377; currency formatting for financial actions).
   - "Evaluate & Authorize Request" button.
   - **One-Click Quick Test Scenarios**: Instant 1-click test buttons for **Rule 1** through **Rule 7** to simplify evaluation.

4. **Live Gatekeeper Decision Display**:
   - Prominent status banner with high-contrast color coding:
     - `ALLOW` (Amazon Forest Green `#067D62`)
     - `ASK CUSTOMER` (Amazon Warm Amber `#C45500`)
     - `BLOCK` (Amazon Crimson Red `#BA0933`)
   - Specific rule number and rule title displayed.
   - Contextual explanation citing the specific customer, agent, amount, and policy justification.

5. **Audit Log Table**:
   - Table columns: Date-Time, Customer Name, Agent Name, Action, Amount, Decision, Rule Triggered, and Context/Reason.
   - Decision filters: All / ALLOW / ASK CUSTOMER / BLOCK.
   - Real-time search across customer, agent, and rule.
   - **Export CSV** button to download audit logs.
   - **Clear Audit Log** button with confirmation.
   - **LocalStorage Persistence**: Auto-saves on every registration, revocation, and evaluation.

---

## 🚀 How to Open and Run
1. Open Windows File Explorer and navigate to `D:\agent-gatekeeper\`.
2. Double-click [index.html](file:///d:/agent-gatekeeper/index.html) to open in Microsoft Edge, Google Chrome, or any web browser.
3. Everything is client-side and requires no web server, Node.js, or external installation.
