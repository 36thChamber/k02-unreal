"""Rendered visual evidence, isolated from timing regressions."""
import unreal,json,traceback
from pathlib import Path
D=Path('A:/K-02 5.8/Saved/Diagnostics/LockRecovery')
class Preview:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.m=self.p.character_movement
  self.target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a not in [self.p,self.target]:a.destroy_actor()
  self.perf=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.perf.get_editor_property('bThrottleCPUWhenNotForeground');self.perf.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.cap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS 60');self.arm=self.p.get_components_by_class(unreal.SpringArmComponent)[0];self.arm.target_arm_length=430
  self.commun=next(o for o in unreal.ObjectIterator(unreal.AnimInstance) if o.get_outer()==self.p.mesh and o.get_class().get_name()=='ABP_K02_Commun_C')
  self.rows=[];self.i=-1;self.cases=[('free_run',False,650,unreal.Vector(1,0,0)),('free_diagonal',False,650,unreal.Vector(.707,.707,0)),('lock_diagonal',True,250,unreal.Vector(.707,.707,0)),('free_idle',False,0,unreal.Vector())];self.next();self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def next(self):
  self.i+=1;self.t=0;self.shot=False
  if self.i>=len(self.cases):self.finish();return
  self.name,lock,speed,self.direction=self.cases[self.i];self.m.max_walk_speed=speed;self.m.stop_movement_immediately();self.p.set_actor_location_and_rotation(unreal.Vector(-800,-500,100),unreal.Rotator(),False,True);self.target.set_actor_location(unreal.Vector(-50,-500,100),False,True);self.pc.set_control_rotation(unreal.Rotator(pitch=-12,yaw=0,roll=0))
  for _ in range(4):
   mode=json.loads(unreal.ToolsetLibrary.get_object_properties(self.pc,['LockonMode']))['LockonMode']
   if mode==(1 if lock else 0):break
   self.pc.call_method('LockOnTargetMode')
 def tick(self,dt):
  try:
   self.t+=unreal.GameplayStatics.get_world_delta_seconds(self.w)
   if self.t<1.5 and self.direction.length()>0:self.p.add_movement_input(self.direction,1,True)
   if self.t>1 and not self.shot:
    self.shot=True;self.rows.append({'case':self.name,'combatStance':self.commun.get_editor_property('K02CombatStance'),'yaw':self.p.get_actor_rotation().yaw,'speed':self.p.get_velocity().length(),'head':self.p.mesh.get_socket_rotation('head').to_tuple(),'spine':self.p.mesh.get_socket_rotation('spine_05').to_tuple()});unreal.AutomationLibrary.take_high_res_screenshot(1280,720,str(D/(self.name+'.png')))
   if self.t>2.3:self.next()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  if hasattr(self,'cb'):unreal.unregister_slate_post_tick_callback(self.cb)
  self.perf.set_editor_property('bThrottleCPUWhenNotForeground',self.old);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.cap));(D/'visual-stance.json').write_text(json.dumps({'error':error,'rows':self.rows},indent=2));unreal.log('K02_VISUAL_STANCE_DONE '+str(error))
k02_stance_preview=Preview()
