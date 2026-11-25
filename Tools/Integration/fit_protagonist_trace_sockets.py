"""Fit existing MACS trace centers to knuckles and insteps, without radius growth."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
BASE='/Game/K02/Characters/Protagonist/Dogi_v001';rc=unreal.IKRigController.get_controller(unreal.load_asset(BASE+'/Rig/IK_K02_Protagonist'));rows=[]
for name in ['SK_K02_BodyForDogi_v001','SK_K02_Dogi_Combined_v001']:
 mesh=unreal.load_asset(BASE+'/Meshes/'+name)
 for side in ['l','r']:
  for bone,end,alpha in [('hand_'+side,'middle_01_'+side,1.),('foot_'+side,'ball_'+side,.5)]:
   socket=mesh.find_socket(bone+'_Trace_Sphere');assert socket
   start=rc.get_ref_pose_transform_of_bone(bone);finish=rc.get_ref_pose_transform_of_bone(end)
   center=start.translation+(finish.translation-start.translation)*alpha
   pos=unreal.MathLibrary.inverse_transform_location(start,center);old=socket.relative_location.to_tuple()
   socket.set_editor_property('relative_location',pos)
   rows.append({'mesh':name,'socket':socket.get_name(),'bone':bone,'anatomical_reference':end,'fraction':alpha,'before_local_cm':old,'after_local_cm':pos.to_tuple(),'radius_cm':socket.relative_rotation.roll})
 assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,False)
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/protagonist-socket-fit.json').write_text(json.dumps(rows,indent=2));print(rows)
