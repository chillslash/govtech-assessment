from pathlib import Path
import json
from collections import Counter
root=Path(__file__).resolve().parents[1]
ev=root/'data'/'evaluations'
years=['2018','2019','2021','2024','2026']
read=lambda p:json.loads(p.read_text(encoding='utf8'))
reports={y:read(ev/f'anao-full-{y}.json') for y in years}
assess={y:read(ev/f'anao-full-eval-{y}.json') for y in years}
theme=read(ev/'anao-full-themes.json')
held=read(ev/'independent-discovery-holdout.json')
cl={(a['report'],a['pdf_page']):a['classification'] for a in held['reviews']}
exceptions={('2019',40):('detected','Reference positive, prediction matches ASC data ownership; original assessor inconsistently called scope uncertain.'),
 ('2026',33):('not_applicable','Original reference contains no observed failure; absence is appropriate.')}
per=[]
holdouts=[]
for y in years:
 p=reports[y]; e=assess[y]
 assert p['status']=='complete'
 counts=Counter(r['verdict'] for r in e['references'])
 per.append({'year':y,'screened':len(p['all_screened_pages']),'nominated':len(p['selected_pages']),
  'verified':len(p['source_verified']),'rejected':len(p['rejected']),
  'invalid_discovery_quotes':sum(len(b.get('rejected',[])) for b in p['discovery_batches']),
  'ref_total':len(e['references']),'clear':counts['clear'],'merged':counts['merged'],
  'attribution_uncertain':counts['attribution_uncertain'],'absent':counts['absent']})
 for h in e['holdouts']:
  v,r=exceptions.get((y,h['pdf_page']),(h['verdict'],None))
  holdouts.append({'year':y,'pdf_page':h['pdf_page'],
   'source_classification':cl[y,h['pdf_page']],
   'original_assessor_verdict':h['verdict'],'reviewed_verdict':v,
   'record_ids':h['matched_record_ids'],'correction_explanation':r})
pos=[x for x in holdouts if x['source_classification']=='positive']
tot={k:sum(p[k] for p in per) for k in ('screened','nominated','verified','rejected',
 'invalid_discovery_quotes','ref_total','clear','merged','attribution_uncertain','absent')}
summary={'protocol':'All physical pages in pre-inspected substantive findings bounds LLM-screened; extraction of nominated pages; source/locator checks; frozen source-first reference matching.',
 'per_report':per,'totals':tot,'holdouts':holdouts,
 'positive_holdout_outcomes':dict(Counter(x['reviewed_verdict'] for x in pos)),
 'theme_proposals':[{'name':t['name'],'report_count':t['report_count'],
 'agency_count':t['agency_count'],'finding_ids':t['finding_ids']} for t in theme['themes']],
 'previous_mvp':{'verified_records':50,'extracted_pages':14,'reference_concepts':58,
 'supported_atomic_records':40,'source_concepts_covered_clear_or_merged':44},
 'cautions':['Neither page screening nor source quotes guarantee semantic recall or correctness.',
 'Evaluation uses frozen AI-created references and an unblinded AI assessor, not auditor ground truth.',
 'The selected-page matched-concept result is not a full-report recall estimate.',
 'Two holdout judge inconsistencies are transparently corrected without rewriting its raw output.',
 'Cross-report themes are unapproved semantic proposals, not independently validated.',
 'The corpus comprises Australian ANAO rather than Singapore AGO reports.']}
(ev/'anao-full-evaluation-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps({'totals':tot,'positive_holdouts':summary['positive_holdout_outcomes'],
'theme_proposals':[x['name'] for x in summary['theme_proposals']]},indent=2))

