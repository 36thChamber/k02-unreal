"""Open native Blend Space editor to rebuild runtime interpolation data, then explicitly save."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
a=unreal.load_asset('/Game/K02/Protagonist/Locomotion/BS_K02_Locomotion');sub=unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
sub.open_editor_for_assets([a]);assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False);sub.close_all_editors_for_asset(a)
Path('A:/K-02 5.8/Saved/Diagnostics/Locomotion/blendspace-rebuilt.json').write_text(unreal.ToolsetLibrary.get_object_properties(a,['sampleData','blendParameters','bInterpolateUsingGrid']));unreal.log('K02_BLENDSPACE_NATIVE_REBUILT')
