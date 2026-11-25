import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0);rows=[]
for c in p.get_components_by_class(unreal.ActorComponent):
 if c.get_class().get_name()=='BP_MACS_TraceComp_C' or c.get_name() in ['CharacterMesh0','K02Body','K02Dogi']:
  rows.append({'component':c.get_name(),'class':c.get_class().get_name(),'enabled':c.is_component_tick_enabled(),'tick':unreal.ToolsetLibrary.get_object_properties(c,['PrimaryComponentTick']),'properties':unreal.ToolsetLibrary.get_object_properties(c,['TracePointsRef','LocalMeshesRef','IsTracing'])})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/runtime-trace-tick.json').write_text(json.dumps(rows,indent=2));print(rows)
