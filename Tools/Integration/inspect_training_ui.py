import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');r={'variables':[],'graphs':{}}
for n in B.list_variables(bp):
 if any(s in n.lower() for s in ['ui','widget','menu','hud']):r['variables'].append(n)
for g in B.list_graphs(bp):
 if any(k in g.get_name().lower() for k in ['ui','widget','begin','eventgraph']):
  r['graphs'][g.get_name()]=[{'title':n.get_node_title(),'class':n.get_class().get_name()} for n in B.find_nodes(g)]
c=unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet');r['toolset']=str(c)
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/training-ui-inspection.json').write_text(json.dumps(r,indent=2));print(r)
