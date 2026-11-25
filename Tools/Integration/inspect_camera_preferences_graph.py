import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');g=next(g for g in B.list_graphs(bp) if g.get_name()=='K02ApplyComfortPreferences');rows=[]
for n in B.find_nodes(g):
 rows.append({'name':n.get_name(),'title':n.get_node_title(),'pins':[{'n':str(p.get_pin_name()),'v':p.get_pin_value(),'links':[(q.get_owning_node().get_name(),str(q.get_pin_name())) for q in p.list_connected_pins()]} for p in n.list_all_pins()]})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/camera-preferences-graph.json').write_text(json.dumps(rows,indent=2));print('CAMERA_PREF_GRAPH_READ',len(rows))
