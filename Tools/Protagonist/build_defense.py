"""Swap own protagonist defense/dash clips without changing MACS parry/hit rules."""
import unreal,json
from pathlib import Path
A=unreal.EditorAssetLibrary;ROOT='/Game/K02/Protagonist';LIB='/Game/K02/Animations/FightAnimations/Manny/'
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
def p(o,ks):return json.loads(unreal.ToolsetLibrary.get_object_properties(o,ks))
def setp(o,v):assert unreal.ToolsetLibrary.set_object_properties(o,json.dumps(v))
def save(o):assert A.save_loaded_asset(o,only_if_is_dirty=False)
def dup(src,dst):return unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(src,dst)
r=[]
def montage(old,clip,name):
 seq=dup(LIB+clip+'_Manny',ROOT+'/Defense/Sequences/AS_K02_'+clip[2:]);unreal.AnimationLibrary.set_root_motion_enabled(seq,False);seq.set_editor_property('bForceRootLock',True);seq.set_editor_property('RootMotionRootLock',unreal.RootMotionRootLock.ANIM_FIRST_FRAME);save(seq)
 m=dup(old.get_path_name(),ROOT+'/Defense/Montages/AM_K02_'+name);v=p(m,['slotAnimTracks','blendIn','blendOut']);seg=v['slotAnimTracks'][0]['animTrack']['animSegments'][0]
 seg['animReference']={'refPath':seq.get_path_name()};seg['animStartTime']=0;seg['animEndTime']=seq.get_play_length();seg['animPlayRate']=seq.get_play_length()/old.get_play_length();seg['cachedPlayLength']=seq.get_play_length()
 v['blendIn']['blendTime']=.08;v['blendOut']['blendTime']=.1;setp(m,v);save(m)
 r.append({'montage':m.get_path_name(),'sequence':seq.get_path_name(),'duration':m.get_play_length(),'slot':v['slotAnimTracks'][0]['slotName'],'clipRate':seg['animPlayRate']});return m
bp=unreal.load_asset(ROOT+'/Abilities/GA_K02_DefenseMode');c=unreal.get_default_object(bp.generated_class())
for key,clip,name in [('UpperBodyDefendMontage','A_Block_Idle','Guard_UpperBody'),('FullBodyDefendMontage','A_Block_Idle','Guard_FullBody'),('FullBodyHitBlockedMontage','A_BlockHit_F_IP','BlockHit_FullBody'),('UpperBodyHitBlockedMontage','A_BlockHit_F_IP','BlockHit_UpperBody')]:
 c.set_editor_property(key,montage(c.get_editor_property(key),clip,name))
unreal.BlueprintEditorLibrary.compile_blueprint(bp);save(bp)
for ability in ['Dash','Escape']:
 bp=unreal.load_asset(ROOT+'/Abilities/GA_K02_'+ability);c=unreal.get_default_object(bp.generated_class())
 for key,clip in [('ForwardMontage','A_Dodge_F'),('BackwardMontage','A_Dodge_B'),('LeftMontage','A_Dodge_L'),('RightMontage','A_Dodge_R')]:
  c.set_editor_property(key,montage(c.get_editor_property(key),clip,ability+'_'+key.replace('Montage','')))
 unreal.BlueprintEditorLibrary.compile_blueprint(bp);save(bp)
Path('A:/K-02 5.8/Saved/Diagnostics/protagonist-defense-build.json').write_text(json.dumps(r,indent=2));unreal.log('K02_PROTAGONIST_DEFENSE_BUILT')
