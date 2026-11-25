"""Inventory dirty state before restoring incidental compiler-only resaves."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if 'RosterLab' in world.get_name():assert L.save_current_level()
r={'dirty_content':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()], 'dirty_maps':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()], 'reload_api':unreal.EditorLoadingAndSavingUtils.reload_packages.__doc__}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/before-restart.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
