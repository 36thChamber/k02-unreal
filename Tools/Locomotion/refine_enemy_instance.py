"""Update the placed arena enemy's migrated navigation override, then save only this map."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert w.get_name()=='L_K02_CombatArena'
e=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Character) if a.get_class().get_name()=='BP_K02_Enemy_C');m=e.character_movement
before=json.loads(unreal.ToolsetLibrary.get_object_properties(m,['NavMovementProperties']));nav=m.get_editor_property('NavMovementProperties');nav.set_editor_property('bUseAccelerationForPaths',True);m.set_editor_property('NavMovementProperties',nav)
assert unreal.EditorLevelLibrary.save_current_level()
Path('A:/K-02 5.8/Saved/Diagnostics/Locomotion/enemy-instance.json').write_text(json.dumps({'before':before,'after':json.loads(unreal.ToolsetLibrary.get_object_properties(m,['NavMovementProperties']))},indent=2));unreal.log('K02_ENEMY_INSTANCE_NAV_SAVED')
