"""Zero-shot baseline: only PDF-to-text and a normal user question.
No audit taxonomy, examples, JSON schema, verification, or categorisation rules.
"""
from pathlib import Path
import sys, subprocess, json, time, hashlib
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/".deps"))
from pypdf import PdfReader
SPECS={
 "2021":("anao-2021-strategies.pdf",[43,44,45]),
 "2024":("anao-2024-incidents.pdf",[48,49])
}
Q=("Read the following excerpts from a government audit report. "
   "Identify the IT or cybersecurity control weaknesses described. "
   "For each issue, briefly explain what was wrong and identify the agency and source page. "
   "Mention any common themes you notice. Base your answer only on the excerpts.")
def main():
 key=sys.argv[1]
 name,nums=SPECS[key]
 pdf=PdfReader(str(ROOT/"data"/"raw"/name))
 pages="\n\n".join(f"PDF page {n}:\n{pdf.pages[n-1].extract_text() or ''}" for n in nums)
 prompt="Do not call tools. The report excerpts are included below.\n\n"+Q+"\n\n"+pages
 cmd=[r"C:\Users\ryano\.codex\packages\standalone\current\bin\codex.exe",
      "exec","--ephemeral","--ignore-user-config","--sandbox","read-only",
      "-m","gpt-6-luna","-c",'model_reasoning_effort="medium"',
      "-C",str(ROOT),"-"]
 start=time.monotonic()
 try:
  result=subprocess.run(cmd,input=prompt,capture_output=True,text=True,
                        encoding="utf-8",errors="replace",cwd=ROOT,timeout=145)
 except subprocess.TimeoutExpired:
  raise SystemExit("Baseline request timed out; no result saved")
 if result.returncode or not result.stdout.strip():
  raise SystemExit(f"Codex failed with code {result.returncode} or empty response")
 out={
  "kind":"plain_prompt_no_framework",
  "model":"gpt-6-luna","reasoning_effort":"medium",
  "source_file":name,"physical_pdf_pages":nums,
  "summary_pages_not_supplied":[7,8,9,10,11],
  "user_prompt":Q,"full_prompt_sha256":hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
  "duration_seconds":round(time.monotonic()-start,2),
  "utc":datetime.now(timezone.utc).isoformat(),
  "raw_answer":result.stdout.strip(),
 }
 path=ROOT/"data"/"evaluations"/f"anao-baseline-{key}-luna-medium.json"
 path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 print(json.dumps({"year":key,"duration":out["duration_seconds"],"chars":len(out["raw_answer"]),"file":str(path)}))
if __name__=="__main__":main()
