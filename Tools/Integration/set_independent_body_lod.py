"""Visible retargeted bodies choose LOD by screen size; outfits still follow their body."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.actor import ActorTools as Actors
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir());rows=[]
for path in json.loads((ROOT/'Saved/Diagnostics/Integration/lod-blueprint-targets.json').read_text()):
 bp=unreal.load_asset(path);cdo=B.get_default_object(bp);cs={c.get_name().replace('_GEN_VARIABLE',''):c for c in Actors.get_components(cdo)};name='K02Body' if 'K02Body' in cs else 'Body';body=cs[name];before=body.get_editor_property('sync_attach_parent_lod');body.set_editor_property('sync_attach_parent_lod',False)
 B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE
 cs2={c.get_name().replace('_GEN_VARIABLE',''):c for c in Actors.get_components(B.get_default_object(bp))};assert not cs2[name].get_editor_property('sync_attach_parent_lod');assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
 rows.append({'asset':path,'component':name,'before':before,'after':False,'reason':'Hidden Manny source must not pin visible body to LOD0; outfit LeaderPose remains unchanged'})
(ROOT/'Saved/Diagnostics/Integration/independent-body-lod.json').write_text(json.dumps(rows,indent=2));print('INDEPENDENT_BODY_LOD',len(rows))
