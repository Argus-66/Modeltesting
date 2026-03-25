# test_models.py
import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask(model, prompt, context=""):
    payload = {
        "model": model,
        "prompt": f"{context}\n\n{prompt}" if context else prompt,
        "stream": False
    }
    start = time.time()
    res = requests.post(OLLAMA_URL, json=payload)
    elapsed = round(time.time() - start, 1)
    data = res.json()
    return data["response"], elapsed

print("=" * 50)
print("Testing deepseek-r1:8b (Analyst)...")
analyst_out, t1 = ask(
    "deepseek-r1:8b",
    "A stock called GOLDETF (Gold ETF on NSE) is down 15% from purchase price but gold globally is rising. In 2-3 sentences, what is your analysis?"
)
print(f"[{t1}s] {analyst_out}\n")

print("=" * 50)
print("Testing mistral:7b (Contrarian)...")
contrarian_out, t2 = ask(
    "mistral:7b",
    "Challenge this analysis in 2 sentences — find the biggest risk or flaw:",
    context=analyst_out
)
print(f"[{t2}s] {contrarian_out}\n")

# ✅ NEW QUANT BLOCK ADDED HERE
print("=" * 50)
print("Testing qwen2.5:7b (Quant)...")
quant_out, t_quant = ask(
    "qwen2.5:7b",
    "Given this portfolio scenario and the two views above, verify the numerical reasoning. Are the figures and percentages being cited correctly? Flag any mathematical inconsistencies in 2-3 sentences.",
    context=f"Analyst: {analyst_out}\n\nContrarian: {contrarian_out}"
)
print(f"[{t_quant}s] {quant_out}\n")

print("=" * 50)
print("Testing synthesis (deepseek-r1:8b as Arbiter)...")
synthesis, t3 = ask(
    "deepseek-r1:8b",
    "Given the analyst view, the contrarian challenge, and the quant verification, give a final verdict with a confidence score (0-100%) in 2-3 sentences.",
    context=f"Analyst: {analyst_out}\n\nContrarian: {contrarian_out}\n\nQuant: {quant_out}"
)
print(f"[{t3}s] {synthesis}\n")

print("=" * 50)
print(f"Total debate time: {round(t1+t2+t_quant+t3, 1)}s")
print("All models working!" if analyst_out and contrarian_out and quant_out and synthesis else "Something failed.")