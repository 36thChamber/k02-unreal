"""Read a live evaluated idle pose to transfer socket axes to the new skeleton."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.skeletal_mesh import SkeletalMeshTools as S
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert W
p=unreal.GameplayStatics.get_player_pawn(W,0);src=p.mesh;dst=next(c for c in p.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='K02Body')
assert not src.get_anim_instance().get_current_active_montage(),'Use settled idle for calibration'
rows=[]
for name in S.get_socket_names(src.get_skinned_asset()):
 name=str(name)
 if not name.startswith('MACS_Weapon_'):continue
 socket=src.get_skinned_asset().find_socket(name);bone=str(socket.bone_name);targetbone='spine_03' if bone=='spine_05' else bone
 if not dst.does_socket_exist(targetbone):continue
 source=src.get_socket_transform(bone,unreal.RelativeTransformSpace.RTS_WORLD);target=dst.get_socket_transform(targetbone,unreal.RelativeTransformSpace.RTS_WORLD);sw=src.get_socket_transform(name,unreal.RelativeTransformSpace.RTS_WORLD)
 ratio=1.;grip_correction=unreal.Vector()
 if bone in ['hand_l','hand_r']:
  finger='middle_01_'+bone[-1];grip_correction=((dst.get_socket_location(finger)-target.translation)-(src.get_socket_location(finger)-source.translation))*.5;ratio=dst.get_socket_location(finger).distance(target.translation)/src.get_socket_location(finger).distance(source.translation)
 desired=unreal.Transform(location=target.translation+(sw.translation-source.translation)+grip_correction,rotation=sw.rotation.rotator(),scale=sw.scale3d)
 local=unreal.MathLibrary.make_relative_transform(desired,target)
 rows.append({'name':name,'bone':targetbone,'local_position_cm':local.translation.to_tuple(),'local_rotation_pyr':[local.rotation.rotator().pitch,local.rotation.rotator().yaw,local.rotation.rotator().roll],'scale':socket.relative_scale.to_tuple(),'hand_length_ratio':ratio,'grip_correction_world_cm':grip_correction.to_tuple(),'method':'preserve weapon pivot offset; adjust palm center only'})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/protagonist-equipment-socket-calibration-v3.json').write_text(json.dumps(rows,indent=2));print('Calibrated',len(rows),'equipment sockets; visual verification pending')
