import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.EditorAssetLibrary.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');g=next(g for g in B.list_graphs(bp) if g.get_name()=='K02HideDemoHelp')
for t in ['Widget|SetVisibility','Class|Widget|SetVisibility']:
 n=B.create_node(g,t,unreal.IntPoint(0,0));print(t,[(p.get_pin_name(),str(p),p.get_pin_value()) for p in n.list_input_pins()])
