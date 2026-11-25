import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
m=unreal.load_asset('/Game/K02/Characters/Common/Materials/M_K02_Surface_v001')
before=json.loads(unreal.ToolsetLibrary.get_object_properties(m,['bUsedWithSkeletalMesh']))
assert unreal.ToolsetLibrary.set_object_properties(m,json.dumps({'bUsedWithSkeletalMesh':True}))
unreal.MaterialEditingLibrary.recompile_material(m)
assert unreal.EditorAssetLibrary.save_loaded_asset(m,False)
after=json.loads(unreal.ToolsetLibrary.get_object_properties(m,['bUsedWithSkeletalMesh']))
assert after['bUsedWithSkeletalMesh']
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/material-usage-fix.json').write_text(json.dumps({'asset':m.get_path_name(),'before':before,'after':after,'scope':'Own common material; all character instances inherit usage. Standalone reload pending.'},indent=2))
print('MATERIAL_USAGE_SAVED',after)
