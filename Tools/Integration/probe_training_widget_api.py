import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');g=next(g for g in B.list_graphs(bp) if g.get_name()=='EventGraph')
for term in ['CreateWidget','Escape','SetInputModeUIOnly','SetGamePaused','SetKeyboardFocus']:
 print(term,[str(x) for x in B.find_node_types(g,term)][:8])
print('graph editors',[x for x in dir(unreal.BlueprintGraphEditor) if 'event' in x or 'widget' in x or 'create' in x])
