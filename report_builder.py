import json
import re
from datetime import datetime

GERMAN_TO_ENGLISH = {
    "Fehler": "Defect",
    "Nicht bestanden": "FAILED",
    "Nicht Bestanden": "FAILED",
    "Fehlgeschlagen": "FAILED",
    "Bestanden": "PASSED",
    "Erfolgreich": "PASSED",
    "Abgebrochen": "ABORTED",
    "Durchgeführt": "EXECUTED",
    "Durchgefuehrt": "EXECUTED",
    "In Bearbeitung": "IN PROGRESS",
    "In Arbeit": "IN PROGRESS",
    "Offen": "OPEN",
    "Geschlossen": "CLOSED",
    "Fertig": "DONE",
    "Erledigt": "DONE",
    "Funnel": "ANALYSIS / TRIAGE",
    "Blockiert": "BLOCKED",
    "Keine": "None",
    "Kein": "None",
    "Beschreibung": "Description",
    "Zusammenfassung": "Summary",
    "Priorität": "Priority",
    "Prioritaet": "Priority",
    "Hoch": "High",
    "Kritisch": "Critical",
    "Mittel": "Medium",
    "Niedrig": "Low",
    "Unbekannt": "Unknown",
    "Nicht zugewiesen": "Unassigned"
}

def clean_german_text(text):
    if not text or not isinstance(text, str):
        return text
    res = text
    for de, en in GERMAN_TO_ENGLISH.items():
        res = re.sub(r'\b' + re.escape(de) + r'\b', en, res, flags=re.IGNORECASE)
    return res

SIEMENS_CORPORATE_CSS = """
:root {
  --siemens-petrol: #009999;
  --siemens-ink: #001b2e;
  --siemens-blue: #007993;
  --siemens-accent: #00e5d0;
  --mist: #f3f7f8;
  --line: #d7e2e5;
  --muted: #52636d;
  --pass: #107c41;
  --fail: #b42318;
  --warn: #c97a00;
  --info: #026aa7;
  --na: #667085;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #e9f0f2;
  color: var(--siemens-ink);
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 14px;
  line-height: 1.45;
}
.card {
  max-width: 1240px;
  min-height: 100vh;
  margin: 0 auto;
  background: #fff;
  box-shadow: 0 0 32px rgba(0, 27, 46, .12);
}
.header {
  position: relative;
  overflow: hidden;
  min-height: 220px;
  padding: 32px 48px;
  color: #fff;
  background: var(--siemens-ink);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.header::after {
  content: "";
  position: absolute;
  right: -70px;
  bottom: -145px;
  width: 540px;
  height: 350px;
  border: 48px solid var(--siemens-petrol);
  border-radius: 50%;
  opacity: .95;
  pointer-events: none;
}
.brand, .header-copy, .meta {
  position: relative;
  z-index: 1;
}
.brand {
  font-family: Arial, sans-serif;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -2px;
  line-height: 1;
  color: var(--siemens-petrol);
}
.header-copy {
  align-self: flex-end;
  margin-top: 50px;
}
.eyebrow {
  margin-bottom: 8px;
  color: #8ce0dc;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.6px;
  text-transform: uppercase;
}
.header h1 {
  max-width: 780px;
  margin: 0;
  font-size: clamp(26px, 3.8vw, 38px);
  font-weight: 300;
  letter-spacing: -.8px;
  line-height: 1.1;
}
.header h1 strong { font-weight: 700; }
.subtitle {
  margin: 12px 0 0;
  color: #c7dde2;
  font-size: 14.5px;
  max-width: 740px;
}
.meta {
  min-width: 220px;
  margin-left: 28px;
  padding: 14px 0 14px 18px;
  border-left: 2px solid var(--siemens-petrol);
  font-size: 12px;
  line-height: 1.7;
}
.meta span {
  display: block;
  color: #9fb7c0;
  text-transform: uppercase;
  letter-spacing: .7px;
  font-size: 10px;
  margin-top: 6px;
}
.meta span:first-child { margin-top: 0; }
.meta strong { color: #fff; font-size: 13.5px; font-weight: 600; }

.content {
  padding: 36px 48px 54px;
  overflow-x: hidden;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 34px;
}
@media (max-width: 900px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 560px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
.kpi-card {
  padding: 18px 22px;
  background: var(--mist);
  border: 1px solid var(--line);
  border-radius: 2px;
}
.kpi-title {
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--muted);
  letter-spacing: .6px;
  margin-bottom: 4px;
}
.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--siemens-ink);
  line-height: 1.15;
  margin: 4px 0;
}
.kpi-sub {
  font-size: 12px;
  color: var(--muted);
}

.summary-box {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 24px;
  align-items: center;
  margin-bottom: 34px;
  padding: 22px 26px;
  border: 1px solid var(--line);
  border-left: 6px solid var(--pass);
  background: var(--mist);
  border-radius: 2px;
}
.summary-state {
  display: inline-block;
  padding: 8px 16px;
  background: #dff3e7;
  color: var(--pass);
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  border-radius: 4px;
  border: 1px solid rgba(16, 124, 65, 0.25);
}
.summary-box h3 {
  margin: 2px 0 4px;
  font-size: 21px;
  font-weight: 600;
  letter-spacing: -.25px;
}
.summary-box p {
  margin: 0;
  color: var(--muted);
  font-size: 13.5px;
}
.summary-stats {
  display: flex;
  gap: 10px;
  align-items: center;
  border-left: 1px solid var(--line);
  padding-left: 20px;
  flex-wrap: wrap;
}
.stat-pill {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 4px;
  min-width: 68px;
  text-align: center;
}
.stat-pill .num { font-size: 18px; font-weight: 700; color: var(--siemens-ink); line-height: 1.1; }
.stat-pill .lbl { font-size: 9.5px; text-transform: uppercase; color: var(--muted); letter-spacing: .5px; margin-top: 3px; white-space: nowrap; }
.stat-pill--pass { background: #f2f9f5; border-color: rgba(16, 124, 65, 0.25); }
.stat-pill--pass .num { color: var(--pass); }
.stat-pill--fail { background: #fdf3f2; border-color: rgba(180, 35, 24, 0.25); }
.stat-pill--fail .num { color: var(--fail); }
.stat-pill--skip { background: #f8f9fa; border-color: rgba(102, 112, 133, 0.25); }
.stat-pill--skip .num { color: var(--na); }

.section-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 36px 0 14px;
  color: var(--siemens-ink);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -.3px;
}
.section-title::before {
  content: "";
  width: 20px;
  height: 4px;
  background: var(--siemens-petrol);
}
.section-desc {
  margin: -6px 0 16px;
  color: var(--muted);
  font-size: 13px;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--line);
  margin-bottom: 24px;
  border-radius: 2px;
}
table {
  width: 100%;
  min-width: 820px;
  border-collapse: collapse;
  table-layout: fixed;
}
th {
  padding: 12px 14px;
  background: var(--siemens-ink);
  border-right: 1px solid #244051;
  color: #fff;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: .75px;
  text-align: left;
  text-transform: uppercase;
}
th:last-child { border-right: 0; }
td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
  color: #263b47;
  font-size: 13px;
  vertical-align: middle;
  overflow-wrap: anywhere;
  word-break: break-word;
}
tbody tr:nth-child(even) { background: #f9fbfc; }
tbody tr:hover { background: #eef7f7; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr.total-row {
  background: #f1f5f8;
  font-weight: 700;
  border-top: 2px solid var(--siemens-ink);
}
tbody tr.total-row td {
  color: var(--siemens-ink);
}
td strong { color: var(--siemens-ink); font-weight: 650; }

.result {
  display: inline-block;
  min-width: 80px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 800;
  letter-spacing: .6px;
  text-align: center;
  text-transform: uppercase;
}
.result--pass { background: #dff3e7; color: var(--pass); }
.result--fail { background: #fde8e6; color: var(--fail); }
.result--warn { background: #fef3cd; color: var(--warn); }
.result--block { background: #fbeae5; color: #b42318; border: 1px dashed #b42318; }
.result--na { background: #eaecf0; color: var(--na); }
.result--info { background: #e0f2fe; color: var(--info); }

.jira-link {
  color: var(--siemens-blue);
  font-weight: 600;
  text-decoration: none;
}
.jira-link:hover {
  text-decoration: underline;
  color: var(--siemens-petrol);
}

.callout {
  margin: 20px 0;
  padding: 16px 20px;
  background: #f0fdf4;
  border-left: 5px solid var(--siemens-petrol);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.custom-card {
  margin-bottom: 24px;
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-left: 5px solid var(--siemens-petrol);
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0,27,46,0.04);
}

.video-feature-card {
  background: linear-gradient(135deg, #001b2e 0%, #00364d 100%);
  border-radius: 4px;
  padding: 26px 30px;
  color: #fff;
  margin-bottom: 30px;
  box-shadow: 0 4px 16px rgba(0, 27, 46, 0.15);
}
.video-layout {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 26px;
  align-items: center;
}
@media (max-width: 900px) {
  .video-layout { grid-template-columns: 1fr; }
}
.video-player-box {
  background: #000;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
}
.video-player-box video {
  width: 100%;
  max-height: 320px;
  object-fit: contain;
}
.btn-load-video {
  background: var(--siemens-petrol);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  margin-top: 10px;
}
.btn-load-video:hover {
  background: #00b3b3;
}

.footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 48px;
  background: var(--siemens-ink);
  color: #b6cbd3;
  font-size: 11px;
  letter-spacing: .3px;
}
.footer strong { color: #fff; font-weight: 600; }

@media print {
  body { background: #fff; }
  .card { max-width: none; box-shadow: none; }
  .filter-bar { display: none !important; }
}
"""

def render_custom_report(custom_data, state=None):
    """
    Renders an official Siemens SAT corporate report dynamically adapted to any content.
    Allows the Copilot to generate field test reports, architecture reviews, handoffs,
    benchmarks, or any freeform engineering prompt using the official Siemens visual standard.
    """
    state = state or {}
    custom_data = custom_data or {}

    title = clean_german_text(custom_data.get("title") or state.get("report_title") or "Siemens Engineering Report")
    subtitle = clean_german_text(custom_data.get("subtitle") or state.get("report_subtitle") or "Technical assessment, verification and operational findings overview")
    eyebrow = clean_german_text(custom_data.get("eyebrow") or state.get("report_eyebrow") or "System & Application Test (SAT) · Engineering Assessment")
    product = clean_german_text(custom_data.get("product") or custom_data.get("product_name") or state.get("product_name") or "Siemens eMobility")
    version = clean_german_text(custom_data.get("version") or custom_data.get("target_version") or state.get("target_fw_str") or "v1.0")
    ref_code = clean_german_text(custom_data.get("reference_code") or custom_data.get("plan_key") or state.get("plan_key") or "SAT-RPT-CUSTOM")
    status_str = clean_german_text(custom_data.get("status") or "Verified & Documented")

    # KPIs Grid
    kpis = custom_data.get("kpis") or []
    kpi_cards_html = ""
    default_colors = ["var(--siemens-petrol)", "var(--pass)", "var(--warn)", "var(--info)"]
    for i, k in enumerate(kpis):
        ktit = clean_german_text(k.get("title", f"Metric {i+1}"))
        kval = clean_german_text(str(k.get("value", "-")))
        ksub = clean_german_text(k.get("sub", ""))
        kcol = k.get("color") or default_colors[i % len(default_colors)]
        val_color = kcol if any(c in str(kcol) for c in ["pass", "fail", "warn", "info"]) else "var(--siemens-ink)"
        kpi_cards_html += f"""
        <div class="kpi-card" style="border-top: 4px solid {kcol};">
            <div class="kpi-title">{ktit}</div>
            <div class="kpi-value" style="color: {val_color};">{kval}</div>
            <div class="kpi-sub">{ksub}</div>
        </div>
        """
    kpi_grid_html = f'<div class="kpi-grid">{kpi_cards_html}</div>' if kpi_cards_html else ""

    # Summary Box
    summary_box_html = ""
    s_box = custom_data.get("summary_box")
    if s_box and isinstance(s_box, dict):
        s_status = clean_german_text(s_box.get("status", "VERIFIED"))
        s_title = clean_german_text(s_box.get("title", title))
        s_desc = clean_german_text(s_box.get("desc", subtitle))
        s_border = "var(--pass)" if any(w in s_status.upper() for w in ["PASS", "OK", "APPROV", "GO"]) else "var(--warn)"
        if any(w in s_status.upper() for w in ["FAIL", "BLOCK", "NO-GO"]):
            s_border = "var(--fail)"

        stat_pills_html = ""
        for pill in s_box.get("stats", []):
            pnum = clean_german_text(str(pill.get("num", "")))
            plbl = clean_german_text(str(pill.get("lbl", "")))
            pcls = pill.get("class", "")
            stat_pills_html += f"""
            <div class="stat-pill {pcls}">
                <span class="num">{pnum}</span>
                <span class="lbl">{plbl}</span>
            </div>
            """

        stats_wrap = f'<div class="summary-stats">{stat_pills_html}</div>' if stat_pills_html else ""
        summary_box_html = f"""
        <div class="summary-box" style="border-left-color: {s_border};">
            <div class="summary-state">{s_status}</div>
            <div>
                <h3>{s_title}</h3>
                <p>{s_desc}</p>
            </div>
            {stats_wrap}
        </div>
        """

    # Executive Notes
    exec_notes_html = ""
    for n in (custom_data.get("executive_notes") or state.get("executive_notes") or []):
        n_clean = clean_german_text(str(n).strip())
        if n_clean:
            exec_notes_html += f"""
            <div class="callout">
                <div style="font-weight:700; color:var(--siemens-ink); font-size:14px; margin-bottom:6px;">
                    💡 Engineering Advisory &amp; Quality Notes
                </div>
                <div style="color:#1e293b; font-size:13.5px; line-height:1.5;">{n_clean}</div>
            </div>
            """

    # Sections
    sections_html = ""
    for i, sec in enumerate(custom_data.get("sections") or [], 1):
        sec_title = clean_german_text(sec.get("title", f"{i}. Section"))
        sec_desc = clean_german_text(sec.get("desc", ""))
        sec_body = clean_german_text(sec.get("content_html") or sec.get("content") or "")
        desc_p = f'<p class="section-desc">{sec_desc}</p>' if sec_desc else ""
        sections_html += f"""
        <div class="section-title">{sec_title}</div>
        {desc_p}
        <div class="section-content" style="margin-bottom: 28px;">
            {sec_body}
        </div>
        """

    # Recommendation
    recom_html = ""
    recom = custom_data.get("recommendation")
    if recom and isinstance(recom, dict):
        r_status = clean_german_text(recom.get("status", "GO • APPROVED"))
        r_title = clean_german_text(recom.get("title", "Engineering Sign-off"))
        r_desc = clean_german_text(recom.get("desc", ""))
        r_color = "var(--pass)" if any(w in r_status.upper() for w in ["PASS", "OK", "APPROV", "GO"]) else "var(--warn)"
        if any(w in r_status.upper() for w in ["FAIL", "BLOCK", "NO-GO"]):
            r_color = "var(--fail)"
        recom_html = f"""
        <div class="section-title">Recommendation &amp; Operational Conclusion</div>
        <div class="summary-box" style="border-left-color: {r_color}; margin-bottom: 20px;">
            <div class="summary-state">{r_status}</div>
            <div>
                <h3>{r_title}</h3>
                <p>{r_desc}</p>
            </div>
        </div>
        """

    custom_css_html = f"<style>{state.get('injected_css')}</style>" if state.get("injected_css") else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &mdash; Siemens SAT</title>
<style>
{SIEMENS_CORPORATE_CSS}
</style>
{custom_css_html}
</head>
<body>
<div class="card">
    <div class="header">
        <div class="brand" aria-label="Siemens">SIEMENS</div>
        <div class="header-copy">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
        <div class="meta">
            <span>Product / Scope</span>
            <strong>{product}</strong>
            <span>Reference Target</span>
            <strong>{version}</strong>
            <span>Report Code</span>
            <strong style="color:#8ce0dc;">{ref_code}</strong>
            <span>Status</span>
            <strong>{status_str}</strong>
        </div>
    </div>
    <div class="content">
        {kpi_grid_html}
        {summary_box_html}
        {exec_notes_html}
        {sections_html}
        {recom_html}
    </div>
    <div class="footer">
        <div><strong>Siemens eMobility</strong> &mdash; System &amp; Application Test (SAT) Technical Report</div>
        <div>Confidential &middot; Internal Engineering &amp; Operational Review Only</div>
    </div>
</div>
</body>
</html>"""

def render_html_report(state):
    """
    Renders the official Siemens SAT Executive Meeting Report template.
    Unified directly from the two official template references:
    1. 'E:\SID\REPORTS\SID 10.0.0-11\SAT_Handoff_Report_FW_v10.0.0-11.html'
    2. 'E:\SID\REPORTS\SAT_Report_FW_v1.0.14_XPNB-1229.html'
    
    If state contains custom_report or report_type == 'custom', dynamically generates
    the custom report adapting the Siemens visual standard.
    """
    if state.get("custom_report") or state.get("report_type") == "custom":
        return render_custom_report(state.get("custom_report") or {}, state)
    plan_key = state.get("plan_key", "XPNB-1229")
    raw_summary = state.get("plan_summary", "SiFlex SAT Test Plan")
    plan_summary = clean_german_text(raw_summary)
    project_key = state.get("project_key", plan_key.split('-')[0])
    executions = state.get("executions", [])
    defects = state.get("defects", [])
    jira_base = state.get("jira_base_url", "https://si-emobility.atlassian.net").rstrip('/')
    lang = state.get("language", "en").lower()

    # Extract target versions from executions
    all_versions = list(dict.fromkeys([x.get("target_version") for x in executions if x.get("target_version") and x.get("target_version") != "Unspecified"]))
    target_fw_str = " + ".join(all_versions) if all_versions else "v1.0.14"

    # Derive Product name
    product_name = "SiFlex Charger" if "sif" in plan_summary.lower() or "xpnb" in plan_key.lower() else "SICHARGE D"
    if "sicharge" in plan_summary.lower():
        product_name = "SICHARGE D"

    # Global execution calculations
    tot_tests = sum(x.get("total", 0) for x in executions)
    tot_passed = sum(x.get("passed", 0) for x in executions)
    tot_failed = sum(x.get("failed", 0) for x in executions)
    tot_skipped = sum(x.get("skipped", 0) for x in executions)
    tot_todo = sum(x.get("todo", 0) for x in executions)
    
    executed = tot_passed + tot_failed
    global_rate = round(tot_passed / executed * 100, 1) if executed > 0 else 0.0

    # Defect metrics
    high_priority_defects = [d for d in defects if d.get("priority", "").lower() in ["blocker", "highest", "critical", "high", "major"]]
    high_count = len(high_priority_defects)
    total_defects = len(defects)

    # Status Determination
    if high_count == 0 and global_rate >= 90.0:
        summary_state_text = "APPROVED"
        summary_state_color = "var(--pass)"
        summary_state_bg = "#dff3e7"
        summary_title = f"{product_name} FW {target_fw_str} Recommended for Release"
        summary_desc = f"System Test validation completed across all {len(executions)} test execution suites for {target_fw_str}. High-voltage safety interlocks, dynamic charging curve and remote operations have been verified. Zero critical blockers."
        recom_badge = "GO &bull; APPROVED"
        recom_badge_bg = "#107c41"
        recom_badge_color = "#fff"
        recom_title = f"Release Approved for {product_name} FW {target_fw_str}"
        recom_title_color = "#0a552c"
        recom_border = "var(--pass)"
        recom_bg = "#f4faf6"
        recom_desc = f"System &amp; Application Test (SAT) recommends deploying firmware version <strong>{target_fw_str}</strong> into production. All core functional areas are production-ready with zero active safety blockers."
        status_meta_str = "Release Approved"
    else:
        summary_state_text = "IN TRIAGE" if high_count > 0 else "VALIDATION PROGRESS"
        summary_state_color = "var(--warn)" if high_count < 10 else "var(--fail)"
        summary_state_bg = "#fef3cd" if high_count < 10 else "#fde8e6"
        summary_title = f"{product_name} FW {target_fw_str} Verification &amp; Defect Triage"
        summary_desc = f"System Test validation in progress across {len(executions)} suites ({tot_tests} tests executed). {high_count} high-priority issues identified for engineering triage. Core charging dynamics and firmware target stability actively tracked."
        recom_badge = "TRIAGE &bull; IN PROGRESS" if high_count > 0 else "GO &bull; CONDITIONAL"
        recom_badge_bg = "#b56a00" if high_count < 10 else "#b42318"
        recom_badge_color = "#fff"
        recom_title = f"Release Under Active Triage for {product_name} FW {target_fw_str}"
        recom_title_color = "#8a6100" if high_count < 10 else "#721c24"
        recom_border = "var(--warn)" if high_count < 10 else "var(--fail)"
        recom_bg = "#fffdf5" if high_count < 10 else "#fffbfa"
        recom_desc = f"System &amp; Application Test (SAT) recommends resolving the {high_count} high-priority defects prioritized below prior to final production sign-off. Workarounds and root-cause analyses documented for engineering meeting review."
        status_meta_str = "Under Active Triage"

    # Custom Recommendation Override if provided by engineering copilot
    custom_recom = state.get("custom_recommendation")
    if custom_recom and isinstance(custom_recom, dict):
        c_status = custom_recom.get("status", "").strip().upper()
        c_title = clean_german_text(custom_recom.get("title", "").strip())
        c_desc = clean_german_text(custom_recom.get("desc", "").strip())
        if c_status:
            recom_badge = c_status
            if any(w in c_status for w in ["APPROVED", "PASS", "GO"]) and not any(w in c_status for w in ["CONDITIONAL", "NO", "NOT", "BLOCK"]):
                recom_badge_bg = "#107c41"
                recom_badge_color = "#fff"
                recom_title_color = "#0a552c"
                recom_border = "var(--pass)"
                recom_bg = "#f4faf6"
                summary_state_color = "var(--pass)"
                summary_state_bg = "#dff3e7"
            elif any(w in c_status for w in ["CONDITIONAL", "WARN", "TRIAGE", "REVIEW"]):
                recom_badge_bg = "#b56a00"
                recom_badge_color = "#fff"
                recom_title_color = "#8a6100"
                recom_border = "var(--warn)"
                recom_bg = "#fffdf5"
                summary_state_color = "var(--warn)"
                summary_state_bg = "#fef3cd"
            else:
                recom_badge_bg = "#b42318"
                recom_badge_color = "#fff"
                recom_title_color = "#721c24"
                recom_border = "var(--fail)"
                recom_bg = "#fffbfa"
                summary_state_color = "var(--fail)"
                summary_state_bg = "#fde8e6"
            summary_state_text = c_status
        if c_title:
            recom_title = c_title
            summary_title = c_title
        if c_desc:
            recom_desc = c_desc

    # Executive Notes / Quality Advisories
    exec_notes = state.get("executive_notes") or []
    exec_notes_html = ""
    for note in exec_notes:
        note_clean = clean_german_text(str(note).strip())
        if note_clean:
            exec_notes_html += f"""
        <div class="callout" style="margin: 20px 0; padding: 16px 20px; background: #f0fdf4; border-left: 5px solid var(--siemens-petrol); border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
            <div style="font-weight:700; color:var(--siemens-ink); font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                <span style="font-size:16px;">💡</span> Engineering Advisory &amp; Quality Notes
            </div>
            <div style="color:#1e293b; font-size:13.5px; line-height:1.5;">{note_clean}</div>
        </div>
        """

    # Custom Engineering Sections
    custom_sections = state.get("custom_sections") or []
    custom_sections_html = ""
    for sec in custom_sections:
        s_title = clean_german_text(sec.get("title", "Engineering Investigation"))
        s_content = clean_german_text(sec.get("content", ""))
        custom_sections_html += f"""
        <div class="section-title">{s_title}</div>
        <div class="custom-card" style="margin-bottom: 24px; padding: 20px 24px; background: #ffffff; border: 1px solid var(--line); border-left: 5px solid var(--siemens-petrol); border-radius: 6px; box-shadow: 0 2px 10px rgba(0,27,46,0.04);">
            <div style="color:var(--siemens-ink); font-size:13.5px; line-height:1.6;">{s_content}</div>
        </div>
        """

    # Execution Table Rows
    exec_rows_html = ""
    for x in executions:
        k = x.get("key", "")
        summ = clean_german_text(x.get("summary", ""))
        tot = x.get("total", 0)
        p = x.get("passed", 0)
        f = x.get("failed", 0)
        s = x.get("skipped", 0)
        rate = x.get("pass_rate", 0)
        t_ver = x.get("target_version", "")
        ver_badge = f'<br><span style="font-size:10.5px;color:var(--muted)">Target: <strong>{t_ver}</strong></span>' if t_ver and t_ver != "Unspecified" else ""

        if f == 0 and p > 0:
            res_cls = "result--pass"
            res_txt = "PASSED"
        elif f > 0:
            res_cls = "result--fail" if rate < 80 else "result--warn"
            res_txt = f"{rate}% PASS"
        elif s > 0 and p == 0 and f == 0:
            res_cls = "result--na"
            res_txt = "SKIPPED"
        else:
            res_cls = "result--info"
            res_txt = "EXECUTED"

        exec_rows_html += f"""
        <tr>
            <td><a class="jira-link" href="{jira_base}/browse/{k}" target="_blank"><strong>{k}</strong></a></td>
            <td><strong>{summ}</strong>{ver_badge}</td>
            <td style="text-align:center">{tot}</td>
            <td style="text-align:center;color:var(--pass);font-weight:700">{p}</td>
            <td style="text-align:center;color:{'var(--fail)' if f > 0 else 'inherit'};font-weight:{'700' if f > 0 else 'normal'}">{f}</td>
            <td style="text-align:center;color:var(--na)">{s}</td>
            <td style="text-align:center"><span class="result {res_cls}">{res_txt}</span></td>
        </tr>
        """

    if not exec_rows_html:
        exec_rows_html = "<tr><td colspan='7' style='text-align:center;padding:24px;color:#667085;'>No test executions recorded for this plan</td></tr>"

    # Total Summary Row for Executions
    total_row_html = f"""
    <tr class="total-row">
        <td>TOTAL</td>
        <td><strong>All {len(executions)} Mapped Execution Suites</strong></td>
        <td style="text-align:center">{tot_tests}</td>
        <td style="text-align:center;color:var(--pass);font-weight:700">{tot_passed}</td>
        <td style="text-align:center;color:{'var(--fail)' if tot_failed > 0 else 'inherit'};font-weight:700">{tot_failed}</td>
        <td style="text-align:center;color:var(--na)">{tot_skipped}</td>
        <td style="text-align:center"><span class="result result--pass" style="font-weight:800;">{global_rate}% PASS</span></td>
    </tr>
    """

    # Featured Demonstration Suite (Find Charging Curve or first major suite)
    featured_suite = None
    for x in executions:
        s_low = (x.get("summary") or "").lower()
        if "charging curve" in s_low or "curve" in s_low or "power" in s_low or "safe" in s_low:
            featured_suite = x
            break
    if not featured_suite and executions:
        featured_suite = executions[0]
    featured_suite_key = featured_suite.get("key", "XPECD-5458") if featured_suite else "XPECD-5458"
    featured_suite_title = clean_german_text(featured_suite.get("summary", "DC Charging Curve & Power Ramp Analysis")) if featured_suite else "DC Charging Curve Validation & Power Ramp Analysis"

    # Defect Rows with data attributes for search & priority filtering
    defect_rows_html = ""
    for d in defects:
        k = d.get("key", "")
        summ = clean_german_text(d.get("summary", ""))
        prio = clean_german_text(d.get("priority", "Medium"))
        st = clean_german_text(d.get("status", "Open"))
        ass = clean_german_text(d.get("assignee", "Unassigned"))
        rep = clean_german_text(d.get("reporter", "Unknown"))
        component = d.get("component") or project_key
        target_ver_str = d.get("affected_version") or target_fw_str

        prio_lower = prio.lower()
        is_blocker = prio_lower in ["blocker", "highest"]
        is_high = prio_lower in ["critical", "high", "major"] or is_blocker

        finding_cls = "result--block" if is_blocker else ("result--fail" if is_high else "result--pass")
        finding_txt = "BLOCKER" if is_blocker else ("HIGH RISK" if is_high else "LOW RISK")
        
        filter_prio_key = "Highest" if is_blocker else ("High" if is_high else ("Medium" if "med" in prio_lower else "Low"))
        search_data_text = f"{k.lower()} {summ.lower()} {st.lower()} {ass.lower()} {component.lower()}"

        risk_color = "var(--fail)" if is_high else "var(--pass)"
        risk_assessment = f"""
        <strong>Risk: <span style="color:{risk_color}">{finding_txt} ({st.upper()})</span></strong><br>
        Engineering triage status for <code>{component}</code>. Assignee: <strong>{ass}</strong> (Reported by {rep}).
        Issue tracked in Jira for target firmware resolution.
        """

        defect_rows_html += f"""
        <tr class="defect-row" data-priority="{filter_prio_key}" data-text="{search_data_text}">
            <td>
                <a class="jira-link" href="{jira_base}/browse/{k}" target="_blank"><strong>{k}</strong></a><br>
                <span style="font-size:10.5px;color:var(--muted)">{component} &middot; {ass}</span>
            </td>
            <td>
                <strong>{summ}</strong><br>
                <span style="font-size:11px;color:var(--muted)">Priority: <strong>{prio}</strong> | Status: <strong>{st}</strong></span>
            </td>
            <td style="text-align:center"><span class="result {finding_cls}">{finding_txt}</span></td>
            <td>{risk_assessment}</td>
        </tr>
        """

    if not defect_rows_html:
        defect_rows_html = "<tr><td colspan='4' style='text-align:center;padding:24px;color:#667085;'>No open project defects recorded in Jira</td></tr>"

    hidden_elements = set(state.get("hidden_elements") or [])
    if state.get("hide_summary_box"):
        hidden_elements.add("summary_box")
    if state.get("hide_kpi_cards"):
        hidden_elements.add("kpi_cards")
    if state.get("hide_section_2"):
        hidden_elements.add("section_2")
    if state.get("hide_section_3"):
        hidden_elements.add("section_3")

    # Injected custom CSS
    custom_css_html = ""
    if state.get("injected_css"):
        custom_css_html = f"<style id='injected-custom-css'>\n{state.get('injected_css')}\n</style>"

    # 1. Top 4 KPI Grid
    kpi_grid_html = ""
    if not any(k in hidden_elements for k in ["kpi_cards", "kpis", "kpi_grid"]):
        kpi_grid_html = f"""
        <!-- Top 4 KPI Grid -->
        <div class="kpi-grid">
            <div class="kpi-card" style="border-top: 4px solid var(--siemens-petrol);">
                <div class="kpi-title">TOTAL TESTS ({target_fw_str})</div>
                <div class="kpi-value">{tot_tests}</div>
                <div class="kpi-sub">Across {len(executions)} mapped execution suites</div>
            </div>
            <div class="kpi-card" style="border-top: 4px solid var(--pass);">
                <div class="kpi-title">OVERALL PASS RATE</div>
                <div class="kpi-value" style="color: var(--pass);">{global_rate}%</div>
                <div class="kpi-sub">{tot_passed} Passed of {executed} Executed ({tot_failed} Failed)</div>
            </div>
            <div class="kpi-card" style="border-top: 4px solid var(--fail);">
                <div class="kpi-title">OPEN DEFECTS ({project_key})</div>
                <div class="kpi-value" style="color: var(--fail);">{total_defects}</div>
                <div class="kpi-sub">{high_count} Highest &amp; High Priority items in triage</div>
            </div>
            <div class="kpi-card" style="border-top: 4px solid var(--warn);">
                <div class="kpi-title">CRITICAL FOCUS AREAS</div>
                <div class="kpi-value" style="font-size: 20px; color: var(--siemens-ink); padding-top: 6px;">Safety &amp; DC Power</div>
                <div class="kpi-sub">Active engineering tracking</div>
            </div>
        </div>
        """

    # 2. Hero Summary Box
    summary_box_html = ""
    if not any(k in hidden_elements for k in ["summary_box", "banner", "hero_banner", "hero", "resumo"]):
        summary_box_html = f"""
        <!-- Hero Summary Box -->
        <div class="summary-box" style="border-left-color: {summary_state_color};">
            <div class="summary-state" style="background:{summary_state_bg}; color:{summary_state_color};">{summary_state_text}</div>
            <div>
                <h3>{summary_title}</h3>
                <p>{summary_desc}</p>
            </div>
            <div class="summary-stats">
                <div class="stat-pill">
                    <span class="num">{tot_tests}</span>
                    <span class="lbl">Total Tests</span>
                </div>
                <div class="stat-pill stat-pill--pass">
                    <span class="num">{global_rate}%</span>
                    <span class="lbl">Pass Rate</span>
                </div>
                <div class="stat-pill stat-pill--fail">
                    <span class="num">{tot_failed}</span>
                    <span class="lbl">Failed</span>
                </div>
                <div class="stat-pill stat-pill--skip">
                    <span class="num">{tot_skipped}</span>
                    <span class="lbl">Skipped</span>
                </div>
            </div>
        </div>
        """

    # 3. Section 2: Featured Demonstration
    section_2_html = ""
    if not any(k in hidden_elements for k in ["section_2", "featured_demo", "video", "charging_curve"]):
        section_2_html = f"""
        <!-- Section 2: Featured Demonstration: DC Charging Curve -->
        <div class="section-title">2. Featured Demonstration: DC Charging Curve</div>
        <p class="section-desc">High-power DC charging session validation with CCS/PLC handshake, current transition stability, and thermal limit verification.</p>
        
        <div class="video-feature-card">
            <div class="video-layout">
                <div class="video-info">
                    <div class="badge" style="display:inline-block;padding:3px 10px;border-radius:3px;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;background:rgba(0,229,208,0.2);color:#00e5d0;margin-bottom:12px;border:1px solid rgba(0,229,208,0.4);">
                        FEATURED VALIDATION SUITE
                    </div>
                    <h3 style="margin:0 0 10px;font-size:20px;font-weight:600;letter-spacing:-0.2px;">
                        {featured_suite_title}
                    </h3>
                    <p style="margin:0 0 16px;color:#c7dde2;font-size:13px;line-height:1.5;">
                        Comprehensive verification of high-power DC charging power delivery, CCS/PLC communication handshake, dynamic current step responses, and thermal dissipation stability under continuous operating conditions.
                    </p>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
                        <div style="background:rgba(255,255,255,0.06);padding:10px 14px;border-radius:4px;border:1px solid rgba(255,255,255,0.1);">
                            <div style="font-size:10px;color:#8ce0dc;text-transform:uppercase;font-weight:700;">Communication Protocol</div>
                            <div style="font-size:13px;font-weight:600;margin-top:2px;">ISO 15118-2 / DIN 70121</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.06);padding:10px 14px;border-radius:4px;border:1px solid rgba(255,255,255,0.1);">
                            <div style="font-size:10px;color:#8ce0dc;text-transform:uppercase;font-weight:700;">Active Test Reference</div>
                            <div style="font-size:13px;font-weight:600;margin-top:2px;">{featured_suite_key}</div>
                        </div>
                    </div>
                    <div style="font-size:12px;color:#9fb7c0;">
                        <span>Target Execution Reference: </span>
                        <a class="jira-link" href="{jira_base}/browse/{featured_suite_key}" target="_blank" style="color:#00e5d0;font-weight:700;">{featured_suite_key}</a>
                    </div>
                </div>

                <div class="video-player-box" id="videoBox">
                    <video id="curveVideo" controls style="display:none;"></video>
                    <div id="videoPlaceholder">
                        <div style="font-size:36px;margin-bottom:8px;">📹</div>
                        <div style="font-size:13px;font-weight:600;color:#fff;">Demonstration Video Available</div>
                        <div style="font-size:11px;color:#9fb7c0;margin:6px 0 12px;max-width:240px;">
                            Drag and drop an MP4 recording here, or select from local storage.
                        </div>
                        <input type="file" id="videoFileInput" accept="video/mp4,video/*" style="display:none;" onchange="handleVideoFile(event)">
                        <button class="btn-load-video" onclick="document.getElementById('videoFileInput').click()">Select Video File (.mp4)</button>
                    </div>
                </div>
            </div>
        </div>
        """

    # 4. Section 3: Verified Validation Scope & Strengths
    section_3_html = ""
    if not any(k in hidden_elements for k in ["section_3", "scope_cards", "scope"]):
        section_3_html = f"""
        <!-- Section 3: Verified Validation Scope & Strengths -->
        <div class="section-title">3. Verified Validation Scope &amp; Strengths</div>
        <p class="section-desc">Key functional domains validated across current test cycle with production-readiness status.</p>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Core Charging &amp; Power Control</div>
                <div class="kpi-value" style="color:var(--pass)">Validated</div>
                <div class="kpi-sub">CCS/PLC Handshake, dynamic power sharing &amp; current ramp limits</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Remote Ops &amp; Connectivity</div>
                <div class="kpi-value" style="color:var(--pass)">Production Ready</div>
                <div class="kpi-sub">OCPP 1.6J/2.0.1, remote reboot triggers, diagnostics &amp; telemetry</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Firmware &amp; OTA Deployment</div>
                <div class="kpi-value" style="color:var(--pass)">Verified</div>
                <div class="kpi-sub">Over-the-Air deployment triggers, rollback protection &amp; state recovery</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Safety Systems &amp; Interlocks</div>
                <div class="kpi-value" style="color:{'var(--pass)' if high_count == 0 else 'var(--warn)'}">
                    {'100% Pass' if high_count == 0 else f'{high_count} Items in Triage'}
                </div>
                <div class="kpi-sub">Safe State, Emergency Stop, contactor feedback &amp; insulation monitoring</div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Siemens SAT Meeting Report &mdash; {product_name} FW {target_fw_str}</title>
<style>
{SIEMENS_CORPORATE_CSS}
</style>
{custom_css_html}
</head>
<body>
<div class="card">
    <div class="header">
        <div class="brand" aria-label="Siemens">SIEMENS</div>
        <div class="header-copy">
            <div class="eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
        <div class="meta">
            <span>Product / Scope</span>
            <strong>{product}</strong>
            <span>Reference Target</span>
            <strong>{version}</strong>
            <span>Report Code</span>
            <strong style="color:#8ce0dc;">{ref_code}</strong>
            <span>Status</span>
            <strong>{status_str}</strong>
        </div>
    </div>
    <div class="content">
        {kpi_grid_html}
        {summary_box_html}
        {exec_notes_html}
        {sections_html}
        {recom_html}
    </div>
    <div class="footer">
        <div><strong>Siemens eMobility</strong> &mdash; System &amp; Application Test (SAT) Technical Report</div>
        <div>Confidential &middot; Internal Engineering &amp; Operational Review Only</div>
    </div>
</div>
</body>
</html>"""

def render_html_report(state):
    """
    Renders the official Siemens SAT Executive Meeting Report template.
    Unified directly from the two official template references:
    1. 'E:\SID\REPORTS\SID 10.0.0-11\SAT_Handoff_Report_FW_v10.0.0-11.html'
    2. 'E:\SID\REPORTS\SAT_Report_FW_v1.0.14_XPNB-1229.html'
    
    If state contains custom_report or report_type == 'custom', dynamically generates
    the custom report adapting the Siemens visual standard.
    """
    if state.get("custom_report") or state.get("report_type") == "custom":
        return render_custom_report(state.get("custom_report") or {}, state)
    plan_key = state.get("plan_key", "XPNB-1229")
    raw_summary = state.get("plan_summary", "SiFlex SAT Test Plan")
    plan_summary = clean_german_text(raw_summary)
    project_key = state.get("project_key", plan_key.split('-')[0])
    executions = state.get("executions", [])
    defects = state.get("defects", [])
    jira_base = state.get("jira_base_url", "https://si-emobility.atlassian.net").rstrip('/')
    lang = state.get("language", "en").lower()

    # Extract target versions from executions
    all_versions = list(dict.fromkeys([x.get("target_version") for x in executions if x.get("target_version") and x.get("target_version") != "Unspecified"]))
    target_fw_str = " + ".join(all_versions) if all_versions else "v1.0.14"

    # Derive Product name
    product_name = "SiFlex Charger" if "sif" in plan_summary.lower() or "xpnb" in plan_key.lower() else "SICHARGE D"
    if "sicharge" in plan_summary.lower():
        product_name = "SICHARGE D"

    # Global execution calculations
    tot_tests = sum(x.get("total", 0) for x in executions)
    tot_passed = sum(x.get("passed", 0) for x in executions)
    tot_failed = sum(x.get("failed", 0) for x in executions)
    tot_skipped = sum(x.get("skipped", 0) for x in executions)
    tot_todo = sum(x.get("todo", 0) for x in executions)
    
    executed = tot_passed + tot_failed
    global_rate = round(tot_passed / executed * 100, 1) if executed > 0 else 0.0

    # Defect metrics
    high_priority_defects = [d for d in defects if d.get("priority", "").lower() in ["blocker", "highest", "critical", "high", "major"]]
    high_count = len(high_priority_defects)
    total_defects = len(defects)

    # Status Determination
    if high_count == 0 and global_rate >= 90.0:
        summary_state_text = "APPROVED"
        summary_state_color = "var(--pass)"
        summary_state_bg = "#dff3e7"
        summary_title = f"{product_name} FW {target_fw_str} Recommended for Release"
        summary_desc = f"System Test validation completed across all {len(executions)} test execution suites for {target_fw_str}. High-voltage safety interlocks, dynamic charging curve and remote operations have been verified. Zero critical blockers."
        recom_badge = "GO &bull; APPROVED"
        recom_badge_bg = "#107c41"
        recom_badge_color = "#fff"
        recom_title = f"Release Approved for {product_name} FW {target_fw_str}"
        recom_title_color = "#0a552c"
        recom_border = "var(--pass)"
        recom_bg = "#f4faf6"
        recom_desc = f"System &amp; Application Test (SAT) recommends deploying firmware version <strong>{target_fw_str}</strong> into production. All core functional areas are production-ready with zero active safety blockers."
        status_meta_str = "Release Approved"
    else:
        summary_state_text = "IN TRIAGE" if high_count > 0 else "VALIDATION PROGRESS"
        summary_state_color = "var(--warn)" if high_count < 10 else "var(--fail)"
        summary_state_bg = "#fef3cd" if high_count < 10 else "#fde8e6"
        summary_title = f"{product_name} FW {target_fw_str} Verification &amp; Defect Triage"
        summary_desc = f"System Test validation in progress across {len(executions)} suites ({tot_tests} tests executed). {high_count} high-priority issues identified for engineering triage. Core charging dynamics and firmware target stability actively tracked."
        recom_badge = "TRIAGE &bull; IN PROGRESS" if high_count > 0 else "GO &bull; CONDITIONAL"
        recom_badge_bg = "#b56a00" if high_count < 10 else "#b42318"
        recom_badge_color = "#fff"
        recom_title = f"Release Under Active Triage for {product_name} FW {target_fw_str}"
        recom_title_color = "#8a6100" if high_count < 10 else "#721c24"
        recom_border = "var(--warn)" if high_count < 10 else "var(--fail)"
        recom_bg = "#fffdf5" if high_count < 10 else "#fffbfa"
        recom_desc = f"System &amp; Application Test (SAT) recommends resolving the {high_count} high-priority defects prioritized below prior to final production sign-off. Workarounds and root-cause analyses documented for engineering meeting review."
        status_meta_str = "Under Active Triage"

    # Custom Recommendation Override if provided by engineering copilot
    custom_recom = state.get("custom_recommendation")
    if custom_recom and isinstance(custom_recom, dict):
        c_status = custom_recom.get("status", "").strip().upper()
        c_title = clean_german_text(custom_recom.get("title", "").strip())
        c_desc = clean_german_text(custom_recom.get("desc", "").strip())
        if c_status:
            recom_badge = c_status
            if any(w in c_status for w in ["APPROVED", "PASS", "GO"]) and not any(w in c_status for w in ["CONDITIONAL", "NO", "NOT", "BLOCK"]):
                recom_badge_bg = "#107c41"
                recom_badge_color = "#fff"
                recom_title_color = "#0a552c"
                recom_border = "var(--pass)"
                recom_bg = "#f4faf6"
                summary_state_color = "var(--pass)"
                summary_state_bg = "#dff3e7"
            elif any(w in c_status for w in ["CONDITIONAL", "WARN", "TRIAGE", "REVIEW"]):
                recom_badge_bg = "#b56a00"
                recom_badge_color = "#fff"
                recom_title_color = "#8a6100"
                recom_border = "var(--warn)"
                recom_bg = "#fffdf5"
                summary_state_color = "var(--warn)"
                summary_state_bg = "#fef3cd"
            else:
                recom_badge_bg = "#b42318"
                recom_badge_color = "#fff"
                recom_title_color = "#721c24"
                recom_border = "var(--fail)"
                recom_bg = "#fffbfa"
                summary_state_color = "var(--fail)"
                summary_state_bg = "#fde8e6"
            summary_state_text = c_status
        if c_title:
            recom_title = c_title
            summary_title = c_title
        if c_desc:
            recom_desc = c_desc

    # Executive Notes / Quality Advisories
    exec_notes = state.get("executive_notes") or []
    exec_notes_html = ""
    for note in exec_notes:
        note_clean = clean_german_text(str(note).strip())
        if note_clean:
            exec_notes_html += f"""
        <div class="callout" style="margin: 20px 0; padding: 16px 20px; background: #f0fdf4; border-left: 5px solid var(--siemens-petrol); border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
            <div style="font-weight:700; color:var(--siemens-ink); font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                <span style="font-size:16px;">💡</span> Engineering Advisory &amp; Quality Notes
            </div>
            <div style="color:#1e293b; font-size:13.5px; line-height:1.5;">{note_clean}</div>
        </div>
        """

    # Custom Engineering Sections
    custom_sections = state.get("custom_sections") or []
    custom_sections_html = ""
    for sec in custom_sections:
        s_title = clean_german_text(sec.get("title", "Engineering Investigation"))
        s_content = clean_german_text(sec.get("content", ""))
        custom_sections_html += f"""
        <div class="section-title">{s_title}</div>
        <div class="custom-card" style="margin-bottom: 24px; padding: 20px 24px; background: #ffffff; border: 1px solid var(--line); border-left: 5px solid var(--siemens-petrol); border-radius: 6px; box-shadow: 0 2px 10px rgba(0,27,46,0.04);">
            <div style="color:var(--siemens-ink); font-size:13.5px; line-height:1.6;">{s_content}</div>
        </div>
        """

    # Execution Table Rows
    exec_rows_html = ""
    for x in executions:
        k = x.get("key", "")
        summ = clean_german_text(x.get("summary", ""))
        tot = x.get("total", 0)
        p = x.get("passed", 0)
        f = x.get("failed", 0)
        s = x.get("skipped", 0)
        rate = x.get("pass_rate", 0)
        t_ver = x.get("target_version", "")
        ver_badge = f'<br><span style="font-size:10.5px;color:var(--muted)">Target: <strong>{t_ver}</strong></span>' if t_ver and t_ver != "Unspecified" else ""

        if f == 0 and p > 0:
            res_cls = "result--pass"
            res_txt = "PASSED"
        elif f > 0:
            res_cls = "result--fail" if rate < 80 else "result--warn"
            res_txt = f"{rate}% PASS"
        elif s > 0 and p == 0 and f == 0:
            res_cls = "result--na"
            res_txt = "SKIPPED"
        else:
            res_cls = "result--info"
            res_txt = "EXECUTED"

        exec_rows_html += f"""
        <tr>
            <td><a class="jira-link" href="{jira_base}/browse/{k}" target="_blank"><strong>{k}</strong></a></td>
            <td><strong>{summ}</strong>{ver_badge}</td>
            <td style="text-align:center">{tot}</td>
            <td style="text-align:center;color:var(--pass);font-weight:700">{p}</td>
            <td style="text-align:center;color:{'var(--fail)' if f > 0 else 'inherit'};font-weight:{'700' if f > 0 else 'normal'}">{f}</td>
            <td style="text-align:center;color:var(--na)">{s}</td>
            <td style="text-align:center"><span class="result {res_cls}">{res_txt}</span></td>
        </tr>
        """

    if not exec_rows_html:
        exec_rows_html = "<tr><td colspan='7' style='text-align:center;padding:24px;color:#667085;'>No test executions recorded for this plan</td></tr>"

    # Total Summary Row for Executions
    total_row_html = f"""
    <tr class="total-row">
        <td>TOTAL</td>
        <td><strong>All {len(executions)} Mapped Execution Suites</strong></td>
        <td style="text-align:center">{tot_tests}</td>
        <td style="text-align:center;color:var(--pass);font-weight:700">{tot_passed}</td>
        <td style="text-align:center;color:{'var(--fail)' if tot_failed > 0 else 'inherit'};font-weight:700">{tot_failed}</td>
        <td style="text-align:center;color:var(--na)">{tot_skipped}</td>
        <td style="text-align:center"><span class="result result--pass" style="font-weight:800;">{global_rate}% PASS</span></td>
    </tr>
    """

    # Featured Demonstration Suite (Find Charging Curve or first major suite)
    featured_suite = None
    for x in executions:
        s_low = (x.get("summary") or "").lower()
        if "charging curve" in s_low or "curve" in s_low or "power" in s_low or "safe" in s_low:
            featured_suite = x
            break
    if not featured_suite and executions:
        featured_suite = executions[0]
    featured_suite_key = featured_suite.get("key", "XPECD-5458") if featured_suite else "XPECD-5458"
    featured_suite_title = clean_german_text(featured_suite.get("summary", "DC Charging Curve & Power Ramp Analysis")) if featured_suite else "DC Charging Curve Validation & Power Ramp Analysis"

    # Defect Rows with data attributes for search & priority filtering
    defect_rows_html = ""
    for d in defects:
        k = d.get("key", "")
        summ = clean_german_text(d.get("summary", ""))
        prio = clean_german_text(d.get("priority", "Medium"))
        st = clean_german_text(d.get("status", "Open"))
        ass = clean_german_text(d.get("assignee", "Unassigned"))
        rep = clean_german_text(d.get("reporter", "Unknown"))
        component = d.get("component") or project_key
        target_ver_str = d.get("affected_version") or target_fw_str

        prio_lower = prio.lower()
        is_blocker = prio_lower in ["blocker", "highest"]
        is_high = prio_lower in ["critical", "high", "major"] or is_blocker

        finding_cls = "result--block" if is_blocker else ("result--fail" if is_high else "result--pass")
        finding_txt = "BLOCKER" if is_blocker else ("HIGH RISK" if is_high else "LOW RISK")
        
        filter_prio_key = "Highest" if is_blocker else ("High" if is_high else ("Medium" if "med" in prio_lower else "Low"))
        search_data_text = f"{k.lower()} {summ.lower()} {st.lower()} {ass.lower()} {component.lower()}"

        risk_color = "var(--fail)" if is_high else "var(--pass)"
        risk_assessment = f"""
        <strong>Risk: <span style="color:{risk_color}">{finding_txt} ({st.upper()})</span></strong><br>
        Engineering triage status for <code>{component}</code>. Assignee: <strong>{ass}</strong> (Reported by {rep}).
        Issue tracked in Jira for target firmware resolution.
        """

        defect_rows_html += f"""
        <tr class="defect-row" data-priority="{filter_prio_key}" data-text="{search_data_text}">
            <td>
                <a class="jira-link" href="{jira_base}/browse/{k}" target="_blank"><strong>{k}</strong></a><br>
                <span style="font-size:10.5px;color:var(--muted)">{component} &middot; {ass}</span>
            </td>
            <td>
                <strong>{summ}</strong><br>
                <span style="font-size:11px;color:var(--muted)">Priority: <strong>{prio}</strong> | Status: <strong>{st}</strong></span>
            </td>
            <td style="text-align:center"><span class="result {finding_cls}">{finding_txt}</span></td>
            <td>{risk_assessment}</td>
        </tr>
        """

    if not defect_rows_html:
        defect_rows_html = "<tr><td colspan='4' style='text-align:center;padding:24px;color:#667085;'>No open project defects recorded in Jira</td></tr>"

    hidden_elements = set(state.get("hidden_elements") or [])
    if state.get("hide_summary_box"):
        hidden_elements.add("summary_box")
    if state.get("hide_kpi_cards"):
        hidden_elements.add("kpi_cards")
    if state.get("hide_section_2"):
        hidden_elements.add("section_2")
    if state.get("hide_section_3"):
        hidden_elements.add("section_3")

    # Injected custom CSS
    custom_css_html = ""
    if state.get("injected_css"):
        custom_css_html = f"<style id='injected-custom-css'>\n{state.get('injected_css')}\n</style>"

    # 1. Top 4 KPI Grid
    kpi_grid_html = ""
    if not any(k in hidden_elements for k in ["kpi_cards", "kpis", "kpi_grid"]):
        kpi_grid_html = f"""
        <!-- Top 4 KPI Grid -->
        <div class="kpi-grid">
            <div class="kpi-card" style="border-top: 4px solid var(--siemens-petrol);">
                <div class="kpi-title">TOTAL TESTS ({target_fw_str})</div>
                <div class="kpi-value">{tot_tests}</div>
                <div class="kpi-sub">Across {len(executions)} mapped execution suites</div>
            </div>
            <div class="kpi-card" style="border-top: 4px solid var(--pass);">
                <div class="kpi-title">OVERALL PASS RATE</div>
                <div class="kpi-value" style="color: var(--pass);">{global_rate}%</div>
                <div class="kpi-sub">{tot_passed} Passed of {executed} Executed ({tot_failed} Failed)</div>
            </div>
            <div class="kpi-card" style="border-top: 4px solid var(--fail);">
                <div class="kpi-title">OPEN DEFECTS ({project_key})</div>
                <div class="kpi-value" style="color: var(--fail);">{total_defects}</div>
                <div class="kpi-sub">{high_count} Highest &amp; High Priority items in triage</div>
            </div>
            <div class="kpi-card" style="border-top: 4px solid var(--warn);">
                <div class="kpi-title">CRITICAL FOCUS AREAS</div>
                <div class="kpi-value" style="font-size: 20px; color: var(--siemens-ink); padding-top: 6px;">Safety &amp; DC Power</div>
                <div class="kpi-sub">Active engineering tracking</div>
            </div>
        </div>
        """

    # 2. Hero Summary Box
    summary_box_html = ""
    if not any(k in hidden_elements for k in ["summary_box", "banner", "hero_banner", "hero", "resumo"]):
        summary_box_html = f"""
        <!-- Hero Summary Box -->
        <div class="summary-box" style="border-left-color: {summary_state_color};">
            <div class="summary-state" style="background:{summary_state_bg}; color:{summary_state_color};">{summary_state_text}</div>
            <div>
                <h3>{summary_title}</h3>
                <p>{summary_desc}</p>
            </div>
            <div class="summary-stats">
                <div class="stat-pill">
                    <span class="num">{tot_tests}</span>
                    <span class="lbl">Total Tests</span>
                </div>
                <div class="stat-pill stat-pill--pass">
                    <span class="num">{global_rate}%</span>
                    <span class="lbl">Pass Rate</span>
                </div>
                <div class="stat-pill stat-pill--fail">
                    <span class="num">{tot_failed}</span>
                    <span class="lbl">Failed</span>
                </div>
                <div class="stat-pill stat-pill--skip">
                    <span class="num">{tot_skipped}</span>
                    <span class="lbl">Skipped</span>
                </div>
            </div>
        </div>
        """

    # 3. Section 2: Featured Demonstration
    section_2_html = ""
    if not any(k in hidden_elements for k in ["section_2", "featured_demo", "video", "charging_curve"]):
        section_2_html = f"""
        <!-- Section 2: Featured Demonstration: DC Charging Curve -->
        <div class="section-title">2. Featured Demonstration: DC Charging Curve</div>
        <p class="section-desc">High-power DC charging session validation with CCS/PLC handshake, current transition stability, and thermal limit verification.</p>
        
        <div class="video-feature-card">
            <div class="video-layout">
                <div class="video-info">
                    <div class="badge" style="display:inline-block;padding:3px 10px;border-radius:3px;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;background:rgba(0,229,208,0.2);color:#00e5d0;margin-bottom:12px;border:1px solid rgba(0,229,208,0.4);">
                        FEATURED VALIDATION SUITE
                    </div>
                    <h3 style="margin:0 0 10px;font-size:20px;font-weight:600;letter-spacing:-0.2px;">
                        {featured_suite_title}
                    </h3>
                    <p style="margin:0 0 16px;color:#c7dde2;font-size:13px;line-height:1.5;">
                        Comprehensive verification of high-power DC charging power delivery, CCS/PLC communication handshake, dynamic current step responses, and thermal dissipation stability under continuous operating conditions.
                    </p>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
                        <div style="background:rgba(255,255,255,0.06);padding:10px 14px;border-radius:4px;border:1px solid rgba(255,255,255,0.1);">
                            <div style="font-size:10px;color:#8ce0dc;text-transform:uppercase;font-weight:700;">Communication Protocol</div>
                            <div style="font-size:13px;font-weight:600;margin-top:2px;">ISO 15118-2 / DIN 70121</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.06);padding:10px 14px;border-radius:4px;border:1px solid rgba(255,255,255,0.1);">
                            <div style="font-size:10px;color:#8ce0dc;text-transform:uppercase;font-weight:700;">Active Test Reference</div>
                            <div style="font-size:13px;font-weight:600;margin-top:2px;">{featured_suite_key}</div>
                        </div>
                    </div>
                    <div style="font-size:12px;color:#9fb7c0;">
                        <span>Target Execution Reference: </span>
                        <a class="jira-link" href="{jira_base}/browse/{featured_suite_key}" target="_blank" style="color:#00e5d0;font-weight:700;">{featured_suite_key}</a>
                    </div>
                </div>

                <div class="video-player-box" id="videoBox">
                    <video id="curveVideo" controls style="display:none;"></video>
                    <div id="videoPlaceholder">
                        <div style="font-size:36px;margin-bottom:8px;">📹</div>
                        <div style="font-size:13px;font-weight:600;color:#fff;">Demonstration Video Available</div>
                        <div style="font-size:11px;color:#9fb7c0;margin:6px 0 12px;max-width:240px;">
                            Drag and drop an MP4 recording here, or select from local storage.
                        </div>
                        <input type="file" id="videoFileInput" accept="video/mp4,video/*" style="display:none;" onchange="handleVideoFile(event)">
                        <button class="btn-load-video" onclick="document.getElementById('videoFileInput').click()">Select Video File (.mp4)</button>
                    </div>
                </div>
            </div>
        </div>
        """

    # 4. Section 3: Verified Validation Scope & Strengths
    section_3_html = ""
    if not any(k in hidden_elements for k in ["section_3", "scope_cards", "scope"]):
        section_3_html = f"""
        <!-- Section 3: Verified Validation Scope & Strengths -->
        <div class="section-title">3. Verified Validation Scope &amp; Strengths</div>
        <p class="section-desc">Key functional domains validated across current test cycle with production-readiness status.</p>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Core Charging &amp; Power Control</div>
                <div class="kpi-value" style="color:var(--pass)">Validated</div>
                <div class="kpi-sub">CCS/PLC Handshake, dynamic power sharing &amp; current ramp limits</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Remote Ops &amp; Connectivity</div>
                <div class="kpi-value" style="color:var(--pass)">Production Ready</div>
                <div class="kpi-sub">OCPP 1.6J/2.0.1, remote reboot triggers, diagnostics &amp; telemetry</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Firmware &amp; OTA Deployment</div>
                <div class="kpi-value" style="color:var(--pass)">Verified</div>
                <div class="kpi-sub">Over-the-Air deployment triggers, rollback protection &amp; state recovery</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Safety Systems &amp; Interlocks</div>
                <div class="kpi-value" style="color:{'var(--pass)' if high_count == 0 else 'var(--warn)'}">
                    {'100% Pass' if high_count == 0 else f'{high_count} Items in Triage'}
                </div>
                <div class="kpi-sub">Safe State, Emergency Stop, contactor feedback &amp; insulation monitoring</div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Siemens SAT Meeting Report &mdash; {product_name} FW {target_fw_str}</title>
<style>
:root {{
  --siemens-petrol: #009999;
  --siemens-ink: #001b2e;
  --siemens-blue: #007993;
  --siemens-accent: #00e5d0;
  --mist: #f3f7f8;
  --line: #d7e2e5;
  --muted: #52636d;
  --pass: #107c41;
  --fail: #b42318;
  --warn: #c97a00;
  --info: #026aa7;
  --na: #667085;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: #e9f0f2;
  color: var(--siemens-ink);
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 14px;
  line-height: 1.45;
}}
.card {{
  max-width: 1240px;
  min-height: 100vh;
  margin: 0 auto;
  background: #fff;
  box-shadow: 0 0 32px rgba(0, 27, 46, .12);
}}
.header {{
  position: relative;
  overflow: hidden;
  min-height: 220px;
  padding: 32px 48px;
  color: #fff;
  background: var(--siemens-ink);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}}
.header::after {{
  content: "";
  position: absolute;
  right: -70px;
  bottom: -145px;
  width: 540px;
  height: 350px;
  border: 48px solid var(--siemens-petrol);
  border-radius: 50%;
  opacity: .95;
  pointer-events: none;
}}
.brand, .header-copy, .meta {{
  position: relative;
  z-index: 1;
}}
.brand {{
  font-family: Arial, sans-serif;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -2px;
  line-height: 1;
  color: var(--siemens-petrol);
}}
.header-copy {{
  align-self: flex-end;
  margin-top: 50px;
}}
.eyebrow {{
  margin-bottom: 8px;
  color: #8ce0dc;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.6px;
  text-transform: uppercase;
}}
.header h1 {{
  max-width: 780px;
  margin: 0;
  font-size: clamp(26px, 3.8vw, 38px);
  font-weight: 300;
  letter-spacing: -.8px;
  line-height: 1.1;
}}
.header h1 strong {{ font-weight: 700; }}
.subtitle {{
  margin: 12px 0 0;
  color: #c7dde2;
  font-size: 14.5px;
  max-width: 740px;
}}
.meta {{
  min-width: 220px;
  margin-left: 28px;
  padding: 14px 0 14px 18px;
  border-left: 2px solid var(--siemens-petrol);
  font-size: 12px;
  line-height: 1.7;
}}
.meta span {{
  display: block;
  color: #9fb7c0;
  text-transform: uppercase;
  letter-spacing: .7px;
  font-size: 10px;
  margin-top: 6px;
}}
.meta span:first-child {{ margin-top: 0; }}
.meta strong {{ color: #fff; font-size: 13.5px; font-weight: 600; }}

.content {{
  padding: 36px 48px 54px;
  overflow-x: hidden;
}}

/* Top 4 KPI Grid */
.kpi-grid {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 34px;
}}
@media (max-width: 900px) {{
  .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 560px) {{
  .kpi-grid {{ grid-template-columns: 1fr; }}
}}
.kpi-card {{
  padding: 18px 22px;
  background: var(--mist);
  border: 1px solid var(--line);
  border-radius: 2px;
}}
.kpi-title {{
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--muted);
  letter-spacing: .6px;
  margin-bottom: 4px;
}}
.kpi-value {{
  font-size: 32px;
  font-weight: 700;
  color: var(--siemens-ink);
  line-height: 1.15;
  margin: 4px 0;
}}
.kpi-sub {{
  font-size: 12px;
  color: var(--muted);
}}

/* Summary hero card */
.summary-box {{
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 24px;
  align-items: center;
  margin-bottom: 34px;
  padding: 22px 26px;
  border: 1px solid var(--line);
  border-left: 6px solid var(--pass);
  background: var(--mist);
  border-radius: 2px;
}}
.summary-state {{
  display: inline-block;
  padding: 8px 16px;
  background: #dff3e7;
  color: var(--pass);
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  border-radius: 4px;
  border: 1px solid rgba(16, 124, 65, 0.25);
}}
.summary-box h3 {{
  margin: 2px 0 4px;
  font-size: 21px;
  font-weight: 600;
  letter-spacing: -.25px;
}}
.summary-box p {{
  margin: 0;
  color: var(--muted);
  font-size: 13.5px;
}}
.summary-stats {{
  display: flex;
  gap: 10px;
  align-items: center;
  border-left: 1px solid var(--line);
  padding-left: 20px;
  flex-wrap: wrap;
}}
.stat-pill {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 4px;
  min-width: 68px;
  text-align: center;
}}
.stat-pill .num {{ font-size: 18px; font-weight: 700; color: var(--siemens-ink); line-height: 1.1; }}
.stat-pill .lbl {{ font-size: 9.5px; text-transform: uppercase; color: var(--muted); letter-spacing: .5px; margin-top: 3px; white-space: nowrap; }}
.stat-pill--pass {{ background: #f2f9f5; border-color: rgba(16, 124, 65, 0.25); }}
.stat-pill--pass .num {{ color: var(--pass); }}
.stat-pill--fail {{ background: #fdf3f2; border-color: rgba(180, 35, 24, 0.25); }}
.stat-pill--fail .num {{ color: var(--fail); }}
.stat-pill--skip {{ background: #f8f9fa; border-color: rgba(102, 112, 133, 0.25); }}
.stat-pill--skip .num {{ color: var(--na); }}

/* Section Title */
.section-title {{
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin: 36px 0 14px;
  color: var(--siemens-ink);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -.3px;
}}
.section-title::before {{
  content: "";
  width: 20px;
  height: 4px;
  background: var(--siemens-petrol);
}}
.section-desc {{
  margin: -6px 0 16px;
  color: var(--muted);
  font-size: 13px;
}}

/* Tables */
.table-wrap {{
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--line);
  margin-bottom: 24px;
  border-radius: 2px;
}}
table {{
  width: 100%;
  min-width: 820px;
  border-collapse: collapse;
  table-layout: fixed;
}}
th {{
  padding: 12px 14px;
  background: var(--siemens-ink);
  border-right: 1px solid #244051;
  color: #fff;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: .75px;
  text-align: left;
  text-transform: uppercase;
}}
th:last-child {{ border-right: 0; }}
td {{
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
  color: #263b47;
  font-size: 13px;
  vertical-align: middle;
  overflow-wrap: anywhere;
  word-break: break-word;
}}
tbody tr:nth-child(even) {{ background: #f9fbfc; }}
tbody tr:hover {{ background: #eef7f7; }}
tbody tr:last-child td {{ border-bottom: 0; }}
tbody tr.total-row {{
  background: #f1f5f8;
  font-weight: 700;
  border-top: 2px solid var(--siemens-ink);
}}
tbody tr.total-row td {{
  color: var(--siemens-ink);
}}
td strong {{ color: var(--siemens-ink); font-weight: 650; }}

/* Status tags */
.result {{
  display: inline-block;
  min-width: 80px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 800;
  letter-spacing: .6px;
  text-align: center;
  text-transform: uppercase;
}}
.result--pass {{ background: #dff3e7; color: var(--pass); }}
.result--fail {{ background: #fde8e6; color: var(--fail); }}
.result--warn {{ background: #fef3cd; color: var(--warn); }}
.result--block {{ background: #fbeae5; color: #b42318; border: 1px dashed #b42318; }}
.result--na {{ background: #eaecf0; color: var(--na); }}
.result--info {{ background: #e0f2fe; color: var(--info); }}

/* Links */
a.jira-link {{
  color: var(--siemens-blue);
  font-weight: 600;
  text-decoration: none;
}}
a.jira-link:hover {{
  text-decoration: underline;
  color: var(--siemens-petrol);
}}

/* Filter Bar */
.filter-bar {{
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}}
.search-input {{
  padding: 6px 12px;
  border: 1px solid var(--line);
  border-radius: 4px;
  font-size: 12.5px;
  outline: none;
  width: 240px;
}}
.search-input:focus {{
  border-color: var(--siemens-petrol);
}}
.filter-btn {{
  padding: 5px 12px;
  border: 1px solid var(--line);
  background: #ffffff;
  border-radius: 4px;
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.filter-btn.active {{
  background: var(--siemens-petrol);
  color: #ffffff;
  border-color: var(--siemens-petrol);
}}

/* Video Feature Card */
.video-feature-card {{
  background: linear-gradient(135deg, #001b2e 0%, #00364d 100%);
  border-radius: 4px;
  padding: 26px 30px;
  color: #fff;
  margin-bottom: 30px;
  box-shadow: 0 4px 16px rgba(0, 27, 46, 0.15);
}}
.video-layout {{
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 26px;
  align-items: center;
}}
@media (max-width: 900px) {{
  .video-layout {{ grid-template-columns: 1fr; }}
}}
.video-player-box {{
  background: #000;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-height: 280px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
}}
.video-player-box video {{
  width: 100%;
  max-height: 320px;
  object-fit: contain;
}}
.btn-load-video {{
  background: var(--siemens-petrol);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  margin-top: 10px;
}}
.btn-load-video:hover {{
  background: #00b3b3;
}}

/* Footer */
.footer {{
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 48px;
  background: var(--siemens-ink);
  color: #b6cbd3;
  font-size: 11px;
  letter-spacing: .3px;
}}
.footer strong {{ color: #fff; font-weight: 600; }}

@media print {{
  body {{ background: #fff; }}
  .card {{ max-width: none; box-shadow: none; }}
  .filter-bar {{ display: none !important; }}
}}
</style>
{custom_css_html}
</head>
<body>
<div class="card">
    <!-- Header -->
    <div class="header">
        <div class="brand" aria-label="Siemens">SIEMENS</div>
        <div class="header-copy">
            <div class="eyebrow">System &amp; Application Test (SAT) &middot; Release Meeting</div>
            <h1>{product_name} <strong>FW {target_fw_str} Release</strong></h1>
            <p class="subtitle">Official meeting report and verification analysis for firmware release candidate {target_fw_str} &middot; Test Plan {plan_key}.</p>
        </div>
        <div class="meta">
            <span>Product</span>
            <strong>{product_name}</strong>
            <span>Firmware Target</span>
            <strong>{target_fw_str}</strong>
            <span>Test Plan</span>
            <strong><a class="jira-link" href="{jira_base}/browse/{plan_key}" target="_blank" style="color:#8ce0dc;">{plan_key}</a></strong>
            <span>Status</span>
            <strong>{status_meta_str}</strong>
        </div>
    </div>

    <div class="content">
        {kpi_grid_html}
        {summary_box_html}
        {exec_notes_html}

        <!-- Section 1: Execution Suites Breakdown Table -->
        <div class="section-title">1. Execution Suites Breakdown</div>
        <p class="section-desc">Results and status distribution across the {len(executions)} test execution suites included in Test Plan {plan_key}:</p>
        
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th style="width:14%">Execution Key</th>
                        <th style="width:30%">Suite Scope</th>
                        <th style="width:10%;text-align:center">Total</th>
                        <th style="width:10%;text-align:center">Passed</th>
                        <th style="width:10%;text-align:center">Failed</th>
                        <th style="width:10%;text-align:center">Skipped</th>
                        <th style="width:16%;text-align:center">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {exec_rows_html}
                    {total_row_html}
                </tbody>
            </table>
        </div>

        {section_2_html}
        {section_3_html}

        <!-- Section 4: Defect & Residual Risk Analysis with Interactive Filter Bar -->
        <div class="section-title">4. Defect &amp; Residual Risk Analysis</div>
        <p class="section-desc">Detailed root cause analysis and operational risk classification for open project defects ({len(defects)} items):</p>
        
        <!-- Interactive Filter & Search Bar from XPNB-1229 Reference -->
        <div class="filter-bar">
            <input type="text" class="search-input" id="defectSearch" placeholder="Filter defects by keyword..." onkeyup="filterDefects()">
            <button class="filter-btn active" onclick="setPriorityFilter('ALL')">All</button>
            <button class="filter-btn" onclick="setPriorityFilter('Highest')">Highest</button>
            <button class="filter-btn" onclick="setPriorityFilter('High')">High</button>
            <button class="filter-btn" onclick="setPriorityFilter('Medium')">Medium</button>
            <button class="filter-btn" onclick="setPriorityFilter('Low')">Low</button>
        </div>

        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th style="width:14%">Issue Key</th>
                        <th style="width:28%">Title / Test Context</th>
                        <th style="width:12%;text-align:center">Finding</th>
                        <th style="width:46%">Risk Assessment &amp; Operational Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {defect_rows_html}
                </tbody>
            </table>
        </div>

        {custom_sections_html}

        <!-- Section 5: SAT Release Recommendation -->
        <div class="section-title">5. SAT Release Recommendation</div>
        <div class="summary-box" style="border-left-color: {recom_border}; background: {recom_bg}; margin-bottom: 20px;">
            <div class="summary-state" style="background:{recom_badge_bg};color:{recom_badge_color};">{recom_badge}</div>
            <div>
                <h3 style="color:{recom_title_color};">{recom_title}</h3>
                <p>{recom_desc}</p>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <div class="footer">
        <div><strong>Siemens eMobility</strong> &mdash; System &amp; Application Test (SAT) Validation Report</div>
        <div>Confidential &middot; For Internal Engineering &amp; Quality Management Review Only</div>
    </div>
</div>

<script>
// Video player drag and drop handlers
const videoBox = document.getElementById('videoBox');
const video = document.getElementById('curveVideo');
const placeholder = document.getElementById('videoPlaceholder');

if (videoBox) {{
    videoBox.addEventListener('dragover', (e) => {{ e.preventDefault(); videoBox.style.borderColor = 'var(--siemens-accent)'; }});
    videoBox.addEventListener('dragleave', () => {{ videoBox.style.borderColor = 'rgba(255,255,255,0.2)'; }});
    videoBox.addEventListener('drop', (e) => {{
        e.preventDefault();
        videoBox.style.borderColor = 'rgba(255,255,255,0.2)';
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('video/')) {{
            playFile(file);
        }}
    }});
}}

function handleVideoFile(event) {{
    const file = event.target.files[0];
    if (file) {{
        playFile(file);
    }}
}}

function playFile(file) {{
    if (!video || !placeholder) return;
    video.src = URL.createObjectURL(file);
    video.style.display = 'block';
    placeholder.style.display = 'none';
    video.play().catch(() => {{}});
}}

// Interactive Defect Search & Priority Filter Handler
let currentPriority = 'ALL';

function setPriorityFilter(priority) {{
    currentPriority = priority;
    document.querySelectorAll('.filter-btn').forEach(btn => {{
        if (btn.innerText.toUpperCase().startsWith(priority.toUpperCase())) {{
            btn.classList.add('active');
        }} else {{
            btn.classList.remove('active');
        }}
    }});
    filterDefects();
}}

function filterDefects() {{
    const searchInput = document.getElementById('defectSearch');
    const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const rows = document.querySelectorAll('.defect-row');
    
    rows.forEach(row => {{
        const prio = (row.getAttribute('data-priority') || '').toUpperCase();
        const text = (row.getAttribute('data-text') || '').toLowerCase();
        
        const matchPrio = (currentPriority === 'ALL' || prio === currentPriority.toUpperCase());
        const matchText = !query || text.includes(query);
        
        if (matchPrio && matchText) {{
            row.style.display = '';
        }} else {{
            row.style.display = 'none';
        }}
    }});
}}
</script>
</body>
</html>"""
    return html
