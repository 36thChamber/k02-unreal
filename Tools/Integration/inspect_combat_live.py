import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0);pc=unreal.GameplayStatics.get_player_controller(w,0)
i=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'))
r={'tags':list(i.call_method('GetActiveTags',args=(p,))),'attrs':[str(a) for a in i.call_method('GetAttributeValues',args=(p,))],'controller':json.loads(unreal.ToolsetLibrary.get_object_properties(pc,['K02InputBuffer','K02BufferedInput','K02CurrentCombo','K02LastInput','K02CombatInputBuffer','K02InputBufferTime'])),'trace':json.loads(unreal.ToolsetLibrary.get_object_properties(next(c for c in p.get_components_by_class(unreal.ActorComponent) if c.get_name()=='UnarmedTrace'),['TracePointsRef']))}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/combat-live.json').write_text(json.dumps(r,indent=2));print(r)
