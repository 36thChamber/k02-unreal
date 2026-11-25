"""Observe the existing AI tree using the protagonist effect, montages and animation graph."""
import unreal,json,traceback
from pathlib import Path
class Test:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character) if a.get_class().get_name()=='BP_K02_Enemy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a not in [self.p,self.e]:a.destroy_actor()
  self.ins=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'));self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.cap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS 60')
  self.p.set_actor_location_and_rotation(unreal.Vector(-100,450,100),unreal.Rotator(),False,True);self.e.set_actor_location_and_rotation(unreal.Vector(300,450,100),unreal.Rotator(pitch=0,yaw=180,roll=0),False,True);self.before=self.health();self.minimum=self.before;self.start=unreal.GameplayStatics.get_time_seconds(self.w);self.rows=[];self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def health(self):return sum(v.get_editor_property('CurrentValue') for v in self.ins.call_method('GetAttributeValues',args=(self.p,)) if v.get_editor_property('AttributeName') in ['Health','Shield'])
 def tick(self,dt):
  try:
   t=unreal.GameplayStatics.get_time_seconds(self.w)-self.start;self.minimum=min(self.minimum,self.health());m=self.e.mesh.get_anim_instance().get_current_active_montage();self.rows.append({'t':t,'distance':self.e.get_actor_location().distance(self.p.get_actor_location()),'speed':self.e.get_velocity().length(),'montage':m.get_name() if m else None,'playerHealth':self.health()})
   if t>=14:self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap))
  names=[a.get_editor_property('AbilityName') for a in self.ins.call_method('GetGrantedAbilities',args=(self.e,))];moves=sorted(set(x['montage'] for x in self.rows if x['montage']));anim=self.e.mesh.get_anim_instance().get_class().get_name();damage=self.before-self.minimum
  r={'pass':not error and anim=='ABP_K02_Player_C' and any('GA_K02_Combo_1_1' in n for n in names) and not any('GA_MACS_Fighter_Combo' in n for n in names) and any('AM_K02_Kyokushin_' in m for m in moves) and damage>0,'error':error,'animClass':anim,'abilities':names,'montages':moves,'playerDamage':damage,'samples':self.rows};Path('A:/K-02 5.8/Saved/Diagnostics/CombatSlip/ai-test.json').write_text(json.dumps(r,indent=2));unreal.log('K02_SHARED_AI_TEST '+str(r['pass'])+' '+str(error))
k02_shared_ai_test=Test()
