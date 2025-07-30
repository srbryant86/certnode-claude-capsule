# tier_enforcer.py
# Tiny heuristic tier estimator + gate. Claude-ready, no external deps.

from typing import Dict

_CONNECTORS = ("however", "therefore", "thus", "hence", "although", "because")
_FALLACIES = ("ad hominem", "strawman", "whataboutism", "slippery slope")


def estimate_tier(text: str) -> int:
    """Heuristic T-score in [2..16] using length, connectors, causals, and refs."""
    words = len(text.split())
    connectors = sum(text.lower().count(k) for k in _CONNECTORS)
    causals = text.lower().count("because") + text.lower().count("due to")
    refs = text.count("http") + text.count("[") + text.count("§")
    fallacies = sum(text.lower().count(f) for f in _FALLACIES)

    # naive scoring: structure + evidence push up; fallacies pull down
    score = 2
    score += min(6, words // 120)        # length: ~720+ words -> +6
    score += min(4, connectors)          # explicit connective logic
    score += min(2, causals)             # causal anchors
    score += min(2, refs)                # citations / anchors
    score -= min(3, fallacies)           # obvious fallacy terms

    return int(max(2, min(16, score)))


class TierEnforcer:
    """Gate that explains why a passage did/didn't meet the minimum tier."""
    def enforce(self, text: str, minimum: int = 13) -> Dict:
        t = estimate_tier(text)
        ok = t >= minimum
        reasons = []
        if not ok:
            if len(text.split()) < 360:
                reasons.append("too_short_for_high_tier")
            if sum(text.lower().count(k) for k in _CONNECTORS) < 2:
                reasons.append("insufficient_connective_logic")
            if ("because" not in text.lower()) and ("due to" not in text.lower()):
                reasons.append("missing_causal_anchors")
            if any(f in text.lower() for f in _FALLACIES):
                reasons.append("fallacy_terms_detected")
            if not reasons:
                reasons.append("insufficient_complexity_signal")
        return {"ok": ok, "estimated_tier": f"T{t}", "minimum": f"T{minimum}", "reasons": reasons}
