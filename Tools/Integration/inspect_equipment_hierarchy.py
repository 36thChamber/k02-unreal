import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
r=[];bp=unreal.load_asset('/Game/MACS/Classes/Components/BP_MACS_Inventory_Comp')
while bp:
 parent=B.get_parent(bp);r.append({'asset':bp.get_path_name(),'parent':parent.get_path_name(),'graphs':{g.get_name():[n.get_node_title() for n in B.find_nodes(g)] for g in B.list_graphs(bp)}})
 path=parent.get_path_name().split('.')[0];bp=unreal.load_asset(path) if path.startswith('/Game/') else None
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/equipment-hierarchy.json').write_text(json.dumps(r,indent=2));print([(x['asset'],x['parent'],list(x['graphs'])) for x in r])
