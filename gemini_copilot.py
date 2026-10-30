import os
import sys
import json
import re
import time
import socket
import urllib.request
import urllib.error

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from jira_xray_client import JiraXrayClient
from report_builder import render_html_report, render_custom_report, clean_german_text

GEMINI_API_KEY = "AQ.Ab8RN6LTu2wrKrkivBXtU2OYfH_5IIK3XvcoDgAQe2eh2TG0Kg"
GEMINI_MODEL = "gemini-3-flash-preview"
FALLBACK_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest"
]

class GeminiCopilot:
    def __init__(self, client=None):
        self.client = client or JiraXrayClient()
        self.api_key = GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.fallback_models = FALLBACK_MODELS
        self.session_stats = {
            "requests": 0,
            "total_prompt_tokens": 0,
            "total_response_tokens": 0,
            "total_tokens": 0,
            "last_model": self.model,
            "last_latency_s": 0.0
        }

    def load_memory(self):
        mem_paths = [
            os.path.join(CURRENT_DIR, "copilot_memory.json"),
            os.path.join(os.path.dirname(CURRENT_DIR), "copilot_memory.json")
        ]
        for p in mem_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f), p
                except Exception:
                    pass
        default_mem = {
            "rules": [
                "Reports must ALWAYS be generated in English by default (Siemens SAT corporate standard), unless explicitly requested in another language.",
                "Chat with the user is in Portuguese (pt-PT), friendly, direct, expert and concise (Antigravity pair-programming style).",
                "Maintain official Siemens corporate styling (Petrol #009999, Ink #001b2e, Segoe UI typography, high-impact KPI cards).",
                "Act as a proactive Principal Test Architect: do not merely repeat Jira fields, deduce root-causes, cross-correlate subsystems, and suggest concrete mitigations."
            ],
            "preferences": {"report_language": "English", "chat_language": "Portuguese"},
            "interaction_notes": []
        }
        return default_mem, mem_paths[0]

    def save_memory(self, memory_data, file_path=None):
        target_path = file_path or os.path.join(CURRENT_DIR, "copilot_memory.json")
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[GeminiCopilot] Error saving memory: {e}")

    def process_message(self, user_prompt, current_state, image_b64=None, chat_history=None, images_b64=None):
        """
        True Gemini pair-programming experience with Continuous Persistent Memory:
        - Positioned as a Senior / Principal SAT Test Architect.
        - Actively supports dynamic report alterations via <EXECUTIVE_NOTE>, <CUSTOM_SECTION>, <UPDATE_RECOMMENDATION>, <HIDE_ELEMENT>, <SHOW_ELEMENT>.
        - Full multi-image vision support (multiple screenshots via Ctrl+V or upload).
        - Never resets report to static Jira template unless explicit Jira refresh/plan change is requested.
        - Preserves and accumulates custom engineering notes, sections, and element visibility states.
        """
        state = dict(current_state or {})
        history = list(chat_history or [])
        curr_plan = state.get("plan_key", "XPNB-1229")

        # Load persistent memory
        memory_data, mem_file_path = self.load_memory()
        rules_text = "\n".join([f"• {r}" for r in memory_data.get("rules", [])])
        notes_text = "\n".join([f"• {n}" for n in memory_data.get("interaction_notes", [])])

        # Precise Intent Detection: Only reload from Jira if explicitly switching plan or requesting fresh Jira fetch
        plan_switch_match = re.search(
            r'(?:mudar?|trocar?|carregar?|abrir?|ver|selecionar?|plano|test\s*plan)\s+(?:para\s+o\s+)?(?:plano\s+)?(XPECD-\d+|XPNB-\d+|ECD-\d+)\b',
            user_prompt,
            re.IGNORECASE
        )
        if not plan_switch_match and re.match(r'^\s*(XPECD-\d+|XPNB-\d+|ECD-\d+)\s*$', user_prompt, re.IGNORECASE):
            plan_switch_match = re.match(r'^\s*(XPECD-\d+|XPNB-\d+|ECD-\d+)\s*$', user_prompt, re.IGNORECASE)

        explicit_reload_keywords = [
            "recarregar jira", "recarrega o jira", "recarregar do jira", "restaurar do jira",
            "restaurar template original", "reset dados", "sincronizar jira", "sincroniza o jira",
            "obter dados frescos", "recarregar plano", "limpar alteracoes"
        ]
        user_wants_explicit_refresh = any(kw in user_prompt.lower() for kw in explicit_reload_keywords)

        custom_report_keywords = [
            "faz um report", "cria um report", "gera um report", "fazer um report", "criar um report", "gerar um report",
            "faz um relatorio", "cria um relatorio", "gera um relatorio", "fazer um relatorio", "criar um relatorio",
            "fazer relatorio", "criar relatorio", "gerar relatorio", "faz relatorio", "cria relatorio", "gera relatorio",
            "fazer outros reports", "outros reports", "outro report", "novo report", "novo relatorio", "novos relatorios",
            "conteudo que coloquei", "conteúdo que coloquei", "com o seguinte conteudo", "com o seguinte conteúdo",
            "com o conteudo", "com o conteúdo", "adapta o mesmo ao conteudo", "adapta o mesmo ao conteúdo",
            "adapta ao conteudo", "adapta ao conteúdo", "adaptar ao conteudo", "adaptar ao conteúdo",
            "relatorio sobre", "relatório sobre", "report sobre", "reuniao sobre", "reunião sobre"
        ]
        is_custom_report_request = any(kw in user_prompt.lower() for kw in custom_report_keywords)

        target_plan = None
        is_plan_reload = False

        if plan_switch_match:
            matched_key = plan_switch_match.group(1).upper()
            if matched_key != curr_plan:
                target_plan = matched_key

        if target_plan:
            print(f"[GeminiCopilot] A mudar e sincronizar Test Plan do Jira: {target_plan}")
            state["report_type"] = "jira"
            state.pop("custom_report", None)
            state = self._load_plan_data(target_plan, state)
            curr_plan = target_plan
            is_plan_reload = True
        elif user_wants_explicit_refresh:
            print(f"[GeminiCopilot] A forcar sincronizacao direta do Jira para o plano ativo: {curr_plan}")
            state["executive_notes"] = []
            state["custom_sections"] = []
            state.pop("custom_recommendation", None)
            state.pop("custom_report", None)
            state["report_type"] = "jira"
            state = self._load_plan_data(curr_plan, state)
            is_plan_reload = True
        elif is_custom_report_request:
            state["report_type"] = "custom"
        elif not state.get("executions") and state.get("report_type") != "custom":
            state = self._load_plan_data(curr_plan, state)
            is_plan_reload = True

        current_html = state.get("current_html") or render_html_report(state)
        state["current_html"] = current_html

        # Summary of Jira test executions & defects for context
        execs_summary = "\n".join([
            f"- {x.get('key')}: {x.get('summary')} | Status: {x.get('jira_status')} | Tests: {x.get('total')} | Pass: {x.get('passed')} | Fail: {x.get('failed')} | Skip: {x.get('skipped')} | Pass Rate: {x.get('pass_rate')}%"
            for x in state.get("executions", [])
        ])
        defects_summary = "\n".join([
            f"- {d.get('key')}: {d.get('summary')} | Priority: {d.get('priority')} | Status: {d.get('status')} | Comp: {d.get('component')}"
            for d in state.get("defects", [])
        ])

        # Active custom modifications summary
        active_notes = "\n".join([f"  * {n}" for n in state.get("executive_notes", [])])
        active_sections = "\n".join([f"  * {s.get('title')}" for s in state.get("custom_sections", [])])

        if state.get("report_type") == "custom" and state.get("custom_report"):
            cr = state["custom_report"]
            context_summary = f"""
Contexto Atual do Relatório Personalizado Ativo (Siemens SAT Standard):
- Título: {cr.get('title', 'Siemens Technical Report')}
- Subtítulo / Âmbito: {cr.get('subtitle', '')}
- Produto / Versão: {cr.get('product', '')} | {cr.get('version', '')}
- Referência / Código: {cr.get('reference_code', '')}
- Estado Geral: {cr.get('status', 'Verified')}
- KPIs Ativos: {len(cr.get('kpis', []))} cartões de métrica
- Secções Ativas: {len(cr.get('sections', []))} secções técnicas
- Recomendação Final: {cr.get('recommendation', {}).get('status', 'N/A')}
"""
        else:
            context_summary = f"""
Contexto Atual do Projeto Jira:
- Test Plan Ativo: {curr_plan} ({state.get('plan_summary', '')})
- Suítes de Test Execution no Jira ({len(state.get('executions', []))} suítes):
{execs_summary or 'Nenhuma'}
- Defeitos Vinculados no Jira ({len(state.get('defects', []))} defeitos):
{defects_summary or 'Nenhum'}
- Notas Executivas Ativas no Relatório:
{active_notes or '  Nenhuma no momento'}
- Secções Customizadas Ativas no Relatório:
{active_sections or '  Nenhuma no momento'}
"""

        system_instruction = f"""Tu és o Gemini, o Principal System & Application Test (SAT) Architect & Technical Lead da Siemens eMobility, a colaborar diretamente com o engenheiro/utilizador no Google Antigravity.

[MEMÓRIA PERSISTENTE E PREMISSAS FUNDAMENTAIS OBRIGATÓRIAS]:
{rules_text}
{notes_text}

PREMISSAS FUNDAMENTAIS INEGOCIÁVEIS:
1. POSTURA DE ENGENHEIRO ARQUITETO SÉNIOR (NÃO APENAS REPETIDOR DO JIRA):
   - Não te limites a ler passivamente o que está escrito no Jira. Tu és um especialista em engenharia de sistemas de carregamento de alta potência (DC Fast Charging).
   - Deduz correlações técnicas profundas: por exemplo, como os tempos de atraso no barramento CAN ou timeouts de watchdog se relacionam com falhas de Safe State (XPNB-1828) e desincronização de contactores (SIF-1086 / SIF-1761); como limites de dissipação térmica afetam a curva de potência DC; ou impactos de transições de versão de firmware (v1.0.12 vs v1.0.14).
   - Sê dinâmico, perspicaz e proativo. Se o utilizador pedir para analisar um problema, propõe causas raiz, testes de regressão adicionais e impacto operacional no terreno.

2. ATUALIZAÇÕES DINÂMICAS AO RELATÓRIO NO LIVE PREVIEW:
   O relatório exibido à esquerda é gerado dinamicamente. Sempre que o utilizador pedir alterações, análises, notas, ou sempre que uma discussão técnica justificar uma atualização visível no relatório, deves utilizar as seguintes tags especiais (em Inglês Técnico):

   A) Adicionar/Atualizar NOTA EXECUTIVA (aparece em destaque abaixo dos cartões de métricas):
      <EXECUTIVE_NOTE>
      Engineering Quality Advisory: Immediate firmware patch required for contactor feedback loop prior to volume field rollout.
      </EXECUTIVE_NOTE>

   B) Adicionar/Atualizar SECÇÃO TÉCNICA PERSONALIZADA (aparece como nova secção antes da Recomendação de Release):
      <CUSTOM_SECTION title="6. Deep Dive: Contactor Timing & Safe State Loop Analysis">
      <p>Technical correlation between Safe State execution failures and dynamic power allocation:</p>
      <ul>
        <li><strong>Identified Anomaly:</strong> Under 300A load steps, auxiliary feedback lag exceeds 45ms.</li>
        <li><strong>Root Cause Hypothesis:</strong> Task priority inversion on the micro-controller loop.</li>
        <li><strong>Engineering Mitigation:</strong> Adjust CAN watchdog threshold to 75ms in patch v1.0.14-p2.</li>
      </ul>
      </CUSTOM_SECTION>

   C) Atualizar RECOMENDAÇÃO DE RELEASE (Secção 5):
      <UPDATE_RECOMMENDATION status="CONDITIONAL GO" title="Conditional Release Approved with Field Safeguards">
      SAT recommends conditional field deployment for test fleets under controlled supervision, contingent on deploying the contactor watchdog patch and completing regression suite XPNB-1828.
      </UPDATE_RECOMMENDATION>
      [Valores típicos para status: "GO • APPROVED", "CONDITIONAL GO", "NO-GO • BLOCKED", "TRIAGE • IN PROGRESS"]

   D) OCULTAR OU EXIBIR ELEMENTOS DO RELATÓRIO:
      Se o utilizador pedir para apagar, remover, ou anexar um print indicando algo para retirar (ex: "apaga o banner", "remove isto", "tira o resumo", "remove os KPIs"):
      - Para ocultar o Banner de Resumo Inicial / Hero Summary Box: <HIDE_ELEMENT>summary_box</HIDE_ELEMENT>
      - Para ocultar os Cartões de KPI: <HIDE_ELEMENT>kpi_cards</HIDE_ELEMENT>
      - Para ocultar a Secção 2 (Demonstração / Vídeo): <HIDE_ELEMENT>section_2</HIDE_ELEMENT>
      - Para ocultar a Secção 3 (Âmbito Validado): <HIDE_ELEMENT>section_3</HIDE_ELEMENT>
      - Para voltar a mostrar um elemento ocultado: <SHOW_ELEMENT>summary_box</SHOW_ELEMENT>
      - Para injetar estilos CSS específicos: <INJECT_CSS>.summary-box {{ display: none !important; }}</INJECT_CSS>

   E) EDIÇÃO PONTUAL DE QUALQUER PARTE DO HTML (TARGETED PATCH):
      Para modificar qualquer texto, título, cor, linha de tabela, número ou classe no relatório:
      <HTML_EDIT>
      <<<< SEARCH
      texto ou HTML exato atualmente no relatório
      ====
      novo texto ou HTML de substituição (ou vazio para apagar)
      >>>>
      </HTML_EDIT>

   F) Modificação completa do relatório (se estritamente necessário):
      <REPORT_HTML>
      ... código HTML completo em Inglês ...
      </REPORT_HTML>

3. CUMPRIMENTO ESTRITO DE TODAS AS INSTRUÇÕES DO UTILIZADOR:
   - NUNCA te limites a responder em texto no chat dizendo "fiz a alteração" ou "removi o bloco".
   - Tens SEMPRE de emitir a respetiva tag (<HTML_EDIT>, <HIDE_ELEMENT>, <INJECT_CSS>, <EXECUTIVE_NOTE>, etc.) para que a modificação seja fisicamente aplicada ao Live Preview!
   - Toda a tua resposta no chat DEVE SER SEMPRE em Português (pt-PT), concisa, elegante, técnica e limpa.
   - NUNCA despejes tags HTML ou blocos ```html soltos na resposta do chat! Todas as alterações devem estar dentro das tags estruturadas acima.

4. RELATÓRIOS 100% EM INGLÊS TÉCNICO (ZERO TERMOS EM ALEMÃO):
   - Todo o conteúdo inserido nas tags do relatório (<EXECUTIVE_NOTE>, <CUSTOM_SECTION>, etc.) deve estar em Inglês técnico corporativo da Siemens.

5. FLEXIBILIDADE TOTAL (NÃO SER OBTUSO NEM PRESO APENAS AO JIRA):
   - A tool NUNCA deve ser obtusa e forçar sempre os mesmos dados de Test Plan Jira (XPNB-1229) quando o utilizador pede outros relatórios!
   - Se o utilizador pedir para fazer um relatório com o conteúdo que colocou no prompt (ex: atas de reunião, ensaios de campo, testes de interoperabilidade, homologação de camiões elétricos, auditorias de segurança, validação de inversores, benchmarks, etc.), DEVES ADAPTAR O RELATÓRIO IMEDIATAMENTE A ESSE CONTEÚDO!
   - O template corporativo oficial da Siemens (Petrol #009999, Ink #001b2e, tipografia Segoe UI, cabeçalho com curva, cartões KPI, hero summary box, tabelas limpas, callouts de engenharia e recomendação final) MANTÉM-SE SEMPRE ATIVO E IMUTÁVEL.
   - Para gerar ou atualizar o relatório adaptado ao conteúdo do utilizador, emite a tag estruturada:
     <CUSTOM_REPORT_JSON>
     {{
       "title": "Technical Report Title in English",
       "subtitle": "Comprehensive technical assessment and operational scope",
       "eyebrow": "System & Application Test (SAT) · Engineering Assessment",
       "product": "Siemens eMobility / Sicharge UC",
       "version": "FW v1.0.14-rc2",
       "reference_code": "SAT-CUSTOM-REPORT",
       "status": "Verified & Documented",
       "kpis": [
         {{"title": "Metric 1", "value": "100%", "sub": "Description of metric", "color": "var(--pass)"}},
         {{"title": "Metric 2", "value": "42", "sub": "Total cycles / items", "color": "var(--siemens-petrol)"}}
       ],
       "summary_box": {{
         "status": "GO • APPROVED" ou "CONDITIONAL GO" ou "NO-GO",
         "title": "Executive Summary Headline",
         "desc": "Key findings, context, and operational outcome...",
         "stats": [
           {{"num": "42", "lbl": "Total Sessions", "class": ""}},
           {{"num": "38", "lbl": "Pass", "class": "pass"}},
           {{"num": "4", "lbl": "Fail", "class": "fail"}}
         ]
       }},
       "executive_notes": [
         "Engineering quality advisory note 1...",
         "Engineering quality advisory note 2..."
       ],
       "sections": [
         {{
           "title": "1. Field Trial Context & Setup",
           "desc": "Infrastructure, charging dispensers and grid parameters",
           "content_html": "<p>Description with clean HTML, tables or lists...</p>"
         }},
         {{
           "title": "2. Session Telemetry & Operational Results",
           "desc": "Detailed breakdown by vehicle brand and power levels",
           "content_html": "<table><thead><tr><th>Brand</th><th>Sessions</th><th>Result</th><th>Notes</th></tr></thead><tbody><tr><td><strong>Mercedes eActros</strong></td><td>24</td><td><span class=\"result result--pass\">PASS</span></td><td>All sessions completed nominal</td></tr></tbody></table>"
         }}
       ],
       "recommendation": {{
         "status": "CONDITIONAL GO",
         "title": "Operational Recommendation Title",
         "desc": "Detailed conclusion and sign-off remarks..."
       }}
     }}
     </CUSTOM_REPORT_JSON>
   - Em alternativa, se preferires controlo total de HTML, podes emitir <REPORT_HTML>...</REPORT_HTML>.

{context_summary}
"""

        if is_plan_reload and (plan_switch_match or user_wants_explicit_refresh):
            system_instruction += f"""
[ESTADO DE CARREGAMENTO DO JIRA]:
O utilizador solicitou carregar/mudar o Test Plan para {curr_plan} ({state.get('plan_summary', '')}).
Confirma a sincronização em Português e sintetiza os principais destaques técnicos.
"""

        contents = []

        # Add recent conversation turns
        for h in history[-6:]:
            role = "user" if h.get("role") == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": h.get("text", "")}]
            })

        # Add current user prompt
        active_hidden_str = ", ".join(state.get("hidden_elements", [])) or "Nenhum"
        if state.get("report_type") == "custom" and state.get("custom_report"):
            cr = state["custom_report"]
            layout_overview = f"""
[ESTRUTURA VISUAL DO RELATÓRIO ATUAL NO LIVE PREVIEW - RELATÓRIO PERSONALIZADO SIEMENS]:
- Cabeçalho: <div class="header"> com título <h1>{cr.get('title', '')}</h1>
- Subtítulo: {cr.get('subtitle', '')}
- Produto / FW: {cr.get('product', '')} | {cr.get('version', '')}
- Cartões KPI: {len(cr.get('kpis', []))} cartões de métricas
- Banner Resumo: {cr.get('summary_box', {}).get('status', '')} - {cr.get('summary_box', {}).get('title', '')}
- Secções Customizadas: {len(cr.get('sections', []))} secções ativas
- Recomendação Final: {cr.get('recommendation', {}).get('status', '')}
- Elementos Ocultados no momento: [{active_hidden_str}]
"""
        else:
            layout_overview = f"""
[ESTRUTURA VISUAL DO RELATÓRIO ATUAL NO LIVE PREVIEW]:
- Cabeçalho: <div class="header"> com título <h1>{state.get('plan_summary', '')}</h1>
- 4 Cartões KPI: <div class="kpi-grid"> (Total Tests, Overall Pass Rate, Open Defects, Critical Focus Areas)
- Banner Resumo Inicial: <div class="summary-box"> com classe .summary-state e pills de estatísticas
- Secção 1: <div class="section-title">1. Execution Suites Breakdown</div>
- Secção 2: <div class="section-title">2. Featured Demonstration: DC Charging Curve</div>
- Secção 3: <div class="section-title">3. Verified Validation Scope & Strengths</div>
- Secção 4: <div class="section-title">4. Defect & Residual Risk Analysis</div> com barra de filtro e tabela
- Secção 5: <div class="section-title">5. SAT Release Recommendation</div>
- Elementos Ocultados no momento: [{active_hidden_str}]
"""
        prompt_context = f"{system_instruction}\n{layout_overview}\n[MENSAGEM DO ENGENHEIRO UTILIZADOR]\n{user_prompt}"

        current_parts = [{"text": prompt_context}]
        all_imgs = list(images_b64 or [])
        if image_b64 and image_b64 not in all_imgs:
            all_imgs.insert(0, image_b64)

        for img in all_imgs:
            current_parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": img
                }
            })

        contents.append({
            "role": "user",
            "parts": current_parts
        })

        payload = {"contents": contents}
        req_data = json.dumps(payload).encode('utf-8')

        raw_text = None
        last_error_detail = ""

        # Model candidate order starting with self.model then alternatives
        candidates = [self.model] + [m for m in self.fallback_models if m != self.model]

        telemetry = {
            "model": self.model,
            "latency_s": 0.0,
            "prompt_tokens": 0,
            "candidates_tokens": 0,
            "total_tokens": 0,
            "service_tier": "standard",
            "timestamp": time.strftime("%H:%M:%S")
        }

        for model_name in candidates:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            
            # Retry loop for temporary issues (503 High Demand, 429, timeouts)
            for attempt in range(2):
                try:
                    t0 = time.time()
                    req = urllib.request.Request(
                        url,
                        data=req_data,
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        data = json.loads(resp.read().decode('utf-8'))
                    latency = round(time.time() - t0, 2)
                    raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if raw_text:
                        print(f"[GeminiCopilot] Sucesso na resposta atraves do modelo: {model_name} ({latency}s)")
                        self.model = model_name  # Keep active working model as primary
                        usage = data.get("usageMetadata", {})
                        telemetry = {
                            "model": model_name,
                            "latency_s": latency,
                            "prompt_tokens": usage.get("promptTokenCount", 0),
                            "candidates_tokens": usage.get("candidatesTokenCount", 0),
                            "total_tokens": usage.get("totalTokenCount", 0),
                            "service_tier": usage.get("serviceTier", "standard"),
                            "timestamp": time.strftime("%H:%M:%S")
                        }
                        self.session_stats["requests"] = self.session_stats.get("requests", 0) + 1
                        self.session_stats["total_prompt_tokens"] = self.session_stats.get("total_prompt_tokens", 0) + usage.get("promptTokenCount", 0)
                        self.session_stats["total_response_tokens"] = self.session_stats.get("total_response_tokens", 0) + usage.get("candidatesTokenCount", 0)
                        self.session_stats["total_tokens"] = self.session_stats.get("total_tokens", 0) + usage.get("totalTokenCount", 0)
                        self.session_stats["last_model"] = model_name
                        self.session_stats["last_latency_s"] = latency
                        break
                except urllib.error.HTTPError as e:
                    err_body = e.read().decode('utf-8', errors='ignore')
                    last_error_detail = f"HTTP {e.code}"
                    print(f"[GeminiCopilot] {model_name} tentativa {attempt+1} HTTP {e.code}: {err_body[:100]}")
                    if e.code == 404:
                        break  # Model deprecated, skip to next model
                    elif e.code in (429, 500, 502, 503, 504):
                        time.sleep(1.0 * (attempt + 1))
                        continue
                    else:
                        break
                except (socket.timeout, urllib.error.URLError, TimeoutError) as e:
                    last_error_detail = f"Timeout ({e})"
                    print(f"[GeminiCopilot] {model_name} tentativa {attempt+1} Timeout: {e}")
                    time.sleep(1.0)
                    continue
                except Exception as e:
                    last_error_detail = str(e)
                    print(f"[GeminiCopilot] {model_name} tentativa {attempt+1} erro: {e}")
                    break

            if raw_text:
                break

        if not raw_text:
            raw_text = (
                "Desculpe, os servidores da Google estão com uma procura anormalmente alta neste instante "
                "(503 / Timeout). Já tentei modelos alternativos automaticamente sem sucesso. "
                "Por favor, repita o seu pedido dentro de alguns segundos."
            )

        # Extract <LEARNED_RULE>...</LEARNED_RULE> if Gemini extracted a new rule
        learned_matches = re.findall(r'<LEARNED_RULE>(.*?)</LEARNED_RULE>', raw_text, re.DOTALL | re.IGNORECASE)
        if learned_matches:
            for new_rule in learned_matches:
                new_rule_clean = new_rule.strip()
                if new_rule_clean and new_rule_clean not in memory_data.get("rules", []):
                    memory_data.setdefault("rules", []).append(new_rule_clean)
                    print(f"[GeminiCopilot] Auto-learned new rule: {new_rule_clean}")
            self.save_memory(memory_data, mem_file_path)
            raw_text = re.sub(r'<LEARNED_RULE>.*?</LEARNED_RULE>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        has_state_modification = False

        # Extract <EXECUTIVE_NOTE>...</EXECUTIVE_NOTE>
        note_matches = re.findall(r'<EXECUTIVE_NOTE>(.*?)</EXECUTIVE_NOTE>', raw_text, re.DOTALL | re.IGNORECASE)
        if note_matches:
            state.setdefault("executive_notes", [])
            for n in note_matches:
                n_clean = clean_german_text(n.strip())
                if n_clean and n_clean not in state["executive_notes"]:
                    state["executive_notes"].append(n_clean)
            has_state_modification = True
            raw_text = re.sub(r'<EXECUTIVE_NOTE>.*?</EXECUTIVE_NOTE>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # Extract <CUSTOM_SECTION title="...">...</CUSTOM_SECTION>
        sec_matches = re.findall(r'<CUSTOM_SECTION(?:\s+title=["\'](.*?)["\'])?>(.*?)</CUSTOM_SECTION>', raw_text, re.DOTALL | re.IGNORECASE)
        if sec_matches:
            state.setdefault("custom_sections", [])
            for tit, content in sec_matches:
                tit_clean = clean_german_text((tit or "Engineering Deep Dive").strip())
                cont_clean = clean_german_text(content.strip())
                # Replace if already exists with same title or append
                matched_sec = None
                for s in state["custom_sections"]:
                    if s.get("title") == tit_clean:
                        matched_sec = s
                        break
                if matched_sec:
                    matched_sec["content"] = cont_clean
                else:
                    state["custom_sections"].append({"title": tit_clean, "content": cont_clean})
            has_state_modification = True
            raw_text = re.sub(r'<CUSTOM_SECTION.*?</CUSTOM_SECTION>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # Extract <UPDATE_RECOMMENDATION status="..." title="...">...</UPDATE_RECOMMENDATION>
        recom_match = re.search(r'<UPDATE_RECOMMENDATION(?:\s+status=["\'](.*?)["\'])?(?:\s+title=["\'](.*?)["\'])?>(.*?)</UPDATE_RECOMMENDATION>', raw_text, re.DOTALL | re.IGNORECASE)
        if recom_match:
            st_val = recom_match.group(1) or "CONDITIONAL GO"
            tit_val = recom_match.group(2) or "Release Recommendation Updated"
            desc_val = clean_german_text(recom_match.group(3).strip())
            state["custom_recommendation"] = {
                "status": st_val.strip(),
                "title": tit_val.strip(),
                "desc": desc_val
            }
            has_state_modification = True
            raw_text = re.sub(r'<UPDATE_RECOMMENDATION.*?</UPDATE_RECOMMENDATION>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # Extract <HIDE_ELEMENT>...</HIDE_ELEMENT> and <REMOVE_ELEMENT>...</REMOVE_ELEMENT>
        hide_matches = re.findall(r'<(?:HIDE_ELEMENT|REMOVE_ELEMENT)>(.*?)</(?:HIDE_ELEMENT|REMOVE_ELEMENT)>', raw_text, re.DOTALL | re.IGNORECASE)
        for h in hide_matches:
            elem = h.strip().lower()
            state.setdefault("hidden_elements", [])
            if elem not in state["hidden_elements"]:
                state["hidden_elements"].append(elem)
            has_state_modification = True
        raw_text = re.sub(r'<(?:HIDE_ELEMENT|REMOVE_ELEMENT)>.*?</(?:HIDE_ELEMENT|REMOVE_ELEMENT)>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # Extract <SHOW_ELEMENT>...</SHOW_ELEMENT>
        show_matches = re.findall(r'<SHOW_ELEMENT>(.*?)</SHOW_ELEMENT>', raw_text, re.DOTALL | re.IGNORECASE)
        for s in show_matches:
            elem = s.strip().lower()
            if "hidden_elements" in state and elem in state["hidden_elements"]:
                state["hidden_elements"].remove(elem)
                has_state_modification = True
        raw_text = re.sub(r'<SHOW_ELEMENT>.*?</SHOW_ELEMENT>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # Extract <INJECT_CSS>...</INJECT_CSS>
        css_matches = re.findall(r'<INJECT_CSS>(.*?)</INJECT_CSS>', raw_text, re.DOTALL | re.IGNORECASE)
        for css in css_matches:
            state["injected_css"] = (state.get("injected_css", "") + "\n" + css.strip()).strip()
            has_state_modification = True
        raw_text = re.sub(r'<INJECT_CSS>.*?</INJECT_CSS>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # Smart Fallback: Banner / Summary box removal intent
        user_wants_remove_banner = bool(re.search(r'(?:apag(?:a|ar)|remov(?:e|er)|tir(?:a|ar)|elimin(?:a|ar)|escond(?:e|er))\s+.*?(?:banner|resumo|sumario|hero)', user_prompt, re.I))
        user_said_apaga_isto = bool(re.search(r'\b(?:apag(?:a|ar)|remov(?:e|er)|tir(?:a|ar)|elimin(?:a|ar))\s+isto\b', user_prompt, re.I))
        gemini_said_removed_banner = bool(re.search(r'(?:remov[ei]|elimin[ei]|ocultei|retirei)\s+.*?(?:banner|resumo)', raw_text, re.I))

        if user_wants_remove_banner or (user_said_apaga_isto and gemini_said_removed_banner) or gemini_said_removed_banner:
            state.setdefault("hidden_elements", [])
            if "summary_box" not in state["hidden_elements"]:
                state["hidden_elements"].append("summary_box")
                has_state_modification = True

        if "kpi" in user_prompt.lower() and any(w in user_prompt.lower() for w in ["apag", "remov", "tir", "elimin", "escond"]):
            state.setdefault("hidden_elements", [])
            if "kpi_cards" not in state["hidden_elements"]:
                state["hidden_elements"].append("kpi_cards")
                has_state_modification = True

        user_wants_restore_banner = bool(re.search(r'(?:mostr(?:a|ar)|restaur(?:a|ar)|recuper(?:a|ar)|volt(?:a|ar)\s+a\s+mostr(?:a|ar))\s+.*?(?:banner|resumo|sumario|hero)', user_prompt, re.I))
        if user_wants_restore_banner and "hidden_elements" in state:
            state["hidden_elements"] = [x for x in state["hidden_elements"] if x not in ["summary_box", "banner", "hero", "hero_banner", "resumo"]]
            has_state_modification = True

        # Extract <CUSTOM_REPORT_JSON>...</CUSTOM_REPORT_JSON>
        custom_json_match = re.search(r'<CUSTOM_REPORT_JSON>(.*?)</CUSTOM_REPORT_JSON>', raw_text, re.DOTALL | re.IGNORECASE)
        if custom_json_match:
            try:
                custom_json_str = custom_json_match.group(1).strip()
                custom_json_str = re.sub(r'^```(?:json)?\s*', '', custom_json_str, flags=re.IGNORECASE)
                custom_json_str = re.sub(r'\s*```$', '', custom_json_str)
                custom_data = json.loads(custom_json_str)
                state["custom_report"] = custom_data
                state["report_type"] = "custom"
                state["current_html"] = render_custom_report(custom_data, state)
                has_state_modification = True
                print("[GeminiCopilot] Successfully generated Siemens custom report from JSON!")
            except Exception as e:
                print(f"[GeminiCopilot] Error parsing CUSTOM_REPORT_JSON: {e}")
            raw_text = re.sub(r'<CUSTOM_REPORT_JSON>.*?</CUSTOM_REPORT_JSON>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        # Base HTML to operate on
        if has_state_modification or is_plan_reload or not state.get("current_html"):
            if state.get("report_type") == "custom" and state.get("custom_report"):
                working_html = render_custom_report(state["custom_report"], state)
            else:
                working_html = render_html_report(state)
        else:
            working_html = state.get("current_html")

        # Extract <HTML_EDIT> and <REMOVE_HTML> patches
        patch_applied_count = 0
        html_edits = re.findall(r'<HTML_EDIT>\s*<<<<\s*SEARCH\s*\n?(.*?)\n?\s*====\s*\n?(.*?)\s*>>>>\s*</HTML_EDIT>', raw_text, re.DOTALL)
        for search_block, replace_block in html_edits:
            s_clean = search_block.strip()
            r_clean = replace_block.strip()
            if s_clean and s_clean in working_html:
                working_html = working_html.replace(s_clean, r_clean, 1)
                patch_applied_count += 1
            elif s_clean:
                pattern = re.escape(s_clean)
                pattern = re.sub(r'\\\s+', r'\\s+', pattern)
                m = re.search(pattern, working_html, re.DOTALL)
                if m:
                    working_html = working_html[:m.start()] + r_clean + working_html[m.end():]
                    patch_applied_count += 1
        raw_text = re.sub(r'<HTML_EDIT>.*?</HTML_EDIT>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        removes = re.findall(r'<REMOVE_HTML>(.*?)</REMOVE_HTML>', raw_text, re.DOTALL | re.IGNORECASE)
        for rem in removes:
            r_str = rem.strip()
            if r_str and r_str in working_html:
                working_html = working_html.replace(r_str, "")
                patch_applied_count += 1
            elif r_str:
                pattern = re.escape(r_str)
                pattern = re.sub(r'\\\s+', r'\\s+', pattern)
                m = re.search(pattern, working_html, re.DOTALL)
                if m:
                    working_html = working_html[:m.start()] + working_html[m.end():]
                    patch_applied_count += 1
        raw_text = re.sub(r'<REMOVE_HTML>.*?</REMOVE_HTML>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        if patch_applied_count > 0:
            state["current_html"] = working_html
            has_state_modification = True
            print(f"[GeminiCopilot] Successfully applied {patch_applied_count} targeted HTML patches!")
        elif has_state_modification:
            state["current_html"] = working_html

        # Extract <REPORT_HTML>...</REPORT_HTML>
        updated_html = None
        html_match = re.search(r'<REPORT_HTML>(.*?)</REPORT_HTML>', raw_text, re.DOTALL | re.IGNORECASE)
        if html_match:
            updated_html = html_match.group(1).strip()
            raw_text = re.sub(r'<REPORT_HTML>.*?</REPORT_HTML>', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
        else:
            doctype_match = re.search(r'```(?:html)?\s*(<!DOCTYPE html.*?)```', raw_text, re.DOTALL | re.IGNORECASE)
            if doctype_match:
                updated_html = doctype_match.group(1).strip()
                raw_text = re.sub(r'```(?:html)?\s*<!DOCTYPE html.*?```', '', raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

        if updated_html:
            is_valid_html = ("<!DOCTYPE html" in updated_html or "<html" in updated_html or 'class="card"' in updated_html) and len(updated_html) > 300
            if is_valid_html:
                state["current_html"] = clean_german_text(updated_html)
                state["report_type"] = "custom"
                has_state_modification = True
                print(f"[GeminiCopilot] Successfully applied full updated HTML ({len(updated_html)} chars)!")

        clean_reply = raw_text
        # Strict Premise 1: Clean all residual HTML code blocks and internal tags from chat side
        clean_reply = re.sub(r'<(?:HTML_EDIT|REMOVE_HTML|INJECT_CSS|HIDE_ELEMENT|SHOW_ELEMENT|EXECUTIVE_NOTE|CUSTOM_SECTION|UPDATE_RECOMMENDATION|CUSTOM_REPORT_JSON|REPORT_HTML)>.*?</(?:HTML_EDIT|REMOVE_HTML|INJECT_CSS|HIDE_ELEMENT|SHOW_ELEMENT|EXECUTIVE_NOTE|CUSTOM_SECTION|UPDATE_RECOMMENDATION|CUSTOM_REPORT_JSON|REPORT_HTML)>', '', clean_reply, flags=re.DOTALL | re.IGNORECASE).strip()
        clean_reply = re.sub(r'```(?:json)?\s*\{.*?\}\s*```', '', clean_reply, flags=re.DOTALL | re.IGNORECASE).strip()
        clean_reply = re.sub(r'```(?:html)?\s*<!DOCTYPE html.*?</html>\s*```', '', clean_reply, flags=re.DOTALL | re.IGNORECASE).strip()
        clean_reply = re.sub(r'<!DOCTYPE html.*?</html>', '', clean_reply, flags=re.DOTALL | re.IGNORECASE).strip()
        clean_reply = re.sub(r'```(?:html)?\s*<div class="card".*?</div>\s*```', '', clean_reply, flags=re.DOTALL | re.IGNORECASE).strip()
        clean_reply = re.sub(r'```(?:html)?\s*<style.*?</style>\s*```', '', clean_reply, flags=re.DOTALL | re.IGNORECASE).strip()

        if not clean_reply:
            clean_reply = "As alterações solicitadas foram cumpridas e aplicadas diretamente no Live Preview."

        if not state.get("current_html"):
            state["current_html"] = render_html_report(state)

        self.last_telemetry = telemetry
        return clean_reply, state, state.get("current_html"), telemetry

    def _load_plan_data(self, key, state):
        issue_info = self.client.get_issue_info(key)
        state["plan_key"] = key
        state["plan_summary"] = issue_info.get("summary", f"Test Plan {key}") if issue_info else f"Test Plan {key}"
        state["project_key"] = issue_info.get("project", key.split('-')[0]) if issue_info else key.split('-')[0]
        execs = self.client.get_test_executions(key)
        metrics = self.client.get_execution_metrics(execs)
        state["executions"] = metrics
        defects = self.client.get_plan_linked_defects(key, execs)
        state["defects"] = defects
        state["current_html"] = render_html_report(state)
        return state
