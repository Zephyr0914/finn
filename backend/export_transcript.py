import json
import re
import os

path = r"C:\Users\91997\.gemini\antigravity\brain\8dd3beb2-b1a9-4ea1-9c7a-d6db2e874a79\.system_generated\logs\transcript_full.jsonl"
out_md = r"C:\Users\91997\.gemini\antigravity\scratch\finn\AI_CHAT_TRANSCRIPT.md"
out_html = r"C:\Users\91997\.gemini\antigravity\scratch\finn\frontend\transcript.html"

dialogue = []
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            obj = json.loads(line)
        except Exception:
            continue
        t = obj.get("type")
        src = obj.get("source")
        created = obj.get("created_at", "")[:19].replace("T", " ")

        if t == "USER_INPUT" and src == "USER_EXPLICIT":
            c = obj.get("content", "").strip()
            c = re.sub(r"==Start of PDF==.*?==End of PDF==", "[Attached ENAM PDF Brief & Reference Guide]", c, flags=re.DOTALL)
            c = re.sub(r"<USER_REQUEST>\s*", "", c)
            c = re.sub(r"\s*</USER_REQUEST>", "", c)
            dialogue.append({"role": "USER", "time": created, "text": c})
        elif t == "PLANNER_RESPONSE" and src == "MODEL":
            c = obj.get("content", "")
            if c and c.strip():
                dialogue.append({"role": "FINN AGENT", "time": created, "text": c.strip()})

print(f"Extracted {len(dialogue)} dialogue turns.")

# Write Markdown
with open(out_md, "w", encoding="utf-8") as f:
    f.write("# AI Development & Pairing Conversation History\n\n")
    f.write("> **Project**: FINN — Financial Investment Agent (ENAM Holdings Challenge)\n")
    f.write("> **Conversation ID**: `8dd3beb2-b1a9-4ea1-9c7a-d6db2e874a79`\n")
    f.write("> **Engine**: Gemini 3.8 Flash (Medium) / Antigravity Agentic Platform\n\n---\n\n")

    for turn in dialogue:
        role = turn["role"]
        time_str = turn["time"]
        text = turn["text"]

        if "USER" in role:
            f.write(f"### 👤 User [{time_str}]\n\n")
            f.write(f"{text}\n\n---\n\n")
        else:
            f.write(f"### 🔮 FINN Agent [{time_str}]\n\n")
            f.write(f"{text}\n\n---\n\n")

# Write HTML
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FINN — AI Development Chat Transcript</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0f1e; color: #e8f0fe; margin: 0; padding: 24px; line-height: 1.6; }
.container { max-width: 860px; margin: 0 auto; }
.header { border-bottom: 1px solid #1e3a5f; padding-bottom: 16px; margin-bottom: 24px; }
.title { font-size: 24px; font-weight: 800; color: #60a5fa; }
.meta { font-size: 12px; color: #94a3b8; margin-top: 4px; }
.turn { margin-bottom: 24px; padding: 18px; border-radius: 12px; border: 1px solid #1e3a5f; }
.user { background: #111827; border-left: 4px solid #3b82f6; }
.agent { background: #1a2235; border-left: 4px solid #a855f7; }
.role { font-size: 13px; font-weight: 700; display: flex; justify-content: space-between; margin-bottom: 10px; }
.user .role { color: #60a5fa; }
.agent .role { color: #c084fc; }
.time { font-size: 11px; color: #64748b; font-weight: normal; }
.content { font-size: 14px; white-space: pre-wrap; word-break: break-word; color: #cbd5e1; }
</style>
</head>
<body>
<div class="container">
<div class="header">
  <div class="title">🔮 FINN — Complete AI Development Transcript</div>
  <div class="meta">Conversation ID: 8dd3beb2-b1a9-4ea1-9c7a-d6db2e874a79 | ENAM Holdings AI Engineer Build Challenge</div>
</div>
"""

for turn in dialogue:
    cls = "user" if "USER" in turn["role"] else "agent"
    escaped_text = turn["text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_content += f"""
<div class="turn {cls}">
  <div class="role">
    <span>{'👤 ' if cls == 'user' else '🔮 '}{turn['role']}</span>
    <span class="time">{turn['time']}</span>
  </div>
  <div class="content">{escaped_text}</div>
</div>
"""

html_content += """
</div>
</body>
</html>
"""

with open(out_html, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Export completed successfully.")
