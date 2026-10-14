# Kiana Green Solar ERP - Pending Features & Gap Analysis

As per the **Master PRD (PDF)**, here is the line-by-line status of the 25 Enhanced Features. This will act as our master checklist to complete the ERP.

| # | Feature Name from PDF | Current Status in Code | What needs to be done next? |
|---|-----------------------|------------------------|-----------------------------|
| 01 | **Management Dashboard / Command Center** | 🟡 Partially Done | We have basic dashboards, but need KPI targets, pipeline, profitability & alerts specific to Owner/Director. |
| 02 | **Employee-ID Based Access Control** | 🟢 Done | Employee IDs and roles (Director, Manager, etc.) are implemented in `users/models.py`. |
| 03 | **Exception-Based Access** | 🔴 Pending | We added the 'custom' role, but need logic to grant temporary access with an *Expiry Date* to specific modules. |
| 04 | **AI Agent / English Prompt Assistant** | 🟢 Done | Integrated using LangGraph & Groq with live database reading and permission awareness. |
| 05 | **Complete Solar Project Workflow** | 🟡 Partially Done | Basic flow exists, but we need to strictly connect AMC/O&M at the very end of the pipeline. |
| 06 | **Costing & Margin Calculator** | 🔴 Pending | Need a dedicated calculator module for Panel, Inverter, BOS, Labour, GST & Gross Margin. |
| 07 | **Approval Engine** | 🔴 Pending | Need multi-level approval limits for discounts, purchase, payments & stock adjustments. |
| 08 | **Audit Trail** | 🟡 Partially Done | `django-simple-history` is installed, but needs to log Employee ID, date/time, and IP/device for *deleted* records too. |
| 09 | **SOP / Stage-Gate Engine** | 🔴 Pending | **Critical:** Currently statuses can be changed casually. We need strict validation (e.g. required documents before jumping from Survey to Design). |
| 10 | **Document Management (Extended)** | 🔴 Pending | Need version history and specific categories (KYC, electricity bills, DISCOM docs) in `documents` app. |
| 11 | **Survey & Technical Design** | 🔴 Pending | Add GPS location, roof dimensions, shadow, sanctioned load, panel count & inverter sizing to Survey models. |
| 12 | **BOM & Kit Configuration** | 🔴 Pending | Standard 1/2/3/5/10 kW kits and BOM versioning. Automatic material reservation is missing. |
| 13 | **Procurement Intelligence** | 🔴 Pending | RFQ → Vendor Quotation → Comparison → Approval → PO → GRN workflow is missing. |
| 14 | **Project Profitability** | 🔴 Pending | Estimated vs Actual cost comparison (Margin by project/salesperson). |
| 15 | **Payment Milestone Tracker** | 🔴 Pending | Ageing reports for outstanding payments and automatic reminders. |
| 16 | **Customer 360°** | 🟡 Partially Done | We have detail views, but need a *single* unified screen showing WhatsApp, payments, AMC history all together. |
| 17 | **Employee Performance / KPI** | 🔴 Pending | Targets vs achievement, TAT, and installation performance for HR. |
| 18 | **Escalation Matrix & SLA / TAT** | 🔴 Pending | Automatic L1 → L2 → L3 escalations if a lead or task crosses its deadline. |
| 19 | **Notification Center** | 🟡 Partially Done | In-app is present. WhatsApp / SMS templates & scheduled auto-reports are pending. |
| 20 | **Universal Search** | 🔴 Pending | One global search bar in the top navbar across customers, Project ID, invoices, vendors. |
| 21 | **Activity Timeline** | 🔴 Pending | A chronological timeline feed (Facebook-style) for every lead/project showing events & approvals. |
| 22 | **Data Import / Export & API Layer** | 🟢 Done | Bulk Excel/CSV endpoints and REST APIs for external integration are built. |
| 23 | **Mobile Field App (Backend)** | 🟡 Partially Done | APIs are ready, but we need *Customer OTP / Signature* logic for site completion. |
| 24 | **Warranty & Serial Tracking** | 🔴 Pending | Panel & Inverter serial numbers mapped to customers for warranty replacement history. |
| 25 | **Backup & Recovery** | 🔴 Pending | Scheduled automated backups stored on the server with a retention policy. |

### Structural Changes Required:
* **The Permanent Project ID (e.g., KG-UP-2026-00125):** We need to ensure that this ID is generated at the **Lead** stage itself and attaches to *every* module (Documents, Payments, Installation, Warranty) without fail.
