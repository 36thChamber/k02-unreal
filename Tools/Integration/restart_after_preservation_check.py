import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir())
for file in ['commercial-pin-comparison.json','commercial-default-comparison.json']:
 assert all(v['equal'] for v in json.loads((ROOT/'Saved/Diagnostics/Integration'/file).read_text()).values())
reload=[]
for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages():
 name=p.get_name()
 if name.startswith('/Game/K02/Characters/'):
  assert unreal.EditorAssetLibrary.save_asset(name,False)
 elif name.startswith('/Game/K02/Validation/SourceComparison/') or name in ['/Game/MACS/Classes/Components/BP_MACS_TraceComp','/Game/MACS/Animations/AnimNotify/ANS_MACS_TraceForTargets']:reload.append(p)
 else:raise RuntimeError('Unexpected dirty package; preserve before exit: '+name)
if reload:
 ok,error=unreal.EditorLoadingAndSavingUtils.reload_packages(reload,unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE);assert ok and not str(error),str(error)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(),[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
print('Own assets saved; comparison-only dirty state discarded; normal editor shutdown')
unreal.SystemLibrary.quit_editor()
