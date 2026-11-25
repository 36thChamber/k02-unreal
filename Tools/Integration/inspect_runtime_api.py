import unreal,json
from pathlib import Path
r={}
for name in ['Actor','SkeletalMeshComponent','PhysicsAssetToolset','BlueprintEditorSettings','SaveOnCompile','SkeletalMeshSocket','SkeletalMesh','SubobjectDataSubsystem']:
 c=getattr(unreal,name,None)
 r[name]={'doc':getattr(c,'__doc__',''),'methods':{k:getattr(getattr(c,k),'__doc__','') for k in dir(c) if any(t in k.lower() for t in ['component','physics','socket','collision','save_on','attach','register'])}}
 if name=='BlueprintEditorSettings' and c:
  s=unreal.get_default_object(c)
  r[name]['value']=str(s.get_editor_property('save_on_compile'))
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/runtime-api.json').write_text(json.dumps(r,indent=2))
print('API recorded')
