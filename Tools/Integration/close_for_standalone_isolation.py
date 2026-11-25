import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
allowed=json.loads((Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/before-memory-isolation.json').read_text())['dirty_content']
for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages():
 assert p.get_name() in allowed and '/Game/K02/Characters/Protagonist/Dogi_v001/Materials/' in p.get_name(),p.get_name()
 assert unreal.EditorAssetLibrary.save_asset(p.get_name(),False)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()
print('All own changes saved; no dirty maps; closing Editor for isolated Standalone validation')
unreal.SystemLibrary.quit_editor()
