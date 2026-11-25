import unreal,json,traceback
from pathlib import Path
class AIObserve:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w
  self.e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character) if a.get_class().get_name()=='BP_K02_Enemy_C');self.p=unreal.GameplayStatics.get_player_pawn(self.w,0)
  self.settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.oldthrottle=self.settings.get_editor_property('bThrottleCPUWhenNotForeground');self.settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.oldcap=unreal.SystemLibrary.get_console_variable_float_value('t.MaxFPS');unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS 60')
  self.before=json.loads(unreal.ToolsetLibrary.get_object_properties(self.e.character_movement,['NavMovementProperties','MaxAcceleration','GroundFriction','BrakingDecelerationWalking']))
  self.t=0;self.rows=[];self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def tick(self,dt):
  try:
   self.t+=unreal.GameplayStatics.get_world_delta_seconds(self.w);a=self.e.mesh.get_anim_instance()
   self.rows.append({'t':self.t,'speed':self.e.get_velocity().length(),'acceleration':self.e.character_movement.get_current_acceleration().length(),'anim':json.loads(unreal.ToolsetLibrary.get_object_properties(a,['GroundSpeed','ShouldMove','Direction']))})
   if self.t>8:self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  unreal.unregister_slate_post_tick_callback(self.cb);self.settings.set_editor_property('bThrottleCPUWhenNotForeground',self.oldthrottle);unreal.SystemLibrary.execute_console_command(self.w,'t.MaxFPS '+str(self.oldcap));r={'movement':self.before,'rows':self.rows,'error':error};Path('A:/K-02 5.8/Saved/Diagnostics/Locomotion/ai-observation.json').write_text(json.dumps(r,indent=2));unreal.log('K02_AI_LOCOMOTION_OBSERVED '+str(error))
k02_ai_observe=AIObserve()
