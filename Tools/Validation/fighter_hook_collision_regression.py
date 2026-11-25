"""Check the authored hook advance against the existing arena east wall."""
import unreal,json,time
from pathlib import Path
class HookWallTest:
 def __init__(self):
  w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert w
  self.p=unreal.GameplayStatics.get_player_pawn(w,0)
  for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Pawn):
   if a==self.p:continue
   c=a.get_controller()
   if c:
    c.stop_movement();brain=c.get_editor_property('BrainComponent')
    if brain:brain.stop_logic('Hook collision regression')
  self.p.set_actor_location_and_rotation(unreal.Vector(1430,0,92),unreal.Rotator(pitch=0,yaw=0,roll=0),False,True)
  self.p.character_movement.stop_movement_immediately();self.p.mesh.set_editor_property('VisibilityBasedAnimTickOption',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
  self.settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'));self.old=self.settings.get_editor_property('bThrottleCPUWhenNotForeground');self.settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.asc=unreal.get_default_object(unreal.load_class(None,'/Script/GameplayAbilities.AbilitySystemBlueprintLibrary')).call_method('GetAbilitySystemComponent',args=(self.p,))
  assert self.asc.try_activate_ability_by_class(unreal.load_class(None,'/Game/MACS/GAS/Abilities/Fighter/GA_MACS_Fighter_Combo_1_3.GA_MACS_Fighter_Combo_1_3_C'),True)
  self.start=time.perf_counter();self.max_x=1430;self.samples=0;self.handle=None
 def tick(self,dt):
  self.max_x=max(self.max_x,self.p.get_actor_location().x);self.samples+=1
  if time.perf_counter()-self.start<1.2:return
  unreal.unregister_slate_post_tick_callback(self.handle);self.settings.set_editor_property('bThrottleCPUWhenNotForeground',self.old)
  radius=self.p.capsule_component.get_scaled_capsule_radius();limit=1500-radius
  r={'status':'pass' if 1435<self.max_x<=limit+.1 else 'fail','initial_x':1430,'max_x':self.max_x,'wall_inner_x':1500,'capsule_radius':radius,'max_allowed_center_x':limit,'samples':self.samples}
  Path('A:/K-02 5.8/Saved/Diagnostics/fighter-hook-wall-results.json').write_text(json.dumps(r,indent=2));unreal.log('K02_HOOK_WALL '+json.dumps(r))
_k02_hook_wall=HookWallTest();_k02_hook_wall.handle=unreal.register_slate_post_tick_callback(_k02_hook_wall.tick)
