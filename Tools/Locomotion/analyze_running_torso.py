"""Offline before/after runtime torso and stride summary."""
import json,math,sys
from pathlib import Path
P=Path(__file__).resolve().parents[2];D=P/'Saved/Diagnostics/RunningTorso'
def unwrapped_range(values):
 out=[values[0]]
 for a,b in zip(values,values[1:]):out.append(out[-1]+(b-a+180)%360-180)
 return max(out)-min(out)
r={}
for phase in ['torso-before','torso-after','torso-final']:
 data=json.loads((P/'Saved/Diagnostics/Locomotion'/('runtime-'+phase+'.json')).read_text());rows=[]
 for row in data['rows']:
  ss=[s for s in row['samples'] if .9<s['t']<1.5];body={}
  for bone in ['spine_03','spine_05','hand_l','hand_r']:
   body[bone]={'rotationRangesDegrees':[unwrapped_range([s['body'][bone]['r'][i] for s in ss]) for i in range(3)],'relativePositionRangesCM':[max(s['body'][bone]['p'][i]-s['feet']['pelvis'][i] for s in ss)-min(s['body'][bone]['p'][i]-s['feet']['pelvis'][i] for s in ss) for i in range(3)]}
  rows.append({'case':row['case']['name'],'body':body,'samples':len(ss)})
 r[phase]=rows
(D/'comparison.json').write_text(json.dumps(r,indent=2))
for phase,rows in r.items():
 print(phase)
 for row in rows:
  if row['case'] in ['steady_250_0','steady_550_0','steady_650_0']:print(row['case'],'spine03',row['body']['spine_03']['rotationRangesDegrees'],'leftHandXYZ',row['body']['hand_l']['relativePositionRangesCM'])
