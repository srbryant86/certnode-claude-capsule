# valence_swap.py
# Lightweight satire/irony detector and penalty swapper.

from typing import Dict

SATIRE_MARKERS = (
    "/s", "s/ ", "sarcasm", "irony", "ironic", "yeah right", "as if",
    "totally", "obviously", "sure, jan", "🙄", "😂", "🤣", "smh",
)
CONTRASTERS = ("sure", "right", "totally", "literally", "obviously")
HYPERBOLE = ("literally", "absolutely", "infinitely", "always", "never", "best", "worst")
PUNCT = ("?!", "!!!")


def _ratio_caps(text: str) -> float:
    caps = sum(1 for c in text if c.isupper())
    letters = sum(1 for c in text if c.isalpha())
    return (caps / letters) if letters else 0.0


class ValenceSwap:
    def detect(self, text: str) -> Dict:
        t = text.lower()
        score = 0
        score += sum(marker in t for marker in SATIRE_MARKERS) * 2
        score += sum(word in t for word in HYPERBOLE)
        score += sum(p in text for p in PUNCT)
        score += 1 if any(w in t for w in CONTRASTERS) and ("but" in t or "however" in t) else 0
        score += 1 if _ratio_caps(text) > 0.18 else 0
        # Normalize to 0..1-ish
        conf = min(1.0, score / 6.0)
        return {"is_satire": conf >= 0.5, "confidence": round(conf, 2), "raw": score}

    def adjust(self, valence: Dict, text: str) -> Dict:
        """If satire is likely, reduce intensity & neutralize polarity."""
        det = self.detect(text)
        v = dict(valence)  # copy
        if det["is_satire"]:
            v["mode"] = "satirical"
            v["intensity"] = max(0.0, float(v.get("intensity", 0.3)) * 0.35)
            v["polarity"] = "neutral"
            v["swap_applied"] = True
            v["satire_confidence"] = det["confidence"]
        else:
            v["swap_applied"] = False
            v["satire_confidence"] = det["confidence"]
        return v
