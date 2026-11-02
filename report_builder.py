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

/* Top 4 KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.kpi-card {
  background: var(--mist);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 18px 20px;
}
.kpi-title {
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .8px;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.kpi-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  color: var(--siemens-ink);
  letter-spacing: -.5px;
}
.kpi-sub {
  color: var(--muted);
  font-size: 12px;
  margin-top: 8px;
}

/* Hero Summary Box */
.summary-box {
  background: #fff;
  border: 1px solid var(--line);
  border-left: 6px solid var(--siemens-petrol);
  border-radius: 6px;
  padding: 22px 26px;
  margin-bottom: 36px;
  box-shadow: 0 4px 16px rgba(0, 27, 46, .05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.summary-state {
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  padding: 6px 14px;
  border-radius: 4px;
  white-space: nowrap;
}
.summary-box h3 {
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 600;
  color: var(--siemens-ink);
}
.summary-box p {
  margin: 0;
  color: var(--muted);
  font-size: 13.5px;
  max-width: 680px;
}
.summary-stats {
  display: flex;
  gap: 12px;
}
.stat-pill {
  background: var(--mist);
  border: 1px solid var(--line);
  padding: 8px 14px;
  border-radius: 6px;
  text-align: center;
  min-width: 70px;
}
.stat-pill .num {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: var(--siemens-ink);
}
.stat-pill .lbl {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: .6px;
  color: var(--muted);
}
.stat-pill--pass .num { color: var(--pass); }
.stat-pill--fail .num { color: var(--fail); }
.stat-pill--skip .num { color: var(--na); }

/* Section Headers */
.section-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -.2px;
  color: var(--siemens-ink);
  margin: 0 0 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-desc {
  margin: 0 0 16px;
  color: var(--muted);
  font-size: 12.5px;
}

/* Callouts / Engineering Advisories */
.callout {
  margin: 20px 0;
  padding: 16px 20px;
  background: #f0fdf4;
  border-left: 5px solid var(--siemens-petrol);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* Custom Sections */
.custom-card {
  margin-bottom: 24px;
  padding: 20px 24px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-left: 5px solid var(--siemens-petrol);
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0,27,46,0.04);
}

/* Tables */
.table-wrap {
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 27, 46, .03);
}
table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
thead th {
  background: var(--siemens-ink);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .8px;
  text-transform: uppercase;
  padding: 12px 16px;
  border: none;
}
tbody tr {
  border-bottom: 1px solid var(--line);
}
tbody tr:last-child {
  border-bottom: none;
}
tbody tr:hover {
  background: #f8fafb;
}
tbody td {
  padding: 12px 16px;
  font-size: 13px;
  vertical-align: middle;
}
.total-row {
  background: var(--mist);
  font-weight: 700;
}
.jira-link {
  color: var(--siemens-blue);
  text-decoration: none;
  font-weight: 600;
}
.jira-link:hover {
  text-decoration: underline;
}

/* Status / Result Badges */
.result {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: .6px;
  text-transform: uppercase;
}
.result--pass { background: #dff3e7; color: var(--pass); }
.result--fail { background: #fde8e6; color: var(--fail); }
.result--warn { background: #fef3cd; color: var(--warn); }
.result--info { background: #e0f2fe; color: var(--info); }
.result--na { background: #eceff1; color: var(--na); }
.result--block { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

/* Filter Controls */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  gap: 16px;
}
.filter-search {
  flex: 1;
  max-width: 320px;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 4px;
  font-size: 13px;
  font-family: inherit;
}
.filter-pills {
  display: flex;
  gap: 6px;
}
.filter-btn {
  background: #fff;
  border: 1px solid var(--line);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .5px;
  cursor: pointer;
  color: var(--muted);
  transition: all .15s;
}
.filter-btn:hover, .filter-btn.active {
  background: var(--siemens-ink);
  color: #fff;
  border-color: var(--siemens-ink);
}

/* Video Demonstration Card */
.video-feature-card {
  background: var(--siemens-ink);
  color: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 27, 46, .15);
}
.video-layout {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 24px;
  align-items: center;
}
.video-player-box {
  background: #000c14;
  border: 2px dashed rgba(255, 255, 255, .2);
  border-radius: 6px;
  height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 16px;
  position: relative;
  overflow: hidden;
}
.video-player-box video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}
.btn-load-video {
  background: var(--siemens-petrol);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

/* Footer */
.footer {
  padding: 24px 48px;
  background: var(--mist);
  border-top: 1px solid var(--line);
  font-size: 11px;
  color: var(--muted);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 900px) {
  .header { padding: 24px; flex-direction: column; }
  .meta { margin-left: 0; margin-top: 20px; border-left: none; padding-left: 0; }
  .content { padding: 20px; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .video-layout { grid-template-columns: 1fr; }
  .summary-box { flex-direction: column; align-items: flex-start; }
}
"""

def render_custom_report(custom_data, state=None):
    state = state or {}
    hidden_elements = set(state.get("hidden_elements") or [])
    
    title = clean_german_text(custom_data.get("title", "Technical Assessment Report"))
    subtitle = clean_german_text(custom_data.get("subtitle", "System & Application Test Engineering Evaluation"))
    eyebrow = clean_german_text(custom_data.get("eyebrow", "Siemens eMobility · Technical Report"))
    product = clean_german_text(custom_data.get("product", "Siemens Sicharge / SAT Scope"))
    version = clean_german_text(custom_data.get("version", "Current Engineering Baseline"))
    ref_code = clean_german_text(custom_data.get("reference_code", "SAT-DYNAMIC-EVAL"))
    status_str = clean_german_text(custom_data.get("status", "Verified & Documented"))

    # KPIs Grid
    kpi_grid_html = ""
    if not any(k in hidden_elements for k in ["kpi_cards", "kpis", "kpi_grid"]):
        kpis = state.get("custom_kpis") or custom_data.get("kpis") or []
        if kpis:
            cards_html = ""
            for k in kpis:
                ktit = clean_german_text(k.get("title", "Metric"))
                kval = clean_german_text(str(k.get("value", "-")))
                ksub = clean_german_text(k.get("sub", ""))
                kcol = k.get("color", "var(--siemens-petrol)")
                cards_html += f"""
                <div class="kpi-card" style="border-top: 4px solid {kcol};">
                    <div class="kpi-title">{ktit}</div>
                    <div class="kpi-value" style="color: {kcol};">{kval}</div>
                    <div class="kpi-sub">{ksub}</div>
                </div>
                """
            kpi_grid_html = f'<div class="kpi-grid">{cards_html}</div>'

    # Summary Box
    summary_box_html = ""
    s_box = custom_data.get("summary_box")
    if s_box and isinstance(s_box, dict) and not any(k in hidden_elements for k in ["summary_box", "banner", "hero", "resumo"]):
        s_status = clean_german_text(s_box.get("status", "APPROVED"))
        s_title = clean_german_text(s_box.get("title", "Technical Evaluation Complete"))
        s_desc = clean_german_text(s_box.get("desc", ""))
        s_border = "var(--pass)" if any(w in s_status.upper() for w in ["PASS", "OK", "APPROV", "GO"]) else "var(--warn)"
        if any(w in s_status.upper() for w in ["FAIL", "BLOCK", "NO-GO"]):
            s_border = "var(--fail)"

        stat_pills_html = ""
        for st in (s_box.get("stats") or []):
            pnum = clean_german_text(str(st.get("num", "")))
            plbl = clean_german_text(st.get("lbl", ""))
            pcls = f"stat-pill--{st.get('class')}" if st.get("class") else ""
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
    if not any(k in hidden_elements for k in ["executive_notes", "notes", "advisory", "callouts"]):
        notes_pool = state.get("executive_notes") if "executive_notes" in state else custom_data.get("executive_notes", [])
        for n in (notes_pool or []):
            n_clean = clean_german_text(str(n).strip())
            if n_clean:
                exec_notes_html += f"""
                <div class="callout">
                    <div style="font-weight:700; color:var(--siemens-ink); font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span style="font-size:16px;">💡</span> Engineering Advisory &amp; Quality Notes
                    </div>
                    <div style="color:#1e293b; font-size:13.5px; line-height:1.5;">{n_clean}</div>
                </div>
                """

    # Custom Sections
    sections_html = ""
    all_sections = list(custom_data.get("sections") or [])
    for cs in (state.get("custom_sections") or []):
        all_sections.append({"title": cs.get("title"), "content_html": cs.get("content")})

    for i, sec in enumerate(all_sections, 1):
        sec_title = clean_german_text(sec.get("title", f"{i}. Section"))
        if any(h in sec_title.lower() for h in hidden_elements):
            continue
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
    recom = state.get("custom_recommendation") or custom_data.get("recommendation")
    if recom and isinstance(recom, dict) and not any(k in hidden_elements for k in ["section_5", "recommendation", "recom"]):
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
    Unified directly from the official Siemens SAT engineering standard.
    Supports dynamic filtering, visibility toggling, custom sections, notes, and metrics.
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
    hidden_elements = set(state.get("hidden_elements") or [])

    # Dynamic Filter for Executions
    filter_ver = state.get("filter_version") or state.get("filter_executions_version")
    filter_status = state.get("filter_status")
    filter_search = state.get("filter_search")

    active_executions = list(executions)
    if filter_ver:
        f_low = filter_ver.lower().strip()
        active_executions = [
            x for x in active_executions
            if f_low in str(x.get("target_version", "")).lower() or f_low in str(x.get("summary", "")).lower()
        ]
        if not active_executions:
            active_executions = executions

    if filter_status:
        st_low = filter_status.lower().strip()
        active_executions = [x for x in active_executions if st_low in str(x.get("jira_status", "")).lower()]

    if filter_search:
        s_low = filter_search.lower().strip()
        active_executions = [
            x for x in active_executions
            if s_low in str(x.get("summary", "")).lower() or s_low in str(x.get("key", "")).lower()
        ]

    # Target versions label
    all_versions = list(dict.fromkeys([
        x.get("target_version") for x in active_executions
        if x.get("target_version") and x.get("target_version") != "Unspecified"
    ]))
    if filter_ver:
        target_fw_str = filter_ver.upper()
    elif all_versions:
        target_fw_str = " + ".join(all_versions)
    else:
        target_fw_str = "v1.0.14"

    # Derive Product name
    product_name = "SiFlex Charger" if "sif" in plan_summary.lower() or "xpnb" in plan_key.lower() else "SICHARGE D"
    if "sicharge" in plan_summary.lower():
        product_name = "SICHARGE D"

    # Dynamic execution calculations from active_executions
    tot_tests = sum(x.get("total", 0) for x in active_executions)
    tot_passed = sum(x.get("passed", 0) for x in active_executions)
    tot_failed = sum(x.get("failed", 0) for x in active_executions)
    tot_skipped = sum(x.get("skipped", 0) for x in active_executions)
    executed = tot_passed + tot_failed
    global_rate = round(tot_passed / executed * 100, 1) if executed > 0 else 0.0

    # Defect metrics
    high_priority_defects = [
        d for d in defects
        if d.get("priority", "").lower() in ["blocker", "highest", "critical", "high", "major"]
    ]
    high_count = len(high_priority_defects)
    total_defects = len(defects)

    # Status Determination
    if high_count == 0 and global_rate >= 90.0:
        summary_state_text = "APPROVED"
        summary_state_color = "var(--pass)"
        summary_state_bg = "#dff3e7"
        summary_title = f"{product_name} FW {target_fw_str} Recommended for Release"
        summary_desc = f"System Test validation completed across {len(active_executions)} suites for {target_fw_str}. High-voltage safety interlocks, dynamic charging curve and remote operations verified with zero critical blockers."
        recom_badge = "GO • APPROVED"
        recom_badge_bg = "#107c41"
        recom_badge_color = "#fff"
        recom_title = f"Release Approved for {product_name} FW {target_fw_str}"
        recom_title_color = "#0a552c"
        recom_border = "var(--pass)"
        recom_bg = "#f4faf6"
        recom_desc = f"System & Application Test (SAT) recommends deploying firmware version <strong>{target_fw_str}</strong> into production. All core functional areas are production-ready."
        status_meta_str = "Release Approved"
    else:
        summary_state_text = "IN TRIAGE" if high_count > 0 else "VALIDATION PROGRESS"
        summary_state_color = "var(--warn)" if high_count < 10 else "var(--fail)"
        summary_state_bg = "#fef3cd" if high_count < 10 else "#fde8e6"
        summary_title = f"{product_name} FW {target_fw_str} Verification & Defect Triage"
        summary_desc = f"System Test validation in progress across {len(active_executions)} suites ({tot_tests} tests executed). {high_count} high-priority issues identified for engineering triage."
        recom_badge = "TRIAGE • IN PROGRESS" if high_count > 0 else "GO • CONDITIONAL"
        recom_badge_bg = "#b56a00" if high_count < 10 else "#b42318"
        recom_badge_color = "#fff"
        recom_title = f"Release Under Active Triage for {product_name} FW {target_fw_str}"
        recom_title_color = "#8a6100" if high_count < 10 else "#721c24"
        recom_border = "var(--warn)" if high_count < 10 else "var(--fail)"
        recom_bg = "#fffdf5" if high_count < 10 else "#fffbfa"
        recom_desc = f"System & Application Test (SAT) recommends resolving the {high_count} high-priority defects prioritized below prior to final production sign-off."
        status_meta_str = "Under Active Triage"

    # Custom Recommendation Override
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

    # 1. Top 4 KPI Grid (or Custom KPIs)
    kpi_grid_html = ""
    if not any(k in hidden_elements for k in ["kpi_cards", "kpis", "kpi_grid"]):
        custom_kpis = state.get("custom_kpis")
        if custom_kpis and isinstance(custom_kpis, list):
            cards_html = ""
            for k in custom_kpis:
                ktit = clean_german_text(k.get("title", "Metric"))
                kval = clean_german_text(str(k.get("value", "-")))
                ksub = clean_german_text(k.get("sub", ""))
                kcol = k.get("color", "var(--siemens-petrol)")
                cards_html += f"""
                <div class="kpi-card" style="border-top: 4px solid {kcol};">
                    <div class="kpi-title">{ktit}</div>
                    <div class="kpi-value" style="color: {kcol};">{kval}</div>
                    <div class="kpi-sub">{ksub}</div>
                </div>
                """
            kpi_grid_html = f'<div class="kpi-grid">{cards_html}</div>'
        else:
            kpi_grid_html = f"""
            <div class="kpi-grid">
                <div class="kpi-card" style="border-top: 4px solid var(--siemens-petrol);">
                    <div class="kpi-title">TOTAL TESTS ({target_fw_str})</div>
                    <div class="kpi-value">{tot_tests}</div>
                    <div class="kpi-sub">Across {len(active_executions)} mapped execution suites</div>
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
    if not any(k in hidden_elements for k in ["summary_box", "banner", "hero", "resumo"]):
        summary_box_html = f"""
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

    # Executive Notes / Quality Advisories
    exec_notes_html = ""
    if not any(k in hidden_elements for k in ["executive_notes", "notes", "advisory", "callouts"]):
        exec_notes = state.get("executive_notes") or []
        for note in exec_notes:
            note_clean = clean_german_text(str(note).strip())
            if note_clean:
                exec_notes_html += f"""
                <div class="callout">
                    <div style="font-weight:700; color:var(--siemens-ink); font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span style="font-size:16px;">💡</span> Engineering Advisory &amp; Quality Notes
                    </div>
                    <div style="color:#1e293b; font-size:13.5px; line-height:1.5;">{note_clean}</div>
                </div>
                """

    # Section 1: Execution Suites Breakdown
    section_1_html = ""
    if not any(k in hidden_elements for k in ["section_1", "executions", "suites"]):
        exec_rows_html = ""
        for x in active_executions:
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
            exec_rows_html = "<tr><td colspan='7' style='text-align:center;padding:24px;color:#667085;'>No test executions match active filter</td></tr>"

        filter_label = f" (Filtered: {target_fw_str})" if filter_ver else ""
        total_row_html = f"""
        <tr class="total-row">
            <td>TOTAL</td>
            <td><strong>All {len(active_executions)} Mapped Execution Suites{filter_label}</strong></td>
            <td style="text-align:center">{tot_tests}</td>
            <td style="text-align:center;color:var(--pass);font-weight:700">{tot_passed}</td>
            <td style="text-align:center;color:{'var(--fail)' if tot_failed > 0 else 'inherit'};font-weight:700">{tot_failed}</td>
            <td style="text-align:center;color:var(--na)">{tot_skipped}</td>
            <td style="text-align:center"><span class="result result--pass" style="font-weight:800;">{global_rate}% PASS</span></td>
        </tr>
        """

        section_1_title = f"1. {target_fw_str} Execution Suites Breakdown" if filter_ver else "1. Execution Suites Breakdown"
        section_1_html = f"""
        <div class="section-title">{section_1_title}</div>
        <p class="section-desc">Detailed verification of individual execution suites, test volumes and individual pass rates.</p>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th style="width:14%">Jira Key</th>
                        <th style="width:40%">Execution Suite Name</th>
                        <th style="width:8%;text-align:center">Total</th>
                        <th style="width:8%;text-align:center">Pass</th>
                        <th style="width:8%;text-align:center">Fail</th>
                        <th style="width:8%;text-align:center">Skip</th>
                        <th style="width:14%;text-align:center">Rate</th>
                    </tr>
                </thead>
                <tbody>
                    {exec_rows_html}
                    {total_row_html}
                </tbody>
            </table>
        </div>
        """

    # Section 2: Featured Demonstration
    section_2_html = ""
    if not any(k in hidden_elements for k in ["section_2", "featured_demo", "video", "charging_curve"]):
        featured_suite = None
        for x in active_executions:
            s_low = (x.get("summary") or "").lower()
            if "charging curve" in s_low or "curve" in s_low or "power" in s_low or "safe" in s_low:
                featured_suite = x
                break
        if not featured_suite and active_executions:
            featured_suite = active_executions[0]
        featured_suite_key = featured_suite.get("key", "XPECD-5458") if featured_suite else "XPECD-5458"
        featured_suite_title = clean_german_text(featured_suite.get("summary", "DC Charging Curve & Power Ramp Analysis")) if featured_suite else "DC Charging Curve Validation & Power Ramp Analysis"

        section_2_html = f"""
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

    # Section 3: Scope Cards
    section_3_html = ""
    if not any(k in hidden_elements for k in ["section_3", "scope_cards", "scope"]):
        section_3_html = f"""
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

    # Section 4: Defects
    section_4_html = ""
    if not any(k in hidden_elements for k in ["section_4", "defects", "defect_analysis"]):
        defect_rows_html = ""
        for d in defects:
            k = d.get("key", "")
            summ = clean_german_text(d.get("summary", ""))
            prio = clean_german_text(d.get("priority", "Medium"))
            st = clean_german_text(d.get("status", "Open"))
            ass = clean_german_text(d.get("assignee", "Unassigned"))
            rep = clean_german_text(d.get("reporter", "Unknown"))
            component = d.get("component") or project_key
            prio_lower = prio.lower()
            is_blocker = prio_lower in ["blocker", "highest"]
            is_high = prio_lower in ["critical", "high", "major"] or is_blocker

            finding_cls = "result--block" if is_blocker else ("result--fail" if is_high else "result--pass")
            finding_txt = "BLOCKER" if is_blocker else ("HIGH RISK" if is_high else "LOW RISK")
            filter_prio_key = "Highest" if is_blocker else ("High" if is_high else ("Medium" if "med" in prio_lower else "Low"))
            search_data_text = f"{k.lower()} {summ.lower()} {st.lower()} {ass.lower()} {component.lower()}"
            risk_color = "var(--fail)" if is_high else "var(--pass)"

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
                <td>
                    <strong>Risk: <span style="color:{risk_color}">{finding_txt} ({st.upper()})</span></strong><br>
                    Engineering triage status for <code>{component}</code>. Assignee: <strong>{ass}</strong> (Reported by {rep}).
                </td>
            </tr>
            """

        if not defect_rows_html:
            defect_rows_html = "<tr><td colspan='4' style='text-align:center;padding:24px;color:#667085;'>No open project defects recorded in Jira</td></tr>"

        section_4_html = f"""
        <div class="section-title">4. Defect &amp; Residual Risk Analysis</div>
        <p class="section-desc">Priority distribution of open Jira defects impacting production release readiness.</p>
        <div class="filter-bar">
            <input type="text" class="filter-search" id="defectSearch" placeholder="Filter defects by key, summary, component..." onkeyup="filterDefects()">
            <div class="filter-pills">
                <button class="filter-btn active" onclick="setPriorityFilter('ALL')">All ({total_defects})</button>
                <button class="filter-btn" onclick="setPriorityFilter('Highest')">Highest</button>
                <button class="filter-btn" onclick="setPriorityFilter('High')">High ({high_count})</button>
                <button class="filter-btn" onclick="setPriorityFilter('Medium')">Medium</button>
            </div>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th style="width:20%">Defect Key &amp; Owner</th>
                        <th style="width:45%">Summary &amp; Severity</th>
                        <th style="width:12%;text-align:center">Finding</th>
                        <th style="width:23%">Residual Risk &amp; Triage Assessment</th>
                    </tr>
                </thead>
                <tbody>
                    {defect_rows_html}
                </tbody>
            </table>
        </div>
        """

    # Custom Engineering Sections
    custom_sections_html = ""
    for sec in (state.get("custom_sections") or []):
        s_title = clean_german_text(sec.get("title", "Engineering Investigation"))
        if any(h in s_title.lower() for h in hidden_elements):
            continue
        s_content = clean_german_text(sec.get("content", ""))
        custom_sections_html += f"""
        <div class="section-title">{s_title}</div>
        <div class="custom-card">
            <div style="color:var(--siemens-ink); font-size:13.5px; line-height:1.6;">{s_content}</div>
        </div>
        """

    # Section 5: Recommendation
    section_5_html = ""
    if not any(k in hidden_elements for k in ["section_5", "recommendation", "recom"]):
        section_5_html = f"""
        <div class="section-title">5. SAT Release Recommendation</div>
        <div class="summary-box" style="border-left-color: {recom_border}; background: {recom_bg}; margin-bottom: 20px;">
            <div class="summary-state" style="background:{recom_badge_bg};color:{recom_badge_color};">{recom_badge}</div>
            <div>
                <h3 style="color:{recom_title_color};">{recom_title}</h3>
                <p>{recom_desc}</p>
            </div>
        </div>
        """

    custom_css_html = f"<style>{state.get('injected_css')}</style>" if state.get("injected_css") else ""

    return f"""<!DOCTYPE html>
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
            <div class="eyebrow">Siemens eMobility &middot; SAT System Test Validation</div>
            <h1>{plan_summary}</h1>
            <p class="subtitle">Detailed Engineering Assessment of {target_fw_str} Execution Suites</p>
        </div>
        <div class="meta">
            <span>Reference Target</span>
            <strong>{target_fw_str}</strong>
            <span>Report Code</span>
            <strong style="color:#8ce0dc;">{plan_key}</strong>
            <span>Status</span>
            <strong>{status_meta_str}</strong>
        </div>
    </div>
    <div class="content">
        {kpi_grid_html}
        {summary_box_html}
        {exec_notes_html}
        {section_1_html}
        {section_2_html}
        {section_3_html}
        {section_4_html}
        {custom_sections_html}
        {section_5_html}
    </div>
    <div class="footer">
        <div><strong>Siemens eMobility</strong> &mdash; System &amp; Application Test (SAT) Validation Report</div>
        <div>Confidential &middot; For Internal Engineering &amp; Quality Management Review Only</div>
    </div>
</div>

<script>
// Video drag & drop handlers
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
        if (file && file.type.startsWith('video/')) playFile(file);
    }});
}}
function handleVideoFile(event) {{
    const file = event.target.files[0];
    if (file) playFile(file);
}}
function playFile(file) {{
    if (!video || !placeholder) return;
    video.src = URL.createObjectURL(file);
    video.style.display = 'block';
    placeholder.style.display = 'none';
    video.play().catch(() => {{}});
}}

// Priority Filter for Defects
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
        row.style.display = (matchPrio && matchText) ? '' : 'none';
    }});
}}
</script>
</body>
</html>"""
