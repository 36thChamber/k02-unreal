"""A paused-camera preference must update the saved free distance, not overwrite lock framing."""
import unreal,json,time,traceback
from pathlib import Path
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
D=Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration';pc=unreal.GameplayStatics.get_player_controller(W,0);p=unreal.GameplayStatics.get_player_pawn(W,0);arm=p.get_components_by_class(unreal.SpringArmComponent)[0];cam=p.get_components_by_class(unreal.CameraComponent)[0]
pc.call_method('K02ResetComfortPreferences');chars=unreal.GameplayStatics.get_all_actors_of_class(W,unreal.Character);target=next(a for a in chars if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
for a in chars:
 a.character_movement.stop_movement_immediately();a.character_movement.set_movement_mode(unreal.MovementMode.MOVE_NONE)
 if a!=p:
  c=a.get_controller();c.stop_movement();brain=c.get_editor_property('BrainComponent')
  if brain:brain.stop_logic('Settings during lock test')
  a.set_actor_location(unreal.Vector(5000,5000,92),False,True)
p.set_actor_location(unreal.Vector(0,0,92),False,True);target.set_actor_location(unreal.Vector(180,0,92),False,True);pc.set_control_rotation(unreal.Rotator(yaw=0,pitch=0));pc.call_method('LockOnTargetMode')
class Test:
 def __init__(self):self.start=time.monotonic();self.done=set();self.checks={};self.rows=[];self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def tick(self,dt):
  try:
   t=time.monotonic()-self.start
   if t>1 and 'change' not in self.done:
    self.done.add('change');self.before=arm.target_arm_length;self.checks['locked_before']=pc.get_editor_property('K02CameraLocked') and pc.get_editor_property('CurrentTarget')==target
    pc.call_method('K02ShowTrainingMenu');pc.call_method('K02CycleCameraDistance');pc.call_method('K02CycleCameraFOV');self.rows.append({'stage':'paused_change','arm':arm.target_arm_length,'saved_arm':pc.get_editor_property('K02SavedArm'),'fov':cam.field_of_view});self.checks['paused_change']=unreal.GameplayStatics.is_game_paused(W) and abs(arm.target_arm_length-self.before)<.01 and pc.get_editor_property('K02SavedArm')==240 and cam.field_of_view==95;pc.call_method('K02CloseTrainingMenu')
   if t>2 and 'unlock' not in self.done:
    self.done.add('unlock');self.checks['framing_retained']=pc.get_editor_property('K02CameraLocked') and arm.target_arm_length>300 and pc.get_editor_property('CurrentTarget')==target;pc.call_method('LockOnTargetMode')
   if t>3:
    self.rows.append({'stage':'after_unlock','arm':arm.target_arm_length,'fov':cam.field_of_view,'look_ignored':pc.is_look_input_ignored()});self.checks['restored']=not pc.get_editor_property('K02CameraLocked') and arm.target_arm_length==240 and cam.field_of_view==95 and not pc.is_look_input_ignored();self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  unreal.unregister_slate_post_tick_callback(self.handle);pc.call_method('K02ResetComfortPreferences');r={'pass':not error and len(self.checks)==4 and all(self.checks.values()),'error':error,'checks':self.checks,'rows':self.rows};(D/'camera-settings-during-lock-v1.json').write_text(json.dumps(r,indent=2));print('CAMERA_SETTINGS_DURING_LOCK',r['pass'])
test=Test()
