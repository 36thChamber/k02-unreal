import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');g=next(g for g in B.list_graphs(bp) if g.get_name()=='K02ShowTrainingMenu')
for term in ['GetHUD','GetUI','GetWB_MACS_DemoKeys','GetWBMACSDemoKeys','SetVisibility']:
 print(term,[str(x) for x in B.find_node_types(g,term)][:20])
