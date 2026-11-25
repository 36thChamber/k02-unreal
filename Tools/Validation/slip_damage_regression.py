"""Real incoming MACS trace/damage before, during and after the slip immunity interval."""
import unreal,json,traceback
from pathlib import Path
class Test:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();self.p=unreal.GameplayStatics.get_player_pawn(self.w,0)
  self.e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a not in [self.p,self.e]:a.destroy_actor()
  self.lib=unreal.get_default_object(unreal.load_class(None,'/Script/GameplayAbilities.AbilitySystemBlueprintLibrary'));self.asc=self.lib.call_method('GetAbilitySystemComponent',args=(self.p,));self.enemyasc=self.lib.call_method('GetAbilitySystemComponent',args=(self.e,));self.ins=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'))
  self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False);self.cap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS 60')
  self.slip=unreal.load_class(None,'/Game/K02/Protagonist/Abilities/GA_K02_Slip.GA_K02_Slip_C');self.attack=unreal.load_class(None,'/Game/MACS/GAS/Abilities/Fighter/GA_MACS_Fighter_Combo_1_1.GA_MACS_Fighter_Combo_1_1_C');self.ge=unreal.load_class(None,'/Game/K02/Protagonist/Slip/GE_K02_SlipIFrames.GE_K02_SlipIFrames_C')
  self.cases=[('unguarded',None),('timed',.45),('early',.2),('late',.65),('cancel',.3)];self.rows=[];self.i=-1;self.clock=unreal.GameplayStatics.get_time_seconds(self.w);self.next();self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def health(self):return sum(v.get_editor_property('CurrentValue') for v in self.ins.call_method('GetAttributeValues',args=(self.p,)) if v.get_editor_property('AttributeName') in ['Health','Shield'])
 def next(self):
  self.i+=1
  if self.i>=len(self.cases):self.finish();return
  self.name,self.delay=self.cases[self.i];self.start=self.clock;self.sent=set();self.p.character_movement.stop_movement_immediately();self.e.character_movement.stop_movement_immediately()
  self.p.set_actor_location_and_rotation(unreal.Vector(-500,-400,100),unreal.Rotator(),False,True);self.e.set_actor_location_and_rotation(unreal.Vector(-390,-400,100),unreal.Rotator(pitch=0,yaw=180,roll=0),False,True)
  self.row={'case':self.name,'before':self.health(),'minimum':self.health(),'samples':[]};self.rows.append(self.row)
 def tick(self,dt):
  try:
   now=unreal.GameplayStatics.get_time_seconds(self.w)
   if now<=self.clock:return
   self.clock=now;t=now-self.start
   if self.name!='cancel' and t>=.3 and 'attack' not in self.sent:self.sent.add('attack');self.row['attackActivated']=bool(self.enemyasc.try_activate_ability_by_class(self.attack,True))
   if self.delay is not None and t>=self.delay and 'slip' not in self.sent:self.sent.add('slip');self.row['slipActivated']=bool(self.asc.try_activate_ability_by_class(self.slip,True))
   if self.name=='cancel' and t>=.4 and 'cancel' not in self.sent:self.sent.add('cancel');self.p.mesh.get_anim_instance().montage_stop(.02)
   self.row['minimum']=min(self.row['minimum'],self.health());m=self.p.mesh.get_anim_instance().get_current_active_montage();tags=list(self.ins.call_method('GetActiveTags',args=(self.p,)))
   self.row['samples'].append({'t':t,'health':self.health(),'iframes':self.asc.call_method('GetGameplayEffectCount',args=(self.ge,None,True)),'montage':m.get_name() if m else None,'tags':tags})
   if t>=2:
    self.row['damage']=self.row['before']-self.row['minimum'];self.row['ended']=self.row['samples'][-1]['iframes']==0 and not any('Fighter.Dash' in x for x in tags)
    if self.name=='timed':ok=self.row.get('slipActivated') and self.row['damage']<.01 and any(x['iframes'] for x in self.row['samples'])
    elif self.name=='cancel':ok=self.row.get('slipActivated') and all(x['iframes']==0 for x in self.row['samples'] if x['t']>.5)
    else:ok=self.row.get('attackActivated') and self.row['damage']>.1
    self.row['pass']=bool(ok and self.row['ended']);self.next()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap));r={'pass':not error and len(self.rows)==len(self.cases) and all(x.get('pass') for x in self.rows),'error':error,'rows':self.rows};Path('A:/K-02 5.8/Saved/Diagnostics/CombatSlip/damage-test.json').write_text(json.dumps(r,indent=2));unreal.log('K02_SLIP_DAMAGE_TEST '+str(r['pass'])+' '+str(error))
k02_slip_damage_test=Test()
