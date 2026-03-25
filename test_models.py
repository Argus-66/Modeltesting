# test_debate.py
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask(model, prompt, context=""):
    full_prompt = f"{context}\n\n---\n{prompt}" if context else prompt
    payload = {"model": model, "prompt": full_prompt, "stream": False}
    start = time.time()
    res = requests.post(OLLAMA_URL, json=payload, timeout=300)
    elapsed = round(time.time() - start, 1)
    return res.json()["response"].strip(), elapsed

# --- Test input (your real format) ---
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
    transcript.append({"role": role, "model": model, "output": output, "time": t})
    print(f"\n{'='*55}")
    print(f"[{role}] {model} — {t}s")
    print(f"{'='*55}")
    print(output)

def build_context():
    return "\n\n".join([
        f"[{e['role']}] {e['model']}:\n{e['output']}"
        for e in transcript
    ])

# ── ROUND 1: Analyst opens ──────────────────────────────
print("\n🔵 ROUND 1 — Analyst opening")
r1, t1 = ask(
    "deepseek-r1:8b",
    f"""You are a financial analyst. Analyse this Indian stock portfolio and recent news.
    
Portfolio:
{PORTFOLIO}

Recent News:
{NEWS}

Provide:
1. What is happening to this holding and why
2. Key risks you see
3. Two possible scenarios (bullish and bearish) with brief reasoning
Be specific and concise."""
)
log("Round 1 — Analyst", "deepseek-r1:8b", r1, t1)

# ── ROUND 2A: Contrarian challenges ────────────────────
print("\n🔴 ROUND 2A — Contrarian challenge")
r2a, t2a = ask(
    "mistral:7b",
    """You are a skeptical contrarian analyst. You have read the analyst's view above.
Your job is to challenge it. Specifically:
1. What assumptions is the analyst making that could be wrong?
2. What risks did they miss or underweight?
3. What is the weakest part of their bullish scenario?
Be direct and specific. Do not repeat what the analyst said.""",
    context=build_context()
)
log("Round 2A — Contrarian", "mistral:7b", r2a, t2a)

# ── ROUND 2B: Quant checks numbers ─────────────────────
print("\n🟢 ROUND 2B — Quant verification")
r2b, t2b = ask(
    "qwen2.5:7b",
    f"""You are a quantitative analyst. You have the portfolio data and the two views above.
    
Portfolio data:
{PORTFOLIO}

Your job:
1. Verify all numbers and percentages cited by both analysts are mathematically consistent
2. Calculate: what % price recovery is needed to break even?
3. Is the day change (+3.45%) meaningful relative to the total loss (-15.60%)?
4. Rate the numerical reliability of the analysis so far: 0-100%
Be precise. Show your calculations.""",
    context=build_context()
)
log("Round 2B — Quant", "qwen2.5:7b", r2b, t2b)

# ── ROUND 3: Analyst rebuts ─────────────────────────────
print("\n🔵 ROUND 3 — Analyst rebuttal")
r3, t3 = ask(
    "deepseek-r1:8b",
    """You are the original analyst. You have now read the contrarian's challenges and the quant's numbers.

1. Which of the contrarian's points do you CONCEDE are valid? Why?
2. Which points do you DEFEND? Why?
3. Update your two scenarios with any corrections from the quant
4. Has your overall conviction changed? If so, in which direction?
Be honest about weaknesses in your original view.""",
    context=build_context()
)
log("Round 3 — Analyst rebuttal", "deepseek-r1:8b", r3, t3)

# ── ROUND 4A: Contrarian final position ────────────────
print("\n🔴 ROUND 4A — Contrarian final position")
r4a, t4a = ask(
    "mistral:7b",
    """You are the contrarian. You have now seen the analyst's rebuttal.

1. Do you concede any points after their rebuttal?
2. What is your single strongest remaining objection?
3. Give your own probability estimate: what % chance does the bearish scenario play out?
Keep it tight — 3-4 sentences max.""",
    context=build_context()
)
log("Round 4A — Contrarian final", "mistral:7b", r4a, t4a)

# ── ROUND 4B: Quant final check ─────────────────────────
print("\n🟢 ROUND 4B — Quant final check")
r4b, t4b = ask(
    "qwen2.5:7b",
    """You are the quant. The debate has evolved. Do a final check:

1. Are the revised scenarios numerically coherent?
2. What is the data confidence score for this analysis overall (0-100%)? 
   Factor in: data quality, calculation accuracy, and how well the numbers support the conclusions.
3. One sentence: what single number or metric should the investor watch most closely?""",
    context=build_context()
)
log("Round 4B — Quant final", "qwen2.5:7b", r4b, t4b)

# ── ARBITER: Final verdict ──────────────────────────────
print("\n⭐ ARBITER — Final structured verdict")
arbiter, t_arb = ask(
    "deepseek-r1:8b",
    """You are the arbiter. You have read the full debate above. Produce a final structured verdict.

Format your response EXACTLY like this:

SIGNAL: [BULLISH / BEARISH / NEUTRAL]
CONFIDENCE: [0-100%]

SCENARIO A (Bullish): [1 sentence] — Probability: [%]
SCENARIO B (Bearish): [1 sentence] — Probability: [%]

KEY DEBATE POINTS:
- Analyst strongest point: [1 sentence]
- Contrarian strongest point: [1 sentence]  
- Quant key finding: [1 sentence]

SUGGESTED ACTION: [HOLD / WATCH / CONSIDER EXIT]
REASONING: [2-3 sentences max]

WARNING: This is AI-generated analysis, not financial advice.""",
    context=build_context()
)
log("Arbiter — Final verdict", "deepseek-r1:8b", arbiter, t_arb)

# ── Summary ─────────────────────────────────────────────
total = round(t1 + t2a + t2b + t3 + t4a + t4b + t_arb, 1)
print(f"\n{'='*55}")
print(f"Full debate complete in {total}s ({round(total/60, 1)} min)")
print(f"Rounds: R1={t1}s | R2={t2a+t2b}s | R3={t3}s | R4={t4a+t4b}s | Arbiter={t_arb}s")