"""Observe the arena enemy with the player inside perception range."""
import unreal,json,time
from pathlib import Path
class EnemyObservation:
 def __init__(self):
  self.w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
  self.p=unreal.GameplayStatics.get_player_pawn(self.w,0)
  self.e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Pawn) if a.get_class().get_name()=='BP_K02_Enemy_C')
  self.p.set_actor_location(unreal.Vector(250,450,92),False,True)
  self.e.set_actor_rotation(unreal.Rotator(pitch=0,yaw=180,roll=0),False)
  self.ins=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'))
  self.settings=unreal.get_default_object(unreal.load_class(None,'/Script/UnrealEd.EditorPerformanceSettings'))
  self.old=self.settings.get_editor_property('bThrottleCPUWhenNotForeground');self.settings.set_editor_property('bThrottleCPUWhenNotForeground',False)
  self.start=self.e.get_actor_location();self.before=self.health();self.minimum=self.before;self.movement=0;self.begin=time.perf_counter();self.samples=0
  self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def health(self):
  return sum(x.get_editor_property('CurrentValue') for x in self.ins.call_method('GetAttributeValues',args=(self.p,)) if x.get_editor_property('AttributeName') in ['Health','Shield'])
 def tick(self,dt):
  self.samples+=1;self.minimum=min(self.minimum,self.health());self.movement=max(self.movement,(self.e.get_actor_location()-self.start).length())
  if time.perf_counter()-self.begin<10:return
  unreal.unregister_slate_post_tick_callback(self.handle);self.settings.set_editor_property('bThrottleCPUWhenNotForeground',self.old)
  c=self.e.get_controller();brain=c.get_editor_property('BrainComponent')
  r={'movement_cm':self.movement,'player_damage':self.before-self.minimum,'samples':self.samples,'controller':c.get_class().get_name(),'brain_running':brain.is_running() if brain else False}
  Path('A:/K-02 5.8/Saved/Diagnostics/arena-enemy-results.json').write_text(json.dumps(r,indent=2));unreal.log('K02_ARENA_ENEMY '+json.dumps(r))
_k02_enemy_observation=EnemyObservation()
