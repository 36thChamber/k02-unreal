"""Summarize actual guard/slip evidence, without hiding failed cases or missing input."""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[2];folder=root/'Saved/Diagnostics/Integration';name=sys.argv[1];assert name.replace('-','').isalnum();p=folder/(name+'.json');r=json.loads(p.read_text());rows=[]
for x in r['rows']:
 ss=x['samples'];rows.append({k:x[k] for k in ['index','case','pass','heldCheck','releaseCheck','enemyActivated','impactResourceDrop','iframeDuration','slipObserved','attackObserved'] if k in x}|{'duration':ss[-1]['t'] if ss else 0,'resource_start':ss[0]['attributes']['Resource'] if ss else None,'resource_end':ss[-1]['attributes']['Resource'] if ss else None,'resource_min':min((s['attributes']['Resource'] for s in ss),default=None)})
s={'pass':r['pass'],'error':r['error'],'fps':r['fps'],'cases':len(rows),'passed':sum(x['pass'] for x in rows),'continuous_hold_resource_drop':r['continuousHoldResourceDrop'],'native_inputs':len(r['native_inputs']),'native_input_errors':[x for x in r['native_inputs'] if not x['ok']],'duration_seconds':sum(x['duration'] for x in rows),'rows':rows};(folder/(name+'-summary.json')).write_text(json.dumps(s,indent=2));print(json.dumps({k:v for k,v in s.items() if k!='rows'},indent=2))
