import unreal,json
from pathlib import Path
r={};opt=unreal.AnimPoseEvaluationOptions();opt.set_editor_property('should_retarget',False)
for name,bone in [('A_JabHead_L_IP','hand_l'),('A_PunchHead_R_IP','hand_r'),('A_HookHead_L_IP','hand_l')]:
 a=unreal.load_asset('/Game/K02/Animations/FightAnimations/Manny/'+name+'_Manny');n=unreal.AnimationLibrary.get_num_frames(a);points=[]
 for f in range(n+1):
  t=unreal.AnimationLibrary.get_time_at_frame(a,f);pose=a.get_anim_pose_at_time(t,opt);v=unreal.AnimPoseExtensions.get_bone_pose(pose,bone,unreal.AnimPoseSpaces.WORLD).translation
  points.append({'frame':f,'time':t,'xyz':[v.x,v.y,v.z]})
 r[name]={'bone':bone,'frames':n,'length':a.get_play_length(),'hand_path':points}
Path('A:/K-02 5.8/Saved/Diagnostics/punch-timing.json').write_text(json.dumps(r,indent=2));unreal.log('K02_PUNCH_TIMING_MEASURED')
