"""Use existing MACS UE5 forward running/sprint clips; retain combat gaits and native movement."""
import unreal,json,statistics,copy
from pathlib import Path
A=unreal.EditorAssetLibrary;D=Path('A:/K-02 5.8/Saved/Diagnostics/RunningTorso');D.mkdir(parents=True,exist_ok=True)
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
opt=unreal.AnimPoseEvaluationOptions();opt.set_editor_property('should_retarget',False)
def authored_speed(a):
 poses=[a.get_anim_pose_at_time(a.get_play_length()*i/120,opt) for i in range(121)];dt=a.get_play_length()/120;values=[]
 for foot in ['foot_l','foot_r']:
  p=[unreal.AnimPoseExtensions.get_bone_pose(s,foot,unreal.AnimPoseSpaces.WORLD).translation for s in poses];low=min(v.z for v in p)
  for x,y in zip(p,p[1:]):
   if max(x.z,y.z)<low+3 and abs(y.z-x.z)/dt<40:values.append(-(y.y-x.y)/dt)
 assert len(values)>10;return statistics.median(values),len(values)
bs=unreal.load_asset('/Game/K02/Protagonist/Locomotion/BS_K02_Locomotion');v=json.loads(unreal.ToolsetLibrary.get_object_properties(bs,['sampleData']));before=copy.deepcopy(v);r={'clips':[],'changes':[]}
for speed,name in [(550,'Run'),(1000,'Sprint')]:
 src='/Game/MACS/Animations/Movements/AS_MACS_N_'+name+'_F_UE5';dst='/Game/K02/Protagonist/Locomotion/Sequences/AS_K02_MACS_'+name+'_F';a=unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(src,dst);assert a
 authored,n=authored_speed(a);assert authored>100
 unreal.AnimationLibrary.set_root_motion_enabled(a,False);a.set_editor_property('bForceRootLock',True);a.set_editor_property('RootMotionRootLock',unreal.RootMotionRootLock.ANIM_FIRST_FRAME);assert A.save_loaded_asset(a,only_if_is_dirty=False)
 r['clips'].append({'source':src,'copy':dst,'authoredSpeedEstimate':authored,'stanceSamples':n,'runtimeCadenceCorrection':1.04,'duration':a.get_play_length(),'calibration':'median backward foot speed while low and vertically slow; source in-place'})
 for s in v['sampleData']:
  if s['sampleValue']['x']==0 and s['sampleValue']['y']==speed:
   old=copy.deepcopy(s);s['animation']={'refPath':a.get_path_name()};s['rateScale']=1.04*speed/authored;r['changes'].append({'before':old,'after':s})
assert len(r['changes'])==2
assert unreal.ToolsetLibrary.set_object_properties(bs,json.dumps({'sampleData':[]}));assert unreal.ToolsetLibrary.set_object_properties(bs,json.dumps(v))
sub=unreal.get_editor_subsystem(unreal.AssetEditorSubsystem);sub.close_all_editors_for_asset(bs);sub.open_editor_for_assets([bs]);assert A.save_loaded_asset(bs,only_if_is_dirty=False);sub.close_all_editors_for_asset(bs)
r['scope']='Forward run and sprint samples only. Walk, directional fight gaits, slots, abilities and movement parameters unchanged.'
(D/'implementation.json').write_text(json.dumps(r,indent=2));unreal.log('K02_FORWARD_RUNNING_REFINED')
