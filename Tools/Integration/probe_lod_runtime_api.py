import unreal
for cls in [unreal.SkeletalMeshComponent,unreal.SkinnedMeshComponent]:
 for n in dir(cls):
  if any(s in n for s in ['forced_lod','predicted_lod','skeletal_mesh','skinned_asset','animation_mode']):
   print(cls.__name__,n,getattr(cls,n).__doc__)
