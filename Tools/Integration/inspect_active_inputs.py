import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');rows=[]
for g in B.list_graphs(bp):
 for n in B.find_nodes(g):
  if any(k in n.get_class().get_name() for k in ['InputKey','InputAction']):
   rows.append({'graph':g.get_name(),'title':n.get_node_title(),'links':[(str(p.get_pin_name()),q.get_owning_node().get_node_title()) for p in n.list_all_pins() for q in p.list_connected_pins()]})
paths=unreal.EditorAssetLibrary.list_assets('/Game/K02',True,False);contexts=[]
for path in paths:
 if '/IMC_' not in path:continue
 a=unreal.load_asset(path)
 if not isinstance(a,unreal.InputMappingContext):continue
 contexts.append({'path':path,'mappings':[{'key':str(m.key),'action':str(m.action),'modifiers':[str(x) for x in m.modifiers]} for m in a.get_editor_property('DefaultKeyMappings').get_editor_property('Mappings')]})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/active-inputs.json').write_text(json.dumps({'events':rows,'contexts':contexts},indent=2));print(rows)
