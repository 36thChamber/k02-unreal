import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
for path,gn in [('/Game/K02/UI/Training/WBP_K02_TrainingMenu','K02Resume'),('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController','K02ShowTrainingMenu')]:
 b=unreal.load_asset(path);g=next(g for g in B.list_graphs(b) if g.get_name()==gn);print(path)
 for term in ['GetResume','ShowMouseCursor','K02CloseTrainingMenu','K02FocusResume','Equal','SetFocustoGameViewport','OpenLevel']:
  print(term,[str(x) for x in B.find_node_types(g,term) if term!='Equal' or ('Key' in str(x))][:12])
