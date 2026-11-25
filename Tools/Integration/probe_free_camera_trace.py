import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();p=unreal.GameplayStatics.get_player_pawn(W,0);a=p.get_components_by_class(unreal.SpringArmComponent)[0];start=a.get_world_location();hit=unreal.SystemLibrary.sphere_trace_single(W,start,start+unreal.Vector(0,0,160),16,unreal.TraceTypeQuery.TRACE_TYPE_QUERY2,False,[p],unreal.DrawDebugTrace.NONE,True)
print('TRACE',str(hit));bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');g=next(g for g in B.list_graphs(bp) if g.get_name()=='K02UpdateFreeCamera');r=[]
for n in B.find_nodes(g):
 r.append({'title':n.get_node_title(),'pins':[{'n':str(x.get_pin_name()),'v':x.get_pin_value(),'links':[(q.get_owning_node().get_node_title(),str(q.get_pin_name())) for q in x.list_connected_pins()]} for x in n.list_all_pins()]})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/free-camera-nodes.json').write_text(json.dumps(r,indent=2))
