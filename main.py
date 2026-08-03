import numpy as np
from emperors_command_center import TashCommandCenter
import json
import re

print("\n🏛️  TASH v2.0 - Open Source Throne (Reset Complete)")
print("📍 Genesis Fingerprint: [4, 2, 1, 2, 1, 0, 0, 0, 0] (Archived)")
print("="*50)

def extract_numbers(text):
    nums = re.findall(r'\d+\.?\d*', text)
    context = {}
    for i, n in enumerate(nums):
        context[f"param_{i+1}"] = float(n)
    if not context:
        context = {"mass": 1.0, "energy": 2.0, "gravity": 3.0}
    return context

ecc = TashCommandCenter()

while True:
    cmd = input("\n📜 Decree > ")
    if cmd.lower() in ["exit", "quit"]:
        break
    if not cmd.strip():
        continue
    
    data = extract_numbers(cmd)
    print(f"📊 Processing: {data}")
    response = ecc.execute(cmd, data)
    print("\n👑 TASH Apex Truth:")
    print(json.dumps(response, indent=2, default=str))
