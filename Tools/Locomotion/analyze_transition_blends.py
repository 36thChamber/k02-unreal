import json,math,statistics,sys
from pathlib import Path
D=Path(sys.argv[1] if len(sys.argv)>1 else '/mnt/a/K-02 5.8/Saved/Diagnostics/TransitionBlends')
def analyze(phase):
 x=json.loads((D/('runtime-'+phase+'.json')).read_text());rows=[]
 for row in x['rows']:
  samples=row['samples'];events=[];speeds=[];edge=[]
  for i,s in enumerate(samples):
   if not i:continue
   a=samples[i-1];dt=s['t']-a['t']
   if dt<=0:continue
   if (s['montage'],s['moving'],s['combat'])!=(a['montage'],a['moving'],a['combat']):events.append(s['t'])
   val=statistics.mean(math.dist(s['bones'][b],a['bones'][b])/dt for b in ['spine_05','head','hand_l','hand_r']);speeds.append((s['t'],val))
  for t,v in speeds:
   if any(0<=t-e<=.15 for e in events):edge.append(v)
  positive=[s['montagePosition']-a['montagePosition'] for a,s in zip(samples,samples[1:]) if s['montage'] and s['montage']==a['montage'] and s['montagePosition']>=a['montagePosition']]
  loops=sum(s['montagePosition']<a['montagePosition']-.1 for a,s in zip(samples,samples[1:]) if s['montage'] and s['montage']==a['montage'])
  rowdata={'case':row['case'],'events':events,'boundarySpeedP95_cm_s':sorted(edge)[max(0,int(.95*(len(edge)-1)))] if edge else None,'boundarySpeedMax_cm_s':max(edge,default=0),'guardLoopWraps':loops,'activated':row.get('activated')};rows.append(rowdata)
 return {'error':x['error'],'rows':rows,'note':'Mean upper-body bone speed in actor-local space within 150ms after state/montage changes. Diagnostic proxy, includes intentional strike motion; not a visual smoothness score.'}
r={p:analyze(p) for p in ['before','after']};(D/'comparison.json').write_text(json.dumps(r,indent=2));
for a,b in zip(r['before']['rows'],r['after']['rows']):print(a['case'],round(a['boundarySpeedP95_cm_s'] or 0,1),'->',round(b['boundarySpeedP95_cm_s'] or 0,1),'max',round(a['boundarySpeedMax_cm_s'],1),'->',round(b['boundarySpeedMax_cm_s'],1))
