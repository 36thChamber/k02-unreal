import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
bp=unreal.EditorAssetLibrary.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');rows={}
for g in B.list_graphs(bp):
 ns=[]
 for n in B.find_nodes(g):
  if 'TryActivateAbility' in n.get_node_title().replace(' ',''):
   ps=[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[(x.get_owning_node().get_node_title(),str(x.get_pin_name())) for x in p.list_connected_pins()]} for p in n.list_input_pins()]
   ns.append({'node':n.get_name(),'title':n.get_node_title(),'inputs':ps,'outputs':[{ 'name':str(p.get_pin_name()),'links':[(x.get_owning_node().get_node_title(),str(x.get_pin_name())) for x in p.list_connected_pins()]} for p in n.list_output_pins()]})
 if ns:rows[g.get_name()]=ns
out=Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/defense-denial-hooks.json';out.write_text(json.dumps(rows,indent=2));print({k:len(v) for k,v in rows.items()})
