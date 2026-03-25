import requests
import time
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

# 🔧 CONFIG
TIMEOUT = 600
MAX_CONTEXT_CHARS = 4000

def ask(model, prompt, context=""):
    full_prompt = f"{context}\n\n---\n{prompt}" if context else prompt

    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False
    }

    start = time.time()
    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        elapsed = round(time.time() - start, 1)
        return res.json()["response"].strip(), elapsed
    except requests.exceptions.ReadTimeout:
        return "⚠️ TIMEOUT", TIMEOUT

# --- Test input ---
PORTFOLIO = """
Instrument: GOLDETF
Qty: 30 | Avg Cost: 160.27 | LTP: 135.26
Invested: 4808.10 | Cur Val: 4057.80 | P&L: -750.30 | Net chg: -15.60% | Day chg: +3.45%
"""

NEWS = """
- Gold prices globally up 4% this week on Fed rate uncertainty
- RBI holds rates steady, rupee weakens slightly
- SEBI introduces new ETF disclosure norms
"""

transcript = []

def log(role, model, output, t):
    transcript.append({
        "role": role,
        "model": model,
        "output": output,
        "time": t
    })

    print(f"\n{'='*55}")
    print(f"[{role}] {model} — {t}s")
    print(f"{'='*55}")
    print(output)

# 🔥 LIMIT CONTEXT SIZE
def build_context():
    context = "\n\n".join([
        f"[{e['role']}] {e['model']}:\n{e['output']}"
        for e in transcript
    ])
    return context[-MAX_CONTEXT_CHARS:]

# ── ROUND 1 ──────────────────────────────
print("\n🔵 ROUND 1 — Analyst opening")
r1, t1 = ask(
    "deepseek-r1:8b",
    f"""You are a financial analyst. Analyse this portfolio and news.

Portfolio:
{PORTFOLIO}

News:
{NEWS}

Give:
1. What is happening and why
2. Key risks
3. Bull vs Bear scenario

Be concise. Max 120 words. No repetition."""
)
log("Round 1 — Analyst", "deepseek-r1:8b", r1, t1)

# ── ROUND 2A ─────────────────────────────
print("\n🔴 ROUND 2A — Contrarian")
r2a, t2a = ask(
    "mistral:7b",
    """You are a contrarian.

Challenge the analyst:
1. Wrong assumptions
2. Missed risks
3. Weakest bullish point

Be sharp. Max 120 words. No repetition.""",
    context=build_context()
)
log("Round 2A — Contrarian", "mistral:7b", r2a, t2a)

# ── ROUND 2B ─────────────────────────────
print("\n🟢 ROUND 2B — Quant")
r2b, t2b = ask(
    "qwen2.5:7b",
    f"""You are a quant.

Portfolio:
{PORTFOLIO}

Tasks:
1. Verify all numbers
2. % recovery to breakeven
3. Is +3.45% meaningful vs -15.6%?
4. Reliability score (0-100)

Be precise. Max 120 words.""",
    context=build_context()
)
log("Round 2B — Quant", "qwen2.5:7b", r2b, t2b)

# ── ROUND 3 ──────────────────────────────
print("\n🔵 ROUND 3 — Analyst rebuttal")
r3, t3 = ask(
    "deepseek-r1:8b",
    """You are the analyst again.

1. What do you concede?
2. What do you defend?
3. Update scenarios
4. Conviction change?

Be concise. Max 120 words.""",
    context=build_context()
)
log("Round 3 — Analyst rebuttal", "deepseek-r1:8b", r3, t3)

# ── ROUND 4A ─────────────────────────────
print("\n🔴 ROUND 4A — Contrarian final")
r4a, t4a = ask(
    "mistral:7b",
    """Final contrarian stance:

1. Any concessions?
2. Strongest objection
3. Bearish probability %

Max 100 words. No repetition.""",
    context=build_context()
)
log("Round 4A — Contrarian final", "mistral:7b", r4a, t4a)

# ── ROUND 4B ─────────────────────────────
print("\n🟢 ROUND 4B — Quant final")
r4b, t4b = ask(
    "qwen2.5:7b",
    """Final quant check:

1. Are numbers coherent?
2. Confidence score (0-100)
3. One key metric to watch

Max 100 words.""",
    context=build_context()
)
log("Round 4B — Quant final", "qwen2.5:7b", r4b, t4b)

# ── ARBITER ──────────────────────────────
print("\n⭐ ARBITER — Final verdict")
arbiter, t_arb = ask(
    "mistral:7b",  # ⚡ faster than deepseek
    """Give final verdict:

SIGNAL: BULLISH / BEARISH / NEUTRAL
CONFIDENCE: %

BULL CASE: 1 line + %
BEAR CASE: 1 line + %

BEST POINTS:
- Analyst:
- Contrarian:
- Quant:

ACTION: HOLD / WATCH / EXIT
REASON: 2 lines max

Max 120 words.""",
    context=build_context()
)
log("Arbiter", "mistral:7b", arbiter, t_arb)

# ── SUMMARY ──────────────────────────────
total = round(t1 + t2a + t2b + t3 + t4a + t4b + t_arb, 1)

print(f"\n{'='*55}")
print(f"✅ Completed in {total}s ({round(total/60,1)} min)")
print(f"R1={t1}s | R2={t2a+t2b}s | R3={t3}s | R4={t4a+t4b}s | Arbiter={t_arb}s")