"""Save final outputs and remove only backed-up intermediate exports."""
import unreal,json,re
from pathlib import Path
D=Path('A:/K-02 5.8/Saved/Diagnostics')
v=json.loads((D/'retarget-validation.json').read_text());assert v['status']=='pass' and v['count']==239
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary
for row in v['rows']:assert A.save_asset(row['target'],only_if_is_dirty=True)
old=[a for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game/K02/Animations/FightAnimations',recursive=False) if str(a.asset_class_path.asset_name)=='AnimSequence']
assert len(old)==0 or 239<=len(old)<=280,len(old)
assert all(re.fullmatch(r'A_.+_Manny[0-9]*',str(x.asset_name)) for x in old)
if old:
 assert Path('A:/K-02 5.8/Content/K02/Animations/FightAnimations/Manny').is_dir()
 assert unreal.get_editor_subsystem(unreal.EditorAssetSubsystem).delete_loaded_assets([x.get_asset() for x in old])
new=[a for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game/K02/Animations/FightAnimations',recursive=True) if str(a.asset_class_path.asset_name)=='AnimSequence']
assert len(new)==239,len(new)
for path in A.list_assets('/Game/K02/Retarget/FightAnimations',recursive=True,include_folder=False):assert A.save_asset(path,only_if_is_dirty=False)
unreal.log('K02_RETARGET_FINALIZED 239 sequences; removed intermediates='+str(len(old)))
