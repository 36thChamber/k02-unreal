"""Offline metrics. Low-foot planar speed is a contact proxy, not a contact solver."""
import json,math,statistics,sys
from pathlib import Path
D=Path(__file__).resolve().parents[2]/'Saved/Diagnostics/Locomotion'
def analyze(phase):
 data=json.loads((D/('runtime-'+phase+'.json')).read_text());out=[]
 for row in data['rows']:
  s=row['samples'];lo,hi=(1.2,1.8) if row['case']['name']=='sprint_1000' else (.9,1.5);steady=[x for x in s if lo<x['t']<hi];speeds=[math.hypot(*x['velocity'][:2]) for x in steady];slips=[]
  minima={b:min(x['feet'][b][2] for x in steady) for b in ['foot_l','foot_r']}
  for a,b in zip(steady,steady[1:]):
   dt=b['t']-a['t']
   if dt<=0:continue
   for bone in ['foot_l','foot_r']:
    p=a['feet'][bone];q=b['feet'][bone]
    if max(p[2],q[2])<minima[bone]+3 and abs(q[2]-p[2])/dt<40:slips.append(math.hypot(q[0]-p[0],q[1]-p[1])/dt)
  stop=[x for x in s if x['t']>=3];release=stop[0];stopped=next((x for x in stop if math.hypot(*x['velocity'][:2])<1),stop[-1]);earlyIdle=[x for x in stop if math.hypot(*x['velocity'][:2])>20 and not x['anim'].get('ShouldMove',False)]
  directionRates=[]
  for a,b in zip(s,s[1:]):
   if 1.55<a['t']<2.0:
    va,vb=a['velocity'],b['velocity']
    if min(math.hypot(*va[:2]),math.hypot(*vb[:2]))>30:directionRates.append(abs((math.degrees(math.atan2(vb[1],vb[0])-math.atan2(va[1],va[0]))+180)%360-180)/(b['t']-a['t']))
  out.append({'case':row['case']['name'],'meanSpeed':statistics.mean(speeds),'lowFootSpeedMedian':statistics.median(slips) if slips else None,'contactProxySamples':len(slips),'brakingToRestSeconds':stopped['t']-release['t'],'brakingDistance':math.dist(stopped['position'][:2],release['position'][:2]),'idleWhileStillMovingFrames':len(earlyIdle),'maxVelocityDirectionRate':max(directionRates,default=0),'finalSpeed':math.hypot(*s[-1]['velocity'][:2])})
 result={'phase':phase,'error':data['error'],'metrics':out,'note':'Median XY speed of feet within 3cm of each foot low point and |vertical speed|<40cm/s, steady .9–1.5s (1.2–1.8s for sprint_1000 to exclude acceleration). Proxy, not guaranteed planted contact.'};(D/('metrics-'+phase+'.json')).write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(json.dumps(analyze(sys.argv[1]),indent=2))
