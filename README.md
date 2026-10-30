# 📊 Siemens SAT Report Copilot (FastAPI + Gemini AI + Jira/Xray)

An interactive, AI-powered pair-programming and reporting platform designed for **System & Application Test (SAT) Architects** at Siemens eMobility. It generates, updates, and refines executive engineering reports in real time, adhering strictly to the **Official Siemens Corporate Visual Standard**.

---

## ⚡ Quick Start (One-Click)

Simply double-click the portable launcher:
👉 **`Iniciar_Report_Copilot.bat`** (or `Iniciar_Copilot.bat`)

The launcher automatically:
1. Detects Python 3.11+ (or auto-installs it in user mode if missing).
2. Verifies and installs dependencies (`fastapi`, `uvicorn`, `cryptography`, `google-generativeai`).
3. Starts the server and opens the interactive UI in your default browser at **http://127.0.0.1:5050**.

---

## 🌟 Key Capabilities

### 1. Dual-Mode Intelligent Reporting
- **Jira & Xray Live Mode:** Synchronizes test plans (`XPNB-1229`, `XPECD-5356`, `ECD`, etc.), parsing execution suites, pass rates, triage status, and linked defects (`SIF-xxxx`) directly from Atlassian Cloud.
- **Custom / Ad-Hoc Report Mode:** Intelligently adapts to freeform engineering prompts (e.g., field trial results, electric truck interoperability sessions, firmware regressions, commissioning notes) without forcing Jira test plans, while preserving the full official Siemens corporate template.

### 2. Official Siemens SAT Corporate Standard
- **Institutional Branding:** Siemens Petrol (`#009999`), Siemens Ink (`#001b2e`), Dark Blue (`#007993`), and Accent (`#00e5d0`).
- **Visual Structure:** Header with circular geometric arc and metadata cards, metric KPI deck, *Summary Hero Box* with stat pills, engineering tables, quality advisories, and release recommendation sign-offs.
- **100% Technical English:** Automatically translates residual German terms into standard international engineering English.

### 3. Edge-to-Edge Split Workspace
- **Persistent Chat:** Conversational assistance on the left, live HTML report preview on the right.
- **Multi-Image Clipboard Support:** Paste multiple screenshots (`Ctrl+V`) or drag & drop images simultaneously. Gemini Multimodal analyzes oscilloscope traces, UI errors, or terminal logs.
- **Surgical Live Edits:** The AI uses targeted search-and-replace patches (`<HTML_EDIT>`), element toggles (`<HIDE_ELEMENT>`), and CSS injections (`<INJECT_CSS>`) for seamless updates.

### 4. Real-Time Telemetry & Token Transparency
- Top navigation bar displays live status indicators (🟢/🔴) for Jira API, Xray Cloud, and Gemini AI.
- Chat message headers feature a real-time telemetry badge displaying the active Gemini model (e.g., `gemini-3-flash-preview`), response latency (in seconds), and token usage (`in / out`).
- Click the telemetry badge to inspect prompt tokens, candidate tokens, total tokens, and service tier.

---

## 📁 Repository Structure

```
REPORT_MEETING/
├── web/
│   └── index.html               # Modern Edge-to-Edge Split UI & Live Preview
├── server.py                    # FastAPI server & streaming endpoints
├── gemini_copilot.py            # Gemini Copilot engine with multimodal vision & telemetry
├── report_builder.py            # Corporate Siemens SAT HTML template & custom report builder
├── jira_xray_client.py          # Jira REST & Xray GraphQL API integration
├── config_helper.py             # Credential encryption & multi-machine decryption
├── copilot_memory.json          # Persistent architectural memory & learned rules
├── dashboard-config.json        # Jira/Xray credentials & endpoint settings
├── requirements.txt             # Minimal Python dependencies
├── Iniciar_Report_Copilot.bat   # One-click portable launcher
├── ARCHITECTURE.md              # Detailed architecture & technical specification
├── .env.example                 # Environment variable template
└── README.md                    # Project documentation
```

---

## 🛠️ Manual Installation & Development

If you prefer to run the server manually using Python:

```bash
# 1. Clone repository
git clone https://github.com/Canditos/siemens-sat-copilot.git
cd siemens-sat-copilot

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run server
python server.py
```
Open **http://127.0.0.1:5050** in your browser.

---

## 🔒 Security & Privacy

- All credentials stored in `dashboard-config.json` use AES encryption handled by `config_helper.py`.
- The repository `.gitignore` ensures that environment variables, logs, local test files, and binaries are excluded from version control.
- Gemini API interactions only transmit prompt text and explicitly pasted screenshots required for report generation.

---

## 📄 License & Internal Usage

Siemens eMobility — System & Application Test (SAT).  
Internal Engineering & Operational Review Only.
