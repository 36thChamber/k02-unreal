import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0);inv=next(c for c in p.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name()=='BP_MACS_Inventory_Comp_C');weapon=inv.call_method('GetCurrentWeaponActor');body=next(c for c in p.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='K02Body')
r={'source_hand':str(p.mesh.get_socket_transform('hand_r')),'target_hand':str(body.get_socket_transform('hand_r')),'source_socket':str(p.mesh.get_socket_transform('MACS_Weapon_Katana')),'target_socket':str(body.get_socket_transform('MACS_Weapon_Katana')),'weapon':[]}
for c in weapon.get_components_by_class(unreal.StaticMeshComponent):
 if not c.is_visible():continue
 r['weapon'].append({'mesh':c.static_mesh.get_path_name(),'bounds':str(c.static_mesh.get_bounds()),'transform':str(c.get_world_transform()),'sockets':{str(n):str(c.get_socket_transform(n,unreal.RelativeTransformSpace.RTS_COMPONENT)) for n in c.get_all_socket_names()}})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/sword-geometry.json').write_text(json.dumps(r,indent=2));print(r)
