import unreal,inspect
from editor_toolset.toolsets.blueprint import BlueprintTools as B
print('FACTORY',unreal.BlueprintFactory.__doc__)
for n in ['create_blueprint','add_variable','add_function_graph','add_function_input','add_function_output']:
 print(n,getattr(B,n).__doc__ if hasattr(B,n) else 'absent')
bp=unreal.EditorAssetLibrary.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');g=next(g for g in B.list_graphs(bp) if g.get_name()=='K02ShowTrainingMenu')
for query in ['SaveGameToSlot','LoadGameFromSlot','CreateSaveGameObject','GetGameUserSettings','SetFrameRateLimit','ApplySettings']:
 print(query,B.find_node_types(g,query))
print('CREATE',unreal.AssetToolsHelpers.get_asset_tools().create_asset.__doc__)
