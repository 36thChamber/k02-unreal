import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.EditorAssetLibrary.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');g=next(g for g in B.list_graphs(bp) if g.get_name()=='K02ShowTrainingMenu')
for q in ['Multiply','SetText','ToText','Append','DoesSaveGameExist','SetFieldOfView','SetFrameRateLimit']:
 print(q,B.find_node_types(g,q))
