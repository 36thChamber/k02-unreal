import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
r={}
for path,names in [('/Game/K02/UI/Training/WBP_K02_TrainingMenu',['OnPreviewKeyDown','K02Resume','K02Restart','K02FocusResume']),('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController',['K02ShowTrainingMenu','K02CloseTrainingMenu'])]:
 bp=unreal.load_asset(path);r[path]={'status':str(bp.get_editor_property('Status')),'graphs':{}}
 for g in B.list_graphs(bp):
  if g.get_name() not in names:continue
  r[path]['graphs'][g.get_name()]=[{'name':n.get_name(),'title':n.get_node_title(),'class':n.get_class().get_name(),'pins':[{'n':str(p.get_pin_name()),'v':p.get_pin_value(),'links':[(q.get_owning_node().get_name(),str(q.get_pin_name())) for q in p.list_connected_pins()]} for p in n.list_all_pins()]} for n in B.find_nodes(g)]
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/menu-binding-inspection.json').write_text(json.dumps(r,indent=2))
print({k:v['status'] for k,v in r.items()})
