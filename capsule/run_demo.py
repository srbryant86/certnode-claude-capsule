# capsule/run_demo.py

import os, json, datetime
from dataclasses import dataclass
from typing import List, Dict, Any

# ---- CMF (minimal) ----
@dataclass
class CausalNode:
    id: str
    clause: str
    cause: str
    mutation: str
    result: str

class CMFEngine:
    def __init__(self):
        self.history: List[CausalNode] = []
    def add(self, clause, cause="input", mutation="none", result="ok"):
        nid = f"CN{len(self.history)+1}"
        n = CausalNode(nid, clause, cause, mutation, result)
        self.history.append(n)
        return n
    def why_emerged(self, n: CausalNode):
        return f"'{n.clause}' due to {n.cause}/{n.mutation}"
    def audit_fault(self, n: CausalNode):
        return "fault" if any(k in n.result for k in ["drift","contradiction"]) else "ok"
    def repair(self, n: CausalNode):
        fix = f"Refactor:{n.clause}" if "drift" in n.result else n.clause
        return self.add(fix, cause="cmf-repair", mutation="refactor", result="progression")

# ---- RDE (minimal) ----
class RDE:
    def __init__(self):
        self.trace=[]
    def introspect(self, agent, claim, method="analysis"):
        r = {"agent":agent,"claim":claim,"method":method,"t":datetime.datetime.utcnow().isoformat()}
        self.trace.append(r)
        return r
    def disputation(self, a,b):
        return {"synthesis": f"Method critique: {a['method']} vs {b['method']}", "agree_on": "shared premises?"}

# ---- CertEngine (thin) ----
class CertEngine:
    def __init__(self):
        self.cmf=CMFEngine()
        self.rde=RDE()
    def certify(self, text: str) -> Dict[str,Any]:
        n = self.cmf.add(text)
        ai = self.rde.introspect("agentA", text, "pattern")
        bi = self.rde.introspect("agentB", text, "counterfactual")
        syn = self.rde.disputation(ai, bi)
        status = self.cmf.audit_fault(n)
        if status!="ok":
            self.cmf.repair(n)
        return {
            "tier_hint":"T13-15",
            "cmf_reason":self.cmf.why_emerged(n),
            "dialectic":syn,
            "history":[h.__dict__ for h in self.cmf.history]
        }

if __name__ == "__main__":
    sample = os.environ.get("CERTNODE_TEXT","Test paragraph, however therefore thus.")
    out = CertEngine().certify(sample)
    print(json.dumps(out, indent=2))
