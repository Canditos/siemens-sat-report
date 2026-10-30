import os
import sys
import json
import webbrowser
import threading
import time
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from report_builder import render_html_report
from jira_xray_client import JiraXrayClient

app = FastAPI(title="Siemens SAT Report Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from gemini_copilot import GeminiCopilot

client = JiraXrayClient()
copilot = GeminiCopilot(client)

global_state = {
    "plan_key": "XPNB-1229",
    "project_key": "XPNB",
    "plan_summary": "Test Plan - SiFlex Release 3 - v1.0.12 + v1.0.14",
    "use_tabs": False,
    "group_by_version": True,
    "show_prepared_by": False,
    "prepared_by": "",
    "active_tab": "tab-executions",
    "executions": [],
    "defects": [],
    "custom_sections": [],
    "jira_base_url": client.jira_base_url or "https://si-emobility.atlassian.net",
    "dest_folder": r"E:\FLEX" if os.path.exists(r"E:\FLEX") else os.path.join(CURRENT_DIR, "exports"),
    "language": "en",
    "current_html": ""
}

# Initial render with official recommended Siemens SAT template
try:
    plan_to_load = global_state.get("plan_key", "XPNB-1229")
    info = client.get_issue_info(plan_to_load)
    if info:
        global_state["plan_summary"] = info.get("summary", global_state["plan_summary"])
        global_state["project_key"] = info.get("project", plan_to_load.split('-')[0])
    execs = client.get_test_executions(plan_to_load)
    metrics = client.get_execution_metrics(execs)
    global_state["executions"] = metrics
    defects = client.get_plan_linked_defects(plan_to_load, execs)
    global_state["defects"] = defects
    global_state["current_html"] = render_html_report(global_state)
    print(f"[Server] Template Oficial Siemens SAT carregado com sucesso ({len(metrics)} execucoes, {len(defects)} defeitos)!")
except Exception as e:
    print(f"[Server] Initial render error: {e}")
    global_state["current_html"] = render_html_report(global_state)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(CURRENT_DIR, "web", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>web/index.html não encontrado</h1>", status_code=404)

@app.get("/api/state")
async def get_state():
    return {
        "state": global_state,
        "services": {
            "jira": "online" if bool(client._auth_header) else "offline",
            "xray": "online" if bool(client.jwt or client.xray_cid) else "offline",
            "gemini": "online"
        },
        "telemetry": {
            "active_model": copilot.model,
            "session_stats": getattr(copilot, "session_stats", {}),
            "fallback_models": copilot.fallback_models
        }
    }

@app.post("/api/set_language")
async def set_language_endpoint(payload: Dict[str, Any]):
    global global_state
    new_lang = payload.get("language", "en").lower()
    global_state["language"] = new_lang

    import importlib
    import report_builder as rb_mod
    importlib.reload(rb_mod)

    global_state["hidden_elements"] = []
    global_state["injected_css"] = ""
    global_state["executive_notes"] = []
    global_state["custom_sections"] = []
    global_state.pop("custom_recommendation", None)

    global_state["current_html"] = rb_mod.render_html_report(global_state)
    return {
        "status": "ok",
        "language": new_lang,
        "html": global_state["current_html"]
    }

@app.post("/api/restore_template")
async def restore_template_endpoint():
    global global_state
    import report_builder as rb_mod
    import importlib
    importlib.reload(rb_mod)

    plan_key = global_state.get("plan_key", "XPNB-1229")
    try:
        execs = client.get_test_executions(plan_key)
        metrics = client.get_execution_metrics(execs)
        global_state["executions"] = metrics
        defects = client.get_plan_linked_defects(plan_key, execs)
        global_state["defects"] = defects
        info = client.get_issue_info(plan_key)
        if info:
            global_state["plan_summary"] = info.get("summary", global_state.get("plan_summary"))
            global_state["project_key"] = info.get("project", plan_key.split('-')[0])
    except Exception as e:
        print(f"[Server] Error refreshing Jira data on restore_template: {e}")

    global_state["hidden_elements"] = []
    global_state["injected_css"] = ""
    global_state["executive_notes"] = []
    global_state["custom_sections"] = []
    global_state.pop("custom_recommendation", None)

    global_state["current_html"] = rb_mod.render_html_report(global_state)
    return {
        "status": "ok",
        "html": global_state["current_html"],
        "plan_key": plan_key
    }

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    global global_state
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    prompt = payload.get("prompt", "")
    image_b64 = payload.get("image_b64")
    images_b64 = payload.get("images_b64") or []
    if image_b64 and image_b64 not in images_b64:
        images_b64.insert(0, image_b64)
    incoming_state = payload.get("state") or global_state
    history = payload.get("history") or []

    # Dynamic reload ensures changes take effect immediately without restarting server
    import importlib
    import gemini_copilot as gc_mod
    import report_builder as rb_mod
    importlib.reload(rb_mod)
    importlib.reload(gc_mod)
    copilot = gc_mod.GeminiCopilot(client)

    # Merge incoming state
    merged_state = {**global_state, **incoming_state}

    # Execute direct Gemini Antigravity Copilot
    res = copilot.process_message(
        prompt, 
        merged_state, 
        image_b64=image_b64, 
        chat_history=history,
        images_b64=images_b64
    )
    if isinstance(res, tuple) and len(res) == 4:
        reply, new_state, html, telemetry = res
    else:
        reply, new_state, html = res
        telemetry = getattr(copilot, "last_telemetry", {})

    global_state = new_state
    if html:
        global_state["current_html"] = html

    return {
        "reply": reply or "Instrução concluída.",
        "state": global_state,
        "html": global_state.get("current_html", ""),
        "telemetry": telemetry
    }

@app.post("/api/export")
async def export_endpoint(payload: Dict[str, Any]):
    global global_state
    folder = payload.get("folder") or global_state.get("dest_folder")
    if not folder:
        folder = os.path.join(CURRENT_DIR, "exports")
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        folder = os.path.join(CURRENT_DIR, "exports")
        os.makedirs(folder, exist_ok=True)
    plan_key = global_state.get("plan_key", "Report")
    file_path = os.path.join(folder, f"SAT_Meeting_Report_{plan_key}.html")

    html = global_state.get("current_html")
    if not html:
        html = render_html_report(global_state)
        global_state["current_html"] = html

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    global_state["dest_folder"] = folder
    global_state["last_exported_path"] = file_path
    return {"status": "ok", "path": file_path}

@app.get("/api/current_report")
async def current_report():
    html = global_state.get("current_html")
    if not html:
        html = render_html_report(global_state)
        global_state["current_html"] = html
    return HTMLResponse(content=html)

@app.get("/api/download_report")
async def download_report():
    html = global_state.get("current_html")
    if not html:
        html = render_html_report(global_state)
        global_state["current_html"] = html
    plan_key = global_state.get("plan_key", "Report")
    filename = f"SAT_Meeting_Report_{plan_key}.html"
    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5050")

if __name__ == "__main__":
    print("[Server] A iniciar Siemens SAT Report Copilot em http://127.0.0.1:5050 ...")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=5050, log_level="info")
