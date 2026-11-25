"""Place free gaits near authored cadence instead of blending sped-up walks into runs."""
import unreal,json,copy
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
path='/Game/K02/Protagonist/Locomotion/BS_K02_FreeLocomotion';a=unreal.load_asset(path);old=json.loads(Path('A:/K-02 5.8/Docs/Validation/CombatSlip/build-baseline.json').read_text())['freeSamples'];rows=[]
for angle in sorted(set(s['sampleValue']['x'] for s in old)):
 samples={s['sampleValue']['y']:s for s in old if s['sampleValue']['x']==angle}
 for speed,sourceSpeed in [(0,0),(140,100),(370,550),(520,1000 if angle==0 else 550)]:
  s=copy.deepcopy(samples[sourceSpeed]);s['sampleValue']['y']=speed
  if sourceSpeed:s['rateScale']*=speed/sourceSpeed
  rows.append(s)
props=json.loads(unreal.ToolsetLibrary.get_object_properties(a,['blendParameters']));props['blendParameters'][1]['max']=520;props['sampleData']=rows
assert unreal.ToolsetLibrary.set_object_properties(a,json.dumps({'sampleData':[]}));assert unreal.ToolsetLibrary.set_object_properties(a,json.dumps(props))
sub=unreal.get_editor_subsystem(unreal.AssetEditorSubsystem);sub.close_all_editors_for_asset(a);sub.open_editor_for_assets([a]);assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False);sub.close_all_editors_for_asset(a)
Path('A:/K-02 5.8/Saved/Diagnostics/CombatSlip/free-gait-samples.json').write_text(json.dumps(rows,indent=2));unreal.log('K02_FREE_GAIT_CADENCE_REBUILT')
