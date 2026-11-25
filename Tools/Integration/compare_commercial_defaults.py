import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
from editor_toolset.toolsets.object import ObjectTools as O
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r={}
for src in ['/Game/MACS/Classes/Components/BP_MACS_TraceComp','/Game/MACS/Animations/AnimNotify/ANS_MACS_TraceForTargets']:
 name=src.rsplit('/',1)[1];copy='/Game/K02/Validation/SourceComparison/'+name;sets=[]
 for path in [src,copy]:
  cdo=B.get_default_object(unreal.load_asset(path));names=list(json.loads(O.list_properties(cdo)))
  sets.append(json.loads(O.get_properties(cdo,names).replace(copy,src)))
 r[name]={'equal':sets[0]==sets[1],'differences':[k for k in set(sets[0])|set(sets[1]) if sets[0].get(k)!=sets[1].get(k)],'values':sets}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/commercial-default-comparison.json').write_text(json.dumps(r,indent=2))
print({k:{n:v for n,v in d.items() if n!='values'} for k,d in r.items()})
