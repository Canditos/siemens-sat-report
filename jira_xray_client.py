import json
import base64
import urllib.request
try:
    from .config_helper import get_jira_credentials, get_xray_credentials
except ImportError:
    from config_helper import get_jira_credentials, get_xray_credentials

class JiraXrayClient:
    def __init__(self):
        self.jira_base_url, self.jira_email, self.jira_token = get_jira_credentials()
        self.xray_cid, self.xray_csec = get_xray_credentials()
        self.jwt = None
        self._auth_header = None
        if self.jira_email and self.jira_token:
            auth_str = f"{self.jira_email}:{self.jira_token}"
            self._auth_header = "Basic " + base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

    def get_jwt(self, force_refresh=False):
        if self.jwt and not force_refresh:
            return self.jwt
        if not self.xray_cid or not self.xray_csec:
            return None
        auth_url = "https://xray.cloud.getxray.app/api/v2/authenticate"
        payload = json.dumps({"client_id": self.xray_cid, "client_secret": self.xray_csec}).encode('utf-8')
        req = urllib.request.Request(auth_url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                self.jwt = resp.read().decode('utf-8').strip('"')
                return self.jwt
        except Exception as e:
            print(f"Xray JWT auth failed: {e}")
            return None

    def jira_get(self, endpoint):
        url = f"{self.jira_base_url}/rest/api/3/{endpoint.lstrip('/')}"
        req = urllib.request.Request(url, headers={
            "Authorization": self._auth_header,
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def jira_post(self, endpoint, payload):
        url = f"{self.jira_base_url}/rest/api/3/{endpoint.lstrip('/')}"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Authorization": self._auth_header,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def xray_graphql(self, query):
        jwt = self.get_jwt()
        if not jwt:
            return None
        url = "https://xray.cloud.getxray.app/api/v2/graphql"
        req = urllib.request.Request(
            url,
            data=json.dumps({"query": query}).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {jwt}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def get_issue_info(self, issue_key):
        """Fetch general issue info and detect its issuetype."""
        try:
            issue = self.jira_get(f"issue/{issue_key}")
            fields = issue.get("fields", {})
            itype = fields.get("issuetype", {}).get("name", "")
            return {
                "key": issue.get("key"),
                "id": issue.get("id"),
                "type": itype,
                "summary": fields.get("summary", ""),
                "description": fields.get("description"),
                "status": fields.get("status", {}).get("name", ""),
                "project": fields.get("project", {}).get("key", ""),
                "project_name": fields.get("project", {}).get("name", ""),
                "versions": [v.get("name") for v in fields.get("versions", [])],
                "fix_versions": [v.get("name") for v in fields.get("fixVersions", [])],
                "issuelinks": fields.get("issuelinks", [])
            }
        except Exception as e:
            print(f"Error getting issue {issue_key}: {e}")
            return None

    def get_test_plan_details(self, plan_key):
        return self.get_issue_info(plan_key)

    def get_test_executions(self, plan_key):
        """Find all Test Executions linked to a Test Plan via JQL."""
        jql = f"issue in testPlanTestExecutions('{plan_key}') ORDER BY created DESC"
        try:
            res = self.jira_post("search/jql", {
                "jql": jql,
                "maxResults": 100,
                "fields": ["summary", "status", "created", "assignee", "fixVersions", "versions", "issuelinks"]
            })
            return res.get("issues", [])
        except Exception as e:
            print(f"Error fetching test executions for {plan_key}: {e}")
            return []

    def get_single_execution_data(self, execution_key):
        """Handles a single Test Execution (like XPNB-1794)."""
        iss = self.get_issue_info(execution_key)
        if not iss:
            return None

        iss_id = iss["id"]
        summary = iss["summary"]
        status = iss["status"]
        fix_v = iss["fix_versions"][0] if iss["fix_versions"] else "Unspecified"

        q = f"""
        {{
            getTestExecution(issueId: "{iss_id}") {{
                issueId
                testPlans(limit: 5) {{
                    total
                    results {{
                        jira(fields: ["key", "summary"])
                    }}
                }}
                testRuns(limit: 100) {{
                    total
                    results {{
                        status {{
                            name
                        }}
                        test {{
                            jira(fields: ["key", "summary"])
                        }}
                    }}
                }}
            }}
        }}
        """
        parent_plans = []
        counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "TO DO": 0, "EXECUTING": 0, "OTHER": 0}
        total_runs = 0

        data = self.xray_graphql(q)
        if data:
            te_data = data.get("data", {}).get("getTestExecution", {}) or {}
            plans_res = te_data.get("testPlans", {}).get("results", [])
            for p in plans_res:
                pj = p.get("jira", {})
                if pj:
                    parent_plans.append(pj)

            runs_res = te_data.get("testRuns", {}).get("results", [])
            total_runs = te_data.get("testRuns", {}).get("total", len(runs_res))
            for r in runs_res:
                st_name = r.get("status", {}).get("name", "OTHER").upper()
                if st_name == "PASS": st_name = "PASSED"
                if st_name == "FAIL": st_name = "FAILED"
                if st_name == "TODO": st_name = "TO DO"
                counts[st_name if st_name in counts else "OTHER"] += 1

        p = counts["PASSED"]
        f = counts["FAILED"]
        s = counts["SKIPPED"]
        td = counts["TO DO"]
        ex = counts["EXECUTING"]
        oth = counts["OTHER"]
        executed = p + f
        rate = round(p / executed * 100, 1) if executed > 0 else 0.0

        execution_entry = {
            "key": execution_key,
            "id": iss_id,
            "summary": summary,
            "jira_status": status,
            "target_version": fix_v,
            "total": total_runs,
            "passed": p,
            "failed": f,
            "skipped": s,
            "todo": td,
            "executing": ex,
            "other": oth,
            "pass_rate": rate
        }

        # Extract linked defects from issuelinks
        linked_defects = []
        for link in iss.get("issuelinks", []):
            for direction in ["inwardIssue", "outwardIssue"]:
                target = link.get(direction)
                if target:
                    itype = target.get("fields", {}).get("issuetype", {}).get("name", "")
                    tkey = target.get("key", "")
                    if itype.lower() in ["defect", "bug"] or tkey.startswith(("SIF-", "ECD-")):
                        tf = target.get("fields", {})
                        linked_defects.append({
                            "key": tkey,
                            "summary": tf.get("summary", ""),
                            "priority": tf.get("priority", {}).get("name", "Medium"),
                            "status": tf.get("status", {}).get("name", "Open"),
                            "assignee": tf.get("assignee", {}).get("displayName", "Unassigned") if tf.get("assignee") else "Unassigned",
                            "reporter": tf.get("reporter", {}).get("displayName", "Unknown") if tf.get("reporter") else "Unknown",
                            "created": tf.get("created", "")[:10] if tf.get("created") else "",
                            "target_version": fix_v
                        })

        return {
            "execution": execution_entry,
            "parent_plans": parent_plans,
            "linked_defects": linked_defects
        }

    def get_execution_metrics(self, execution_issues):
        """Fetch live test run statistics from Xray GraphQL concurrently for all executions."""
        jwt = self.get_jwt()
        if not execution_issues:
            return []

        def fetch_single_metric(te):
            k = te.get("key")
            iss_id = te.get("id")
            summary = te.get("fields", {}).get("summary", "")
            jira_status = te.get("fields", {}).get("status", {}).get("name", "")
            
            fix_versions = [v.get("name") for v in te.get("fields", {}).get("fixVersions", [])]
            versions = [v.get("name") for v in te.get("fields", {}).get("versions", [])]
            target_v = fix_versions[0] if fix_versions else (versions[0] if versions else "Unspecified")

            entry = {
                "key": k,
                "id": iss_id,
                "summary": summary,
                "jira_status": jira_status,
                "target_version": target_v,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "todo": 0,
                "executing": 0,
                "other": 0,
                "pass_rate": 0.0
            }

            if jwt and iss_id:
                query = f"""
                {{
                    getTestExecution(issueId: "{iss_id}") {{
                        issueId
                        testRuns(limit: 100) {{
                            total
                            results {{
                                status {{
                                    name
                                }}
                            }}
                        }}
                    }}
                }}
                """
                try:
                    data = self.xray_graphql(query)
                    res_te = data.get("data", {}).get("getTestExecution", {}) if data else {}
                    test_runs = res_te.get("testRuns", {}) if res_te else {}
                    total = test_runs.get("total", 0)
                    results = test_runs.get("results", [])
                    st_counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "TO DO": 0, "EXECUTING": 0, "OTHER": 0}
                    for r in results:
                        st_name = r.get("status", {}).get("name", "OTHER").upper()
                        if st_name == "PASS": st_name = "PASSED"
                        if st_name == "FAIL": st_name = "FAILED"
                        if st_name == "TODO": st_name = "TO DO"
                        st_counts[st_name if st_name in st_counts else "OTHER"] += 1
                    
                    p = st_counts["PASSED"]
                    f = st_counts["FAILED"]
                    s = st_counts["SKIPPED"]
                    td = st_counts["TO DO"]
                    ex = st_counts["EXECUTING"]
                    oth = st_counts["OTHER"]
                    
                    exec_cnt = p + f
                    rate = round(p / exec_cnt * 100, 1) if exec_cnt > 0 else 0.0
                    
                    entry.update({
                        "total": total,
                        "passed": p,
                        "failed": f,
                        "skipped": s,
                        "todo": td,
                        "executing": ex,
                        "other": oth,
                        "pass_rate": rate
                    })
                except Exception as ex_err:
                    print(f"GraphQL error for {k}: {ex_err}")

            return entry

        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            stats = list(executor.map(fetch_single_metric, execution_issues))
        return stats

    def get_plan_linked_defects(self, plan_key, execution_issues=None):
        """
        Deep search for defects linked to a Test Plan:
        1. Checks issuelinks of the Test Plan itself.
        2. Checks issuelinks of all Test Executions in the Test Plan.
        3. Detects product defect project (SIF for XPNB/SiFlex, ECD for XPECD/Sicharge D).
        """
        if not execution_issues:
            execution_issues = self.get_test_executions(plan_key)

        found_defects = {}

        # 1. From all executions (using preloaded issuelinks whenever available)
        for te in execution_issues:
            te_key = te.get("key") if isinstance(te, dict) else str(te)
            try:
                fields = te.get("fields", {}) if isinstance(te, dict) else {}
                issuelinks = fields.get("issuelinks")
                if issuelinks is None:
                    try:
                        te_full = self.jira_get(f"issue/{te_key}")
                        issuelinks = te_full.get("fields", {}).get("issuelinks", []) if te_full else []
                    except Exception:
                        issuelinks = []
                
                for link in issuelinks:
                    for direction in ["inwardIssue", "outwardIssue"]:
                        target = link.get(direction)
                        if target:
                            itype = target.get("fields", {}).get("issuetype", {}).get("name", "")
                            tkey = target.get("key", "")
                            st = target.get("fields", {}).get("status", {}).get("name", "Open")
                            
                            # Check if defect/bug
                            if itype.lower() in ["defect", "bug"] or tkey.startswith(("SIF-", "ECD-")):
                                tf = target.get("fields", {})
                                if tkey not in found_defects:
                                    found_defects[tkey] = {
                                        "key": tkey,
                                        "summary": tf.get("summary", ""),
                                        "priority": tf.get("priority", {}).get("name", "Medium"),
                                        "status": st,
                                        "assignee": tf.get("assignee", {}).get("displayName", "Unassigned") if tf.get("assignee") else "Unassigned",
                                        "reporter": tf.get("reporter", {}).get("displayName", "Unknown") if tf.get("reporter") else "Unknown",
                                        "created": tf.get("created", "")[:10] if tf.get("created") else "",
                                        "target_version": (tf.get("fixVersions") or [{}])[0].get("name", "None") if tf.get("fixVersions") else "None"
                                    }
            except Exception as e:
                print(f"Error checking issuelinks on {te_key}: {e}")

        # 2. From Test Plan itself
        try:
            plan_full = self.jira_get(f"issue/{plan_key}")
            for link in plan_full.get("fields", {}).get("issuelinks", []):
                for direction in ["inwardIssue", "outwardIssue"]:
                    target = link.get(direction)
                    if target:
                        itype = target.get("fields", {}).get("issuetype", {}).get("name", "")
                        tkey = target.get("key", "")
                        if itype.lower() in ["defect", "bug"] or tkey.startswith(("SIF-", "ECD-")):
                            tf = target.get("fields", {})
                            if tkey not in found_defects:
                                found_defects[tkey] = {
                                    "key": tkey,
                                    "summary": tf.get("summary", ""),
                                    "priority": tf.get("priority", {}).get("name", "Medium"),
                                    "status": target.get("fields", {}).get("status", {}).get("name", "Open"),
                                    "assignee": tf.get("assignee", {}).get("displayName", "Unassigned") if tf.get("assignee") else "Unassigned",
                                    "reporter": tf.get("reporter", {}).get("displayName", "Unknown") if tf.get("reporter") else "Unknown",
                                    "created": tf.get("created", "")[:10] if tf.get("created") else "",
                                    "target_version": (tf.get("fixVersions") or [{}])[0].get("name", "None") if tf.get("fixVersions") else "None"
                                }
        except Exception as e:
            print(f"Error checking issuelinks on {plan_key}: {e}")

        # 3. If SIF (SiFlex), add open Funnel defects from SIF project
        if "XPNB" in plan_key or any(k.startswith("SIF") for k in found_defects):
            sif_defects = self.get_defects(project_key="SIF", status="Funnel")
            for d in sif_defects:
                if d["key"] not in found_defects:
                    found_defects[d["key"]] = d

        return list(found_defects.values())

    def get_defects(self, project_key="SIF", status="Funnel", custom_jql=None, max_results=100):
        """Fetch project defects matching status or custom JQL."""
        if project_key == "XPNB":
            project_key = "SIF"

        if custom_jql:
            jql = custom_jql
        elif project_key and status:
            jql = f"project = {project_key} AND status = '{status}' ORDER BY priority DESC, created DESC"
        elif project_key:
            jql = f"project = {project_key} AND resolution is EMPTY ORDER BY priority DESC, created DESC"
        else:
            jql = "project = SIF AND status = 'Funnel' ORDER BY priority DESC, created DESC"

        try:
            res = self.jira_post("search/jql", {
                "jql": jql,
                "maxResults": max_results,
                "fields": ["summary", "priority", "status", "assignee", "reporter", "created", "fixVersions", "versions"]
            })
            issues = res.get("issues", [])
            
            clean_defects = []
            for iss in issues:
                f = iss.get("fields", {})
                clean_defects.append({
                    "key": iss.get("key"),
                    "summary": f.get("summary", ""),
                    "priority": f.get("priority", {}).get("name", "Medium"),
                    "status": f.get("status", {}).get("name", "Open"),
                    "assignee": f.get("assignee", {}).get("displayName", "Unassigned") if f.get("assignee") else "Unassigned",
                    "reporter": f.get("reporter", {}).get("displayName", "Unknown") if f.get("reporter") else "Unknown",
                    "created": f.get("created", "")[:10] if f.get("created") else "",
                    "target_version": (f.get("fixVersions") or [{}])[0].get("name", "None") if f.get("fixVersions") else "None"
                })
            return clean_defects
        except Exception as e:
            print(f"Error fetching defects with JQL '{jql}': {e}")
            return []
