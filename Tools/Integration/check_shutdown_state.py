import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r={'dirty_content':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],'dirty_maps':[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/before-memory-isolation.json').write_text(json.dumps(r,indent=2));print(r)
