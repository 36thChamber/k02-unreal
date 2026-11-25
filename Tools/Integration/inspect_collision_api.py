import unreal
print(unreal.PrimitiveComponent.set_collision_response_to_all_channels.__doc__)
for n in ['CollisionResponse','CollisionResponseType','CollisionChannel','EdGraphPinRef']:
 o=getattr(unreal,n,None);print(n,dir(o))
