"""Exercise existing arena dummy and collectible sword through real GAS attacks."""
from pathlib import Path
src=Path('A:/K-02 5.8/Tools/Validation/unarmed_combat_regression.py').read_text()
exec(src[:src.index('_k02_unarmed_test =')])
class ArenaCombatTest(K02UnarmedCombatTest):
 def __init__(self):
  super().__init__()
  self.target.destroy_actor()
  self.target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.world,unreal.Pawn) if a.get_class().get_name()=='BP_K02_TrainingDummy_C')
  self.sword=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(self.world,unreal.Actor) if a.get_class().get_name()=='BP_K02_GroundSword_C')
  self.target.mesh.set_editor_property('VisibilityBasedAnimTickOption',unreal.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
 def equip_blade(self):
  self.inv.call_method('TryToGetWorldItem',args=(self.sword,))
 def finish(self,status,error=None):
  super().finish(status,error)
  p=Path('A:/K-02 5.8/Saved/Diagnostics')
  (p/'arena-combat-results.json').write_text((p/'unarmed-combat-results.json').read_text())
_k02_arena_combat=ArenaCombatTest()
_k02_arena_combat.handle=unreal.register_slate_post_tick_callback(_k02_arena_combat.tick)
