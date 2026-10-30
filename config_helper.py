import os
import json
import socket
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

def get_crypto_key(host=None):
    hostname = host or socket.gethostname()
    material = hashlib.sha256((hostname + "-ocpp-dashboard").encode('utf-8')).hexdigest().encode('utf-8')
    kdf = Scrypt(salt=b"ocpp-cert-v1", length=32, n=16384, r=8, p=1)
    return kdf.derive(material)

def decrypt(val, key=None):
    if not val or not isinstance(val, str) or not val.startswith("enc:"):
        return val
    parts = val[4:].split(":")
    if len(parts) != 3:
        return val
    iv = bytes.fromhex(parts[0])
    tag = bytes.fromhex(parts[1])
    ct = bytes.fromhex(parts[2])

    if key is not None:
        keys_to_try = [key]
    else:
        # Try local machine hostname first, then fallback to original source host 'md63hbdc'
        curr_host = socket.gethostname()
        keys_to_try = [get_crypto_key(curr_host)]
        if curr_host != "md63hbdc":
            keys_to_try.append(get_crypto_key("md63hbdc"))

    for k in keys_to_try:
        try:
            aesgcm = AESGCM(k)
            return aesgcm.decrypt(iv, ct + tag, None).decode('utf-8')
        except Exception:
            continue
    return val

def load_config():
    paths = [
        os.path.join(os.path.dirname(__file__), "dashboard-config.json"),
        os.path.join(os.path.dirname(__file__), "..", "dashboard-config.json"),
        r"f:\DISCO_D_BACKUP\OCA_FINAL_CANDITOS\dashboard-config.json"
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

def get_jira_credentials():
    cfg = load_config()
    jira_cfg = cfg.get("jira", {}) if isinstance(cfg.get("jira"), dict) else {}
    base_url = cfg.get("jiraBaseUrl") or jira_cfg.get("baseUrl") or "https://jira.siemens.com"
    email = decrypt(cfg.get("jiraEmail") or jira_cfg.get("email"))
    token = decrypt(cfg.get("jiraApiToken") or jira_cfg.get("apiToken"))
    return base_url.rstrip('/'), email, token

def get_xray_credentials():
    cfg = load_config()
    cid = decrypt(cfg.get("xrayClientId"))
    csec = decrypt(cfg.get("xrayClientSecret"))
    return cid, csec
