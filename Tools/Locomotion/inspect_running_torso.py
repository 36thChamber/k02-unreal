"""Read-only torso motion and native pose graph inspection."""
import unreal,json,math
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
D=Path('A:/K-02 5.8/Saved/Diagnostics/RunningTorso');D.mkdir(parents=True,exist_ok=True);r={'graphs':{},'clips':{}}
for name in ['ABP_K02_Player','ABP_K02_Locomotion','ABP_K02_Commun']:
 bp=unreal.load_asset('/Game/K02/Protagonist/Locomotion/'+name)
 for g in B.list_graphs(bp):
  if g.get_name() not in ['AnimGraph','BS_MACS_Locomotion_UE5_2']:continue
  nodes=[]
  for n in B.find_nodes(g):
   item={'name':n.get_name(),'class':n.get_class().get_name(),'inputs':{},'outputs':{}}
   if 'node' in json.loads(unreal.ToolsetLibrary.list_struct_properties(n.get_class())):item['node']=json.loads(unreal.ToolsetLibrary.get_object_properties(n,['node']))['node']
   info=B._get_node_info(n)
   for label,pins in [('inputs',info.input_pins),('outputs',info.output_pins)]:
    for pin in pins:item[label][pin.name]={'value':pin.value,'links':[{'node':x.node.get_path_name(),'index':x.index_id} for x in pin.connected_pins]}
   nodes.append(item)
  r['graphs'][name+'/'+g.get_name()]=nodes
paths=['/Game/K02/Animations/FightAnimations/Manny/A_Run_F_Manny','/Game/K02/Animations/FightAnimations/Manny/A_Move_F_Manny','/Game/K02/Animations/FightAnimations/Manny/A_Idle_Active_Manny','/Game/MACS/Animations/Movements/AS_MACS_N_Run_F_UE5','/Game/MACS/Animations/Movements/AS_MACS_N_Sprint_F_UE5','/Game/MACS/Animations/Movements/AS_MACS_N_Run_B_UE5','/Game/MACS/Animations/Movements/AS_MACS_N_Run_FL_UE5','/Game/MACS/Animations/Movements/AS_MACS_N_Run_FR_UE5']
opt=unreal.AnimPoseEvaluationOptions();opt.set_editor_property('should_retarget',False)
for path in paths:
 a=unreal.load_asset(path);row={'duration':a.get_play_length(),'skeleton':a.get_editor_property('Skeleton').get_path_name(),'poses':[]}
 for i in range(61):
  pose=a.get_anim_pose_at_time(a.get_play_length()*i/60,opt);sample={}
  for bone in ['root','pelvis','spine_01','spine_02','spine_03','spine_04','spine_05','clavicle_l','clavicle_r','upperarm_l','upperarm_r','hand_l','hand_r','foot_l','foot_r']:
   tr=unreal.AnimPoseExtensions.get_bone_pose(pose,bone,unreal.AnimPoseSpaces.WORLD);rr=tr.rotation.rotator();sample[bone]={'p':tr.translation.to_tuple(),'r':[rr.pitch,rr.yaw,rr.roll]}
  row['poses'].append(sample)
 r['clips'][path]=row
(D/'inspection.json').write_text(json.dumps(r));unreal.log('K02_RUNNING_TORSO_INSPECTED')
