import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();r=[]
for name in ['ABP_K02_Commun','ABP_K02_Locomotion','ABP_K02_Jump']:
 bp=unreal.load_asset('/Game/K02/Protagonist/Locomotion/'+name)
 for g in B.list_graphs(bp):
  for n in B.find_nodes(g):
   if 'BlendList' in n.get_class().get_name():
    info=B._get_node_info(n);r.append({'node':n.get_path_name(),'pins':[(p.name,p.value,len(p.connected_pins)) for p in info.input_pins]})
Path('A:/K-02 5.8/Saved/Diagnostics/TransitionBlends/blend-pins.json').write_text(json.dumps(r,indent=2));unreal.log('K02_BLEND_PINS_AUDITED')
