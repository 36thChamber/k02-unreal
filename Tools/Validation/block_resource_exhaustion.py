"""Verify that the held-cost fix still respects exhausted stamina and recovers after rest."""
from pathlib import Path
import unreal,json,traceback
source=Path('A:/K-02 5.8/Tools/Validation/combat_slip_input_regression.py').read_text();exec(source[:source.rindex('k02_slip_input_test=Test()')])
class ResourceTest(Test):
 def next(self):
  if self.i==-1:self.cases=['resource_locked']
  super().next()
 def tick(self,dt):
  try:
   t=unreal.GameplayStatics.get_time_seconds(self.w)-self.start
   def once(label,when,fn):
    if t>=when and label not in self.sent:self.sent.add(label);fn()
   once('press',.2,lambda:self.key('Ctrl',True))
   def exhaust():
    cls=unreal.load_class(None,'/Game/MACS/GAS/Effects/AbilityCosts/GE_MACS_Base_Cost_DefenseMode.GE_MACS_Base_Cost_DefenseMode_C');ctx=self.asc.make_effect_context()
    for _ in range(1002):self.asc.call_method('BP_ApplyGameplayEffectToSelf',args=(cls,1,ctx))
   once('exhaust',.8,exhaust)
   once('release',1.2,lambda:self.key('Ctrl',False));once('retry',3.5,lambda:self.key('Ctrl',True));once('releaseAgain',4.5,lambda:self.key('Ctrl',False))
   attrs={v.get_editor_property('AttributeName'):v.get_editor_property('CurrentValue') for v in self.ins.call_method('GetAttributeValues',args=(self.p,))};tags=list(self.ins.call_method('GetActiveTags',args=(self.p,)));m=self.p.mesh.get_anim_instance().get_current_active_montage();self.row['samples'].append({'t':t,'resource':attrs['Resource'],'guard':any(tag.endswith('.DefenseMode') for tag in tags),'montage':m.get_name() if m else None})
   if t>=5:self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  for k in list(self.held):self.key(k,False)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap))
  ss=self.row['samples'];checks={'started':any(.4<s['t']<.7 and s['guard'] for s in ss),'exhaustedEndsGuard':any(1<s['t']<1.2 and s['resource']<.1 and not s['guard'] for s in ss),'regenerated':any(3<s['t']<3.4 and s['resource']>1 for s in ss),'blockReturns':any(4<s['t']<4.4 and s['guard'] and 'BlockHold_' in (s['montage'] or '') for s in ss),'released':bool(ss and not ss[-1]['guard'])}
  result={'pass':not error and all(checks.values()),'checks':checks,'error':error,'testOnlyResourceDrain':'1002 applications of the existing native 0.1 Resource cost; no health or asset edits','samples':ss};Path('A:/K-02 5.8/Saved/Diagnostics/GuardLifetime/exhaustion.json').write_text(json.dumps(result,indent=2));unreal.log('K02_BLOCK_RESOURCE_EDGE '+str(result['pass'])+' '+str(error))
k02_block_resource=ResourceTest()
