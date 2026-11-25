"""Compare real graph nodes/pin defaults/links, without DSL display ordering."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r={}
for src in ['/Game/MACS/Classes/Components/BP_MACS_TraceComp','/Game/MACS/Animations/AnimNotify/ANS_MACS_TraceForTargets']:
 name=src.rsplit('/',1)[1];copy='/Game/K02/Validation/SourceComparison/'+name;sets=[]
 for path in [src,copy]:
  bp=unreal.load_asset(path);assert bp
  graphs={}
  for g in B.list_graphs(bp):
   nodes={}
   for n in B.find_nodes(g):
    pins={}
    for p in n.list_all_pins():
     key=str(p.get_pin_direction())+':'+str(p.get_pin_name())
     pins[key]={'value':p.get_pin_value().replace(copy,src),'type':str(p.get_pin_type_display_string()),'links':sorted(str(q.get_owning_node().get_name())+':'+str(q.get_pin_name()) for q in p.list_connected_pins())}
    nodes[n.get_name()]={'class':n.get_class().get_name(),'title':str(n.get_node_title()),'pins':pins}
   graphs[g.get_name()]=nodes
  sets.append(graphs)
 r[name]={'equal':sets[0]==sets[1],'different_graphs':[n for n in set(sets[0])|set(sets[1]) if sets[0].get(n)!=sets[1].get(n)],'graphs':sets}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/commercial-pin-comparison.json').write_text(json.dumps(r,indent=2))
print({n:{k:v for k,v in s.items() if k!='graphs'} for n,s in r.items()})
