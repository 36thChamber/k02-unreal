import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.EditorAssetLibrary.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
r={}
for g in B.list_graphs(bp):
 rows=[]
 for n in B.find_nodes(g):
  title=n.get_node_title()
  if any(x.lower() in title.lower() for x in ['yaw','pitch','turn','look','sensitivity','camera','field of view','arm length']):
   rows.append({'name':n.get_name(),'title':title,'inputs':[{ 'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[(x.get_owning_node().get_node_title(),str(x.get_pin_name())) for x in p.list_connected_pins()]} for p in n.list_input_pins()]})
 if rows:r[g.get_name()]=rows
out=Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/comfort-hooks.json';out.write_text(json.dumps(r,indent=2));print({k:len(v) for k,v in r.items()});print('CDO',unreal.ToolsetLibrary.get_object_properties(B.get_default_object(bp),['InputYawScale','InputPitchScale','bEnableClickEvents','bEnableMouseOverEvents']))
