"""Exact LBS skin sole estimates from original weights and live retarget bones."""
import unreal,json
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
pawn=unreal.GameplayStatics.get_player_pawn(W,0);body=next(c for c in pawn.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='K02Body')
rc=unreal.IKRigController.get_controller(unreal.load_asset('/Game/K02/Characters/Protagonist/Dogi_v001/Rig/IK_K02_Protagonist'))
vertices=json.loads((ROOT/'Saved/Diagnostics/Integration/Protagonist/contact-regions.json').read_text())['sole_vertices'];values={'l':[],'r':[]};bones={}
for v in vertices:
 pos=unreal.Vector(*v['position_cm']);world=unreal.Vector();total=sum(v['weights'].values())
 for bone,weight in v['weights'].items():
  if bone not in bones:bones[bone]=(rc.get_ref_pose_transform_of_bone(bone),body.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_WORLD))
  bind,live=bones[bone];local=unreal.MathLibrary.inverse_transform_location(bind,pos);world+=unreal.MathLibrary.transform_location(live,local)*(weight/total)
 side='l' if max(v['weights'],key=v['weights'].get).endswith('_l') else 'r';values[side].append(world.z)
r={'source':'original skin vertices z<3.5 cm, exact per-vertex weights and live bone matrices','world_floor_z_cm':0.,'body_offset':body.relative_location.to_tuple(),'montage':str(pawn.mesh.get_anim_instance().get_current_active_montage()),'feet':{k:{'samples':len(v),'min_z_cm':min(v),'median_z_cm':sorted(v)[len(v)//2]} for k,v in values.items()}}
(ROOT/'Saved/Diagnostics/Integration/protagonist-foot-contact.json').write_text(json.dumps(r,indent=2));print(r)
