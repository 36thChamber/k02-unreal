"""Separate rendered running preview. Never use this capture run for timing assertions."""
import unreal,json,traceback
from pathlib import Path
class PreviewForwardRun:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert self.w
  self.p=unreal.GameplayStatics.get_player_pawn(self.w,0);self.pc=unreal.GameplayStatics.get_player_controller(self.w,0);self.arm=self.p.get_components_by_class(unreal.SpringArmComponent)[0]
  for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Character):
   if a!=self.p:a.destroy_actor()
  self.tr=self.p.get_actor_transform();self.rot=self.pc.get_control_rotation();self.length=self.arm.target_arm_length;self.speed=self.p.character_movement.max_walk_speed
  self.settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.settings.get_editor_property('bThrottleCPUWhenNotForeground');self.settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.arm.target_arm_length=500;self.pc.set_control_rotation(unreal.Rotator(pitch=-12,yaw=0,roll=0));self.p.set_actor_location_and_rotation(unreal.Vector(-800,-500,100),unreal.Rotator(pitch=0,yaw=0,roll=0),False,True);self.p.character_movement.max_walk_speed=600
  self.t=0;self.shot=False;self.cb=unreal.register_slate_post_tick_callback(self.tick)
 def tick(self,dt):
  try:
   self.t+=unreal.GameplayStatics.get_world_delta_seconds(self.w)
   if self.t<2.0:self.p.add_movement_input(unreal.Vector(1,0,0),1,True)
   if self.t>.85 and not self.shot:
    self.shot=True;unreal.AutomationLibrary.take_high_res_screenshot(1280,720,'A:/K-02 5.8/Saved/Diagnostics/RunningTorso/forward-running-preview.png')
   if self.t>3.5:self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  unreal.unregister_slate_post_tick_callback(self.cb);self.settings.set_editor_property('bThrottleCPUWhenNotForeground',self.old);self.arm.target_arm_length=self.length;self.pc.set_control_rotation(self.rot);self.p.set_actor_transform(self.tr,False,True);self.p.character_movement.max_walk_speed=self.speed;unreal.log('K02_FORWARD_RUN_PREVIEW_DONE '+str(error))
k02_forward_preview=PreviewForwardRun()
