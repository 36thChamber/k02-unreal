"""Integrate the first three Fighter attacks using existing MACS/GAS contracts."""
import unreal,json
from pathlib import Path
ROOT='/Game/K02/Combat/Fighter/Montages'
A=unreal.EditorAssetLibrary
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(),'Stop PIE first'
configs=[('Jab','A_JabHead_L_IP','hand_l_Trace_Sphere'),('Cross','A_PunchHead_R_IP','hand_r_Trace_Sphere'),('HookStep','A_HookHead_L_M','hand_l_Trace_Sphere')]
assert not Path('A:/K-02 5.8/Saved/Diagnostics/fighter-combo-build.json').exists(),'Already built; edit existing montage explicitly instead'
for step in [1,2,3]:
 existing=unreal.get_default_object(A.load_blueprint_class('/Game/MACS/GAS/Abilities/Fighter/GA_MACS_Fighter_Combo_1_'+str(step)))
 assert existing.get_editor_property('AbilityMontage').get_path_name().startswith('/Game/MACS/'),'Already integrated; refusing to replace live montage assets'
report=[]
def copy_props(source,dest):
 schema=json.loads(unreal.ToolsetLibrary.list_struct_properties(source.get_class()))
 values=json.loads(unreal.ToolsetLibrary.get_object_properties(source,list(schema)))
 assert unreal.ToolsetLibrary.set_object_properties(dest,json.dumps(values))
for index,(name,clip,socket) in enumerate(configs,1):
 path=ROOT+'/AM_K02_Fighter_Light_'+str(index)+'_'+name
 if A.does_asset_exist(path):assert A.delete_asset(path),'Unable to remove incomplete montage'
 anim=unreal.load_asset('/Game/K02/Animations/FightAnimations/Manny/'+clip+'_Manny')
 if index==3:
  combat_seq='/Game/K02/Combat/Fighter/Sequences/AS_K02_Fighter_HookStep'
  if not A.does_asset_exist(combat_seq):assert A.duplicate_asset(anim.get_path_name(),combat_seq)
  anim=unreal.load_asset(combat_seq);unreal.AnimationLibrary.set_root_motion_enabled(anim,True);assert A.save_asset(combat_seq,only_if_is_dirty=False)
 old=unreal.load_asset('/Game/MACS/Animations/Fighter/AM_MACS_Fighter_Combo_1_'+str(index)+'_UE5')
 factory=unreal.AnimMontageFactory();factory.set_editor_property('SourceAnimation',anim);factory.set_editor_property('TargetSkeleton',anim.get_editor_property('Skeleton'))
 montage=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],ROOT,unreal.AnimMontage,factory)
 assert montage and abs(montage.get_play_length()-anim.get_play_length())<.0001
 slot_values=json.loads(unreal.ToolsetLibrary.get_object_properties(montage,['slotAnimTracks']))
 slot_values['slotAnimTracks'][0]['slotName']='FullBody'
 assert unreal.ToolsetLibrary.set_object_properties(montage,json.dumps(slot_values))
 blend=json.loads(unreal.ToolsetLibrary.get_object_properties(old,['blendIn','blendOut','blendOutTriggerTime','bEnableAutoBlendOut']))
 blend['blendIn']['blendTime']=.075;blend['blendOut']['blendTime']=.1
 assert unreal.ToolsetLibrary.set_object_properties(montage,json.dumps(blend))
 for track in ['K02_Combo','K02_Impact','K02_Audio']:unreal.AnimationLibrary.add_animation_notify_track(montage,track)
 events=[]
 for e in unreal.AnimationLibrary.get_animation_notify_events(old):
  state=e.get_editor_property('NotifyStateClass');notify=e.get_editor_property('Notify')
  if state:
   if 'ComboWindow' in state.get_class().get_name():
    start=.24;duration=.22;track='K02_Combo'
   elif 'TraceForTargets' in state.get_class().get_name():
    start=(9 if index==3 else 7)/30;duration=4/30;track='K02_Impact'
   else:raise RuntimeError('Unexpected notify state '+state.get_class().get_name())
   clone=unreal.AnimationLibrary.add_animation_notify_state_event(montage,track,start,duration,state.get_class())
   copy_props(state,clone)
   if 'TraceForTargets' in state.get_class().get_name():
    data=json.loads(unreal.ToolsetLibrary.get_object_properties(clone,['traceInfo']));data['traceInfo'][0]['socketsToTrace']=socket
    assert unreal.ToolsetLibrary.set_object_properties(clone,json.dumps(data))
   events.append({'state':clone.get_class().get_name(),'object':clone.get_path_name(),'start':start,'duration':duration,'track':track})
  elif notify:
   clone=unreal.AnimationLibrary.add_animation_notify_event(montage,'K02_Audio',(10 if index==3 else 8)/30,notify.get_class())
   copy_props(notify,clone)
 assert A.save_asset(path,only_if_is_dirty=False)
 report.append({'step':index,'montage':path,'animation':anim.get_path_name(),'length':montage.get_play_length(),'socket':socket,'notifies':events})
# Commit all three new montages before redirecting the existing data-only abilities.
for row in report:
 bp_path='/Game/MACS/GAS/Abilities/Fighter/GA_MACS_Fighter_Combo_1_'+str(row['step'])
 bp=unreal.load_asset(bp_path);cdo=unreal.get_default_object(A.load_blueprint_class(bp_path))
 cdo.set_editor_property('AbilityMontage',unreal.load_asset(row['montage']))
 unreal.BlueprintEditorLibrary.compile_blueprint(bp)
 assert A.save_asset(bp_path,only_if_is_dirty=False)
 row['ability']=bp_path
Path('A:/K-02 5.8/Saved/Diagnostics/fighter-combo-build.json').write_text(json.dumps(report,indent=2))
unreal.log('K02_FIGHTER_COMBO_BUILT 3 steps')
