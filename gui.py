import json, subprocess, html, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
D = os.path.dirname(os.path.abspath(__file__)); P = D + "/policy.json"
IF = {"users": "eth1", "servers": "eth2"}
def load(): return json.load(open(P))
def save(r): json.dump(r, open(P, "w"), indent=1)
def ruleset(rules):
    o = ["flush ruleset", "table inet fw {", " chain forward {", "  type filter hook forward priority 0; policy drop;", "  ct state established,related accept"]
    for r in rules:
        m = 'iifname "%s" oifname "%s" ' % (IF[r["from"]], IF[r["to"]])
        if r["proto"] == "icmp": m += "ip protocol icmp "
        elif r["proto"] in ("tcp", "udp"): m += r["proto"] + (" dport " + r["port"] if r["port"] else " ") + " "
        o.append("  " + m + "counter " + r["action"])
    return "\n".join(o + [" }", "}"]) + "\n"
def apply():
    open(D + "/rules.nft", "w").write(ruleset(load()))
    try: return subprocess.run(["nft", "-f", D + "/rules.nft"], capture_output=True, text=True).stderr.strip()
    except FileNotFoundError: return "nft not installed"
def live():
    try: return subprocess.run(["nft", "list", "ruleset"], capture_output=True, text=True).stdout
    except Exception as e: return "nft unavailable: " + str(e)
def page(msg=""):
    rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><form method=post><input type=hidden name=a value=del><input type=hidden name=i value=%d><button>Delete</button></form></td></tr>" % (r["from"], r["to"], r["proto"], html.escape(r["port"]), r["action"], i) for i, r in enumerate(load()))
    z = "".join("<option>%s</option>" % k for k in IF)
    return ("<!DOCTYPE html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>fw1</title><style>body{font:14px system-ui;margin:20px;max-width:900px}table{border-collapse:collapse}td,th{border:1px solid #888;padding:4px 8px}pre{background:#eee;color:#111;padding:8px;overflow:auto}</style>"
      "<h2>fw1 firewall policy</h2><p>Default: deny everything between zones. users = eth1 (fabric side), servers = eth2.</p><p style=color:#c00>%s</p>"
      "<table><tr><th>From</th><th>To</th><th>Proto</th><th>Port</th><th>Action</th><th></th></tr>%s</table>"
      "<h3>Add rule</h3><form method=post><input type=hidden name=a value=add>From <select name=from>%s</select> To <select name=to>%s</select> Proto <select name=proto><option>tcp</option><option>udp</option><option>icmp</option><option>any</option></select> Port <input name=port size=6> Action <select name=action><option>accept</option><option>drop</option></select> <button>Add and apply</button></form>"
      "<h3>Live ruleset (counters)</h3><pre>%s</pre>") % (html.escape(msg), rows, z, z, html.escape(live()))
class H(BaseHTTPRequestHandler):
    def send(self, b):
        self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers(); self.wfile.write(b.encode())
    def do_GET(self): self.send(page())
    def do_POST(self):
        q = {k: v[0] for k, v in parse_qs(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()).items()}
        r = load(); msg = ""
        if q.get("a") == "del" and q.get("i", "").isdigit() and int(q["i"]) < len(r): r.pop(int(q["i"]))
        elif q.get("a") == "add":
            port = q.get("port", "").strip()
            if q.get("from") in IF and q.get("to") in IF and q.get("from") != q.get("to") and q.get("proto") in ("tcp", "udp", "icmp", "any") and q.get("action") in ("accept", "drop") and (port == "" or (port.isdigit() and 0 < int(port) < 65536)):
                r.append({"from": q["from"], "to": q["to"], "proto": q["proto"], "port": port if q["proto"] in ("tcp", "udp") else "", "action": q["action"]})
            else: msg = "Invalid rule"
        save(r); msg = msg or apply(); self.send(page(msg))
if __name__ == "__main__":
    apply(); HTTPServer(("0.0.0.0", 8080), H).serve_forever()
