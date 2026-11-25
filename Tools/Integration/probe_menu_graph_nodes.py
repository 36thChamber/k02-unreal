import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/UI/Training/WBP_K02_TrainingMenu');g=B.add_function_graph(bp,'K02FocusResume')
for term in ['GetKey','Handled','SetInputModeGameOnly','ShowMouseCursor','SetGamePaused','GetOwningPlayer','AddToViewport','RemoveFromParent']:
 print(term,[str(x) for x in B.find_node_types(g,term)][:12])
print('override',[str(f) for f in B.list_functions(bp) if 'KeyDown' in str(f)])
