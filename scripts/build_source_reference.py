"""Source-first reference annotations for bounded 14-page ANAO evaluation.

Created using original PDF text, before opening current run prediction records
in this evaluation session. A reviewer has prior exposure to broad result
summaries, so this is source-first but not strictly blinded or auditor certified.
"""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"));sys.path.insert(0,str(ROOT/".deps"))
from audit_assurance.core import read_report,normalise

# year, page, observation locator, agency_scope, atomic weakness, direct quote excerpt
LABELS=[
("2018",45,"page 45","All three audited entities","Cyber-security improvement prioritisation was not systematically risk based","The three entities had not adopted a systematic risk-based approach to prioritise improvements"),
("2018",45,"page 45","All three audited entities","Cyber initiatives after FY2017–18 had not been identified and documented","identified and documented cyber initiatives beyond"),
("2018",46,"4.15","National Archives and Geoscience Australia","Enterprise IT architecture plans were outdated or did not represent actual systems","these plans were out-of-date and/or did not reflect"),
("2018",46,"4.15","Audited entities (specific agency scope unclear)","Supporting IT architecture records lacked inventory of security initiatives and effectiveness of controls","Supporting documentation did not include: the security initiatives in"),
("2018",46,"4.15","Audited entities (specific agency scope unclear)","No endorsed data-storage strategy identifying data owners, importance and security classification","an endorsed storage strategy"),
("2018",46,"4.18","All three audited entities","Audit/risk committees did not review vulnerabilities and cyber threats","There was no evidence that"),
("2018",46,"4.18","National Archives of Australia","Divisional cyber risk registers were not consolidated at enterprise level","risk registers were prepared at the division or branch level but"),
("2018",46,"4.18","Geoscience Australia","Divisional cyber risk registers were not consolidated at enterprise level","risk registers were prepared at the division or branch level but"),
("2018",46,"4.19","National Archives of Australia","The Chief Information Officer role was unfilled at the time of the audit","National Archives was in the process of recruiting a Chief Information Officer"),
("2019",24,"2.14","Australia Post","Vulnerability assessments and reporting excluded some critical IT systems","these did not cover all critical systems"),
("2019",24,"2.14","ASC","Identified vulnerabilities were not all documented","ASC does not document all the vulnerabilities identified"),
("2019",24,"2.17","ASC","Critical IT assets were not identified separately","ASC has not separately identified critical ICT assets"),
("2019",24,"2.17","ASC","Threat/risk profiles were not tailored to individual information assets","Further work would be required by ASC to develop tailored threat and risk profiles"),
("2019",24,"2.17","ASC","Information security strategy had not been updated since 2016","ASC has not updated its information security strategy since 2016"),
("2019",24,"2.18","Australia Post","Threats, risks and mitigations not documented for all critical IT assets","it has not documented the threats, risks and mitigations against all critical assets"),
("2019",26,"2.25","Australia Post","Half of sampled framework controls were partly implemented or not implemented","Three of the 10 sampled controls were partly implemented and two controls were not implemented"),
("2019",26,"2.25","Australia Post","No approval documentation or risk assessment for deviations from the security framework","No approval documentation or risk assessment was available"),
("2019",31,"3.13","ASC","Patch timeframes were not consistently met, including some extreme-risk patches","including for some extreme risk patches in ASC and Australia Post"),
("2019",31,"3.13","Australia Post","Patch timeframes were not consistently met, including some extreme-risk patches","including for some extreme risk patches in ASC and Australia Post"),
("2019",31,"3.13","Reserve Bank of Australia","Patch timeframes were not consistently met for some non-extreme-risk patches","for some non-extreme risk patches within the Reserve Bank"),
("2019",31,"3.15","Australia Post","Server patch remediation excluded lower-severity patches","patch remediation only occurs for extreme and high risk patches in server environments"),
("2019",31,"3.15","Australia Post","Compensating controls for patch remediation risks were generally insufficient","these other controls found that they were generally not sufficient"),
("2019",31,"3.18","ASC","Regular network-wide password assessments were not performed","ASC and Australia Post did not perform regular assessments of passwords"),
("2019",31,"3.18","Australia Post","Regular network-wide password assessments were not performed","ASC and Australia Post did not perform regular assessments of passwords"),
("2021",44,"2.33","Attorney-General's Department","SIEM review documentation and formal approval were absent","there was no documentation and formal approval of reviews"),
("2021",54,"2.80","Attorney-General's Department","No timeframe for reaching Managing maturity against PSPF Policy 10","AGD has not set a timeframe for achieving"),
("2021",54,"2.80","Attorney-General's Department","No clear strategy for reaching Managing maturity against PSPF Policy 10","AGD has not developed a clear strategy"),
("2021",54,"2.81","Attorney-General's Department","No evidence demonstrating documented processes for maturity improvement","AGD has not provided evidence to demonstrate"),
("2021",54,"2.82","Attorney-General's Department","No independent assurance of compliance with Top Four mitigation strategies","AGD has not had independent assurance of its compliance"),
("2021",54,"2.83","Attorney-General's Department","Committee did not receive security maturity progress reports","does not receive reports"),
("2024",30,"page 30","AUSTRAC","CISO responsibilities were not documented","the assigned responsibilities for its Chief Information Security Officer"),
("2024",30,"page 30","AUSTRAC","Continuous monitoring and improvement-reporting approach not documented","its approach to continuous monitoring and improvement reporting"),
("2024",30,"page 30","AUSTRAC","Stakeholder security-reporting timeframes were not defined","defined timeframes for reporting to stakeholders"),
("2024",30,"page 30","AUSTRAC","Event-log coverage did not conform to cyber security guidance","The coverage of event logs is not in accordance with ASD"),
("2024",30,"page 30","AUSTRAC","Event-logging policy was absent","It does not have an event logging policy"),
("2024",30,"page 30","AUSTRAC","Analysis of all security events was not documented","does not document its analysis of all cyber security"),
("2024",30,"page 30","AUSTRAC","Recovery procedures omitted security and testing of backups","These procedures do not include the security and testing of backup solutions"),
("2024",30,"page 30","AUSTRAC","Recovery procedures did not identify critical supporting systems, applications and servers","nor detail the systems, applications and servers supporting critical business processes"),
("2024",38,"2.16","AUSTRAC","Threat/vulnerability assessment approach not documented","AUSTRAC has not documented its approach to cyber security threat and vulnerability"),
("2024",38,"2.16","AUSTRAC","Critical information and asset registers not established","has not established critical information and asset registers"),
("2024",38,"2.17","AUSTRAC","No documented lifecycle plan to review/update/test security documentation","does not have a documented plan to review"),
("2024",38,"2.21","AUSTRAC","Incident-management procedures were not reviewed, updated or tested","AUSTRAC has not reviewed, updated and tested"),
("2024",38,"2.22","AUSTRAC","No documented triage/response process for monitored security reporting email","there is no documented approach for how triaging and responding is undertaken"),
("2024",38,"2.23","AUSTRAC","No security maturity monitoring plan","AUSTRAC does not have a security maturity monitoring plan"),
("2024",56,"2.86","AUSTRAC","No routine complete disaster-recovery testing of backups and systems","AUSTRAC does not perform complete system disaster testing"),
("2024",56,"2.86","AUSTRAC","No process to extract and analyse archived/production backup data","AUSTRAC does not have a process for extracting and analysing production and archived backup data"),
("2024",56,"2.90","AUSTRAC","Post-incident findings were not used to improve controls or disseminate learning","AUSTRAC does not use these incident reports to design and implement"),
("2026",25,"2.9","Australian Bureau of Statistics","Overlapping strategic and programme cybersecurity risks tracked without synchronized reassessment","Changes in assessments for strategic level risks do not automatically flow through"),
("2026",25,"2.9","Australian Bureau of Statistics","Cyber risk registers omitted essential ratings or proximity dates","Key information that was present in the registers for some cyber security risks was missing for others"),
("2026",25,"2.10","Australian Bureau of Statistics","Risk officer assignment policy did not specify experience/seniority criteria","provides no criteria or guidance on the seniority or specialist expertise"),
("2026",25,"2.11","Australian Bureau of Statistics","Cyber risk owners for PR3 and PR6 not documented","Risk owners for PR3 and PR6 are not documented"),
("2026",25,"2.12","Australian Bureau of Statistics","Timing and content of cyber risk updates not documented in procedures","There are no documented procedures for the timing of updates"),
("2026",26,"2.14","Australian Bureau of Statistics","Medium-rated programme cyber risk PR3 received fewer periodic reassessments than overlapping risks","Updates on PR3 were sought only three times"),
("2026",26,"2.15","Australian Bureau of Statistics","Three requested risk updates lacked documented responses","Three (18 per cent) had no documented response"),
("2026",26,"2.15","Australian Bureau of Statistics","Most risk updates omitted documented cyber security progress","Six (35 per cent) included updates on the cyber security components"),
("2026",26,"2.15","Australian Bureau of Statistics","Risk reporting for oversight committee meetings was stale","they were completed an average of 31 days prior"),
("2026",45,"page 45","Australian Bureau of Statistics","Census cybersecurity planning failed to encompass broader ABS ICT environment","The ABS gave insufficient consideration to holistic cyber security planning"),
("2026",45,"2.99","Australian Bureau of Statistics","Key cybersecurity mitigation controls had not all been implemented","did not implement all key mitigation controls"),
]
FILES={
 "2018":"ANAO_Report_2017-2018_53a.pdf",
 "2019":"Auditor-General_Report_2019-20_1.pdf",
 "2021":"anao-2021-strategies.pdf",
 "2024":"anao-2024-incidents.pdf",
 "2026":"Auditor-General_Report_2025-26_34.pdf",
}
cache={}
rows=[];bad=[]
for y,p,loc,entity,concept,quote in LABELS:
 if y not in cache:cache[y]=read_report(ROOT/"data"/"raw"/FILES[y])
 actual=normalise(cache[y][p-1].text)
 if normalise(quote) not in actual:
  bad.append((y,p,concept,quote))
 rows.append({"label_id":f"R{len(rows)+1:03d}","year":y,"document_id":FILES[y],
    "pdf_page":p,"source_locator":loc,"entity_scope":entity,
    "reference_weakness":concept,"source_quote":quote,
    "status":"source_first_provisional","reviewer":"AI source reading, not professional auditor"})
print("labels",len(rows),"exact_anchor_failures",len(bad))
for b in bad:print("BAD",b)
out=ROOT/"data"/"evaluations"/"independent-reference-selected-pages.json"
out.write_text(json.dumps({"protocol":"Source-first manual AI reading of the 14 selected PDF pages; excludes pure recommendations, generic risk explanations, and duplicates; prior assistant has seen broad predicted output summaries; not blinded.","labels":rows,"invalid_quotes":bad},indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print("output",out)
