"""Interrupt slip after natural blend-out starts, then verify block can activate."""
import unreal,json,traceback
from pathlib import Path
source=Path('A:/K-02 5.8/Tools/Validation/slip_damage_regression.py').read_text();exec(source[:source.rindex('k02_slip_damage_test=Test()')])
class LateInterrupt(Test):
 def next(self):
  if self.i==-1:self.cases=[('late_stop',None)]
  super().next()
 def tick(self,dt):
  try:
   now=unreal.GameplayStatics.get_time_seconds(self.w)
   if now<=self.clock:return
   self.clock=now;t=now-self.start;anim=self.p.mesh.get_anim_instance()
   if t>=.2 and 'start' not in self.sent:
    self.sent.add('start');self.row['activated']=bool(self.asc.try_activate_ability_by_class(self.slip,True));self.montage=anim.get_current_active_montage();self.row['montageConfig']=json.loads(unreal.ToolsetLibrary.get_object_properties(self.montage,['sequenceLength','blendOut','blendOutTriggerTime']));self.length=self.montage.get_play_length();self.blend=self.montage.get_editor_property('blend_out').get_editor_property('blend_time');self.row['interruptAt']=.2+self.length-self.blend/2
   if 'start' in self.sent and t>.3 and anim.get_current_active_montage() is None and 'stop' not in self.sent:self.sent.add('stop');self.row['actualInterruptAt']=t;anim.montage_play(unreal.load_asset('/Game/K02/Protagonist/Slip/Montages/AM_K02_Slip_Forward'))
   if t>=1.5 and 'block' not in self.sent:self.sent.add('block');self.row['blockActivated']=bool(self.asc.try_activate_ability_by_class(unreal.load_class(None,'/Game/K02/Protagonist/Abilities/GA_K02_DefenseMode.GA_K02_DefenseMode_C'),True))
   tags=list(self.ins.call_method('GetActiveTags',args=(self.p,)));self.row['samples'].append({'t':t,'tags':tags,'montage':str(anim.get_current_active_montage())})
   if t>=1.6:
    self.row['pass']=self.row['activated'] and self.row.get('blockActivated',False) and not any(x.endswith('.Dash') for x in tags);self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap));r={'pass':not error and all(x.get('pass') for x in self.rows),'error':error,'rows':self.rows};Path('A:/K-02 5.8/Saved/Diagnostics/LiveBlock/regression.json').write_text(json.dumps(r,indent=2));unreal.log('K02_LATE_SLIP_TEST '+str(r['pass']))
k02_late_slip_test=LateInterrupt()
