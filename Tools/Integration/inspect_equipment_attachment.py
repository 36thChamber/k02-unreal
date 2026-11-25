"""Read native Blueprint nodes/pins without DSL reconstruction or compilation."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
paths=['/Game/MACS/Classes/BP_MACS_Inv_Item']
r={}
for path in paths:
 bp=unreal.load_asset(path);assert bp
 r[path]={}
 for g in B.list_graphs(bp):
  nodes=B.find_nodes(g);names=[n.get_node_title() for n in nodes]
  if any(any(t in n.lower() for t in ['attach','mesh','socket']) for n in names):
   r[path][g.get_name()]=names
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/equipment-attachment-nodes.json').write_text(json.dumps(r,indent=2));print(r)
