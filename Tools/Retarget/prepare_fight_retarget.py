"""Prepare isolated copies of the shipped UE4 -> UE5 retarget assets."""
import unreal,json
from pathlib import Path
ROOT='/Game/K02/Retarget/FightAnimations'
A=unreal.EditorAssetLibrary
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(),'Stop PIE first'
base='/Game/MACS/Demo/ThirdPersonTemplateUE5/Characters/'
source_mesh=unreal.load_asset('/Game/FightAnimations/Mannequin/Character/Mesh/SK_Mannequin')
target_mesh=unreal.load_asset(base+'Mannequins/Meshes/SKM_Manny')
paths=[(base+'Mannequin_UE4/Rigs/IK_UE4_Mannequin',ROOT+'/Rigs/IK_Fight_UE4'),(base+'Mannequins/Rigs/IK_Mannequin',ROOT+'/Rigs/IK_K02_Manny'),(base+'Mannequin_UE4/Rigs/RTG_UE4Manny_UE5Manny',ROOT+'/Rigs/RTG_Fight_UE4_K02_Manny')]
for src,dst in paths:
 if not A.does_asset_exist(dst):assert A.duplicate_asset(src,dst),dst
source_rig=unreal.load_asset(paths[0][1]);target_rig=unreal.load_asset(paths[1][1]);rt=unreal.load_asset(paths[2][1])
sc=unreal.IKRigController.get_controller(source_rig)
bones=['root','pelvis','spine_01','spine_03','clavicle_l','upperarm_l','lowerarm_l','hand_l','thigh_l','calf_l','foot_l','ball_l','head']
baseline=unreal.IKRigController.get_controller(unreal.load_asset(paths[0][0]))
old={b:baseline.get_ref_pose_transform_of_bone(b) for b in bones}
assert sc.set_skeletal_mesh(source_mesh)
ref_errors={b:{'position_cm':(old[b].translation-sc.get_ref_pose_transform_of_bone(b).translation).length(),'rotation_dot':abs(sum(getattr(old[b].rotation,v)*getattr(sc.get_ref_pose_transform_of_bone(b).rotation,v) for v in ['x','y','z','w']))} for b in bones}
assert unreal.IKRigController.get_controller(target_rig).set_skeletal_mesh(target_mesh)
c=unreal.IKRetargeterController.get_controller(rt)
for side,rig,mesh in [(unreal.RetargetSourceOrTarget.SOURCE,source_rig,source_mesh),(unreal.RetargetSourceOrTarget.TARGET,target_rig,target_mesh)]:
 c.set_ik_rig(side,rig);c.assign_ik_rig_to_all_ops(side,rig);c.set_preview_mesh(side,mesh)
# Explicit matching prevents fuzzy mapping a finger to a thigh twist.
c.auto_map_chains(unreal.AutoMapChainType.EXACT,True)
root_index=c.get_index_of_op_by_name('Root Motion')
if root_index<0:root_index=c.add_retarget_op('/Script/IKRig.IKRetargetRootMotionOp')
root_ctrl=c.get_op_controller(root_index)
root_ctrl.set_source_root_bone('root');root_ctrl.set_target_root_bone('root');root_ctrl.set_target_pelvis_bone('pelvis')
pin_index=c.get_index_of_op_by_name('Pin Bones')
if pin_index<0:pin_index=c.add_retarget_op('/Script/IKRig.IKRetargetPinBoneOp')
pc=c.get_op_controller(pin_index);pc.clear_all_bone_pairs()
for src_bone,dst_bone in [('foot_l','ik_foot_l'),('foot_r','ik_foot_r'),('hand_r','ik_hand_gun'),('hand_l','ik_hand_l'),('hand_r','ik_hand_r')]:
 pc.set_bone_pair(src_bone,dst_bone)
assert len(pc.get_all_bone_pairs())==5
ops=[]
for i in range(30):
 n=c.get_op_name(i)
 if str(n)=='None':break
 ops.append({'name':str(n),'enabled':c.get_retarget_op_enabled(i)})
chains=[str(x.chain_name) for x in unreal.IKRigController.get_controller(target_rig).get_retarget_chains()]
mapping={ch:str(c.get_source_chain(ch)) for ch in chains}
for _,dst in paths:assert A.save_asset(dst,only_if_is_dirty=False)
r={'source_mesh':source_mesh.get_path_name(),'target_mesh':target_mesh.get_path_name(),'retargeter':rt.get_path_name(),'reference_pose_comparison':ref_errors,'ops':ops,'chain_mapping':mapping,'pin_bone_pairs':{str(k):str(v) for k,v in pc.get_all_bone_pairs().items()},'source_pose':str(c.get_current_retarget_pose_name(unreal.RetargetSourceOrTarget.SOURCE)),'target_pose':str(c.get_current_retarget_pose_name(unreal.RetargetSourceOrTarget.TARGET))}
Path('A:/K-02 5.8/Saved/Diagnostics/retarget-setup.json').write_text(json.dumps(r,indent=2))
unreal.log('K02_RETARGET_PREPARED '+json.dumps(r))
