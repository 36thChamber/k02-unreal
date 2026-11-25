"""Read-only semantic comparison after an incidental compile/save."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r={}
for src in ['/Game/MACS/Classes/Components/BP_MACS_TraceComp','/Game/MACS/Animations/AnimNotify/ANS_MACS_TraceForTargets']:
 name=src.rsplit('/',1)[1];copy='/Game/K02/Validation/SourceComparison/'+name
 sets=[]
 for path in [src,copy]:
  bp=unreal.load_asset(path);assert bp
  sets.append({g.get_name():B.read_graph_dsl(g).replace(path,src) for g in B.list_graphs(bp)})
 r[name]={'equal':sets[0]==sets[1],'different_graphs':[n for n in set(sets[0])|set(sets[1]) if sets[0].get(n)!=sets[1].get(n)],'graphs':sets}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/commercial-baseline-comparison.json').write_text(json.dumps(r,indent=2))
print({n:{k:v for k,v in s.items() if k!='graphs'} for n,s in r.items()})
