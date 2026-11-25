"""Repeated real Ctrl, long holds, block impacts and slip recovery in one PIE session."""
from pathlib import Path
import unreal,json,traceback
source=Path('A:/K-02 5.8/Tools/Validation/combat_slip_input_regression.py').read_text();exec(source[:source.rindex('k02_slip_input_test=Test()')])
class GuardLifetime(Test):
 def next(self):
  if self.i==-1:self.cases=['long_locked']+['repeat_locked','hit_locked','slip_locked','attack_locked']*8+['recover_locked','retry_locked']
  super().next()
  if self.i<len(self.cases):self.row['index']=self.i
 def tick(self,dt):
  try:
   now=unreal.GameplayStatics.get_time_seconds(self.w)
   if now<=self.clock:return
   self.clock=now;t=now-self.start;end=13 if self.name=='long_locked' else (12 if self.name=='recover_locked' else 3)
   def once(label,when,fn):
    if t>=when and label not in self.sent:self.sent.add(label);fn()
   if self.name!='recover_locked':once('ctrl',.2,lambda:self.key('Ctrl',True))
   if self.name=='slip_locked':
    once('dir',.5,lambda:self.key('A',True));once('dirup',.8,lambda:self.key('A',False))
   if self.name=='hit_locked':
    def hit():
     self.target.set_actor_location(unreal.Vector(-390,-400,100),False,True)
     asc=self.lib.call_method('GetAbilitySystemComponent',args=(self.target,));self.row['enemyActivated']=bool(asc.try_activate_ability_by_class(unreal.load_class(None,'/Game/MACS/GAS/Abilities/Fighter/GA_MACS_Fighter_Combo_1_1.GA_MACS_Fighter_Combo_1_1_C'),True))
    once('hit',.8,hit)
   once('up',end-.8,lambda:self.key('Ctrl',False))
   if self.name=='attack_locked':
    def attack():self.row['attackActivated']=bool(self.asc.try_activate_ability_by_class(unreal.load_class(None,'/Game/K02/Protagonist/Abilities/GA_K02_Combo_1_1.GA_K02_Combo_1_1_C'),True))
    once('attack',end-.65,attack)
   montage=self.p.mesh.get_anim_instance().get_current_active_montage();tags=list(self.ins.call_method('GetActiveTags',args=(self.p,)));attrs={v.get_editor_property('AttributeName'):v.get_editor_property('CurrentValue') for v in self.ins.call_method('GetAttributeValues',args=(self.p,))}
   self.row['samples'].append({'t':t,'ctrl':self.pc.is_input_key_down(self.makekey('LeftControl')),'montage':montage.get_name() if montage else None,'tags':tags,'attributes':attrs})
   if t>=end:
    held=[s for s in self.row['samples'] if end-1.0<s['t']<end-.85];self.row['heldCheck']=bool(held) and all(s['ctrl'] and any(t.endswith('.DefenseMode') for t in s['tags']) and 'BlockHold_' in (s['montage'] or '') for s in held)
    self.row['releaseCheck']=not any(t.endswith('.DefenseMode') for t in tags);self.row['pass']=self.row['releaseCheck'] and (self.row['heldCheck'] or self.name=='recover_locked');Path('A:/K-02 5.8/Saved/Diagnostics/GuardLifetime/progress.json').write_text(json.dumps({'index':self.i,'case':self.name,'pass':self.row['pass'],'attributes':attrs,'tags':tags}));self.next()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  for k in list(self.held):self.key(k,False)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap))
  hold=[s['attributes']['Resource'] for s in self.rows[0]['samples'] if .5<s['t']<12] if self.rows else []
  drop=hold[0]-hold[-1] if hold else 999
  result={'pass':not error and len(self.rows)==len(self.cases) and all(r.get('pass') for r in self.rows) and drop<.2,'continuousHoldResourceDrop':drop,'error':error,'rows':self.rows};Path('A:/K-02 5.8/Saved/Diagnostics/GuardLifetime/soak.json').write_text(json.dumps(result,indent=2));unreal.log('K02_GUARD_SOAK '+str(result['pass']))
k02_guard_lifetime=GuardLifetime()
