import unreal
from editor_toolset.toolsets.skeletal_mesh import SkeletalMeshTools as S
for c in [S,unreal.SkeletalMesh,unreal.SkeletalMeshDescription]:
 print('TYPE',c.__name__)
 for n in dir(c):
  if any(k in n.lower() for k in ['lod','vertex','triangle','description','build']):print(n,getattr(c,n).__doc__)
