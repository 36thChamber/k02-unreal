"""Real Ctrl input: stance -> held block -> stance, and preserved Ctrl+direction slip."""
from pathlib import Path
import json,unreal
source=Path('A:/K-02 5.8/Tools/Validation/combat_slip_input_regression.py').read_text()
exec(source[:source.rindex('k02_slip_input_test=Test()')])
class StanceBlockTest(Test):
 def next(self):
  if self.i==-1:self.cases=['block_free','block_locked','slip_A']
  super().next()
 def tick(self,dt):
  if self.i>=len(self.cases):return
  t=unreal.GameplayStatics.get_time_seconds(self.w)-self.start
  if self.name=='block_locked':
   for stamp,label in [(.8,'block'),(1.65,'stance')]:
    mark='capture_'+label
    if t>=stamp and mark not in self.sent:
     self.sent.add(mark);unreal.SystemLibrary.execute_console_command(self.w,'HighResShot 1280x720 filename="A:/K-02 5.8/Saved/Diagnostics/StanceBlock/'+label+'.png"',self.pc)
  super().tick(dt)
 def finish(self,error=None):
  super().finish(error)
  checks={}
  for row in self.rows:
   if not row['case'].startswith('block'):continue
   samples=row['samples'];held=[s for s in samples if .6<s['t']<1.0];released=[s for s in samples if s['t']>1.6]
   checks[row['case']]=bool(held and released and all('BlockHold_' in (s['montage'] or '') for s in held) and all(s['montage'] is None and not any(t.endswith('.DefenseMode') for t in s['tags']) for s in released))
  result={'pass':not error and len(self.rows)==3 and all(r.get('pass') for r in self.rows) and all(checks.values()),'checks':checks,'error':error,'rows':self.rows};Path('A:/K-02 5.8/Saved/Diagnostics/StanceBlock/input.json').write_text(json.dumps(result,indent=2));unreal.log('K02_STANCE_BLOCK_TEST '+str(result['pass']))
k02_stance_block_test=StanceBlockTest()
