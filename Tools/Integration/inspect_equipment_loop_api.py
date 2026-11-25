import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Prototype/Blueprints/BP_K02_Player');g=next(g for g in B.list_graphs(bp) if g.get_name()=='EventGraph')
print(B.find_node_types(g,'ForEachLoop'));print([x for x in dir(unreal.BlueprintGraphEditor) if 'macro' in x or 'self' in x or 'node' in x])
