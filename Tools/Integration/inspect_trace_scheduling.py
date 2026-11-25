"""Native read-only Blueprint graph inspection; never compiles purchased assets."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r={}
for path in ['/Game/MACS/Classes/Components/BP_MACS_TraceComp','/Game/MACS/Animations/AnimNotify/ANS_MACS_TraceForTargets']:
 bp=unreal.load_asset(path);graphs={}
 for g in B.list_graphs(bp):
  graphs[g.get_name()]=[{'name':n.get_name(),'title':n.get_node_title(),'inputs':[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[(x.get_owning_node().get_name(),str(x.get_pin_name())) for x in p.list_connected_pins()]} for p in n.list_input_pins()]} for n in B.find_nodes(g)]
 r[path]={'variables':[str(x) for x in B.list_variables(bp)],'graphs':graphs}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/trace-scheduling-inspection.json').write_text(json.dumps(r,indent=2));print({p:{g:len(n) for g,n in v['graphs'].items()} for p,v in r.items()})
