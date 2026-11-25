"""Editor helpers for the MACS-owned move/notify configuration (no runtime Python)."""
import unreal,json
A=unreal.EditorAssetLibrary;ROOT='/Game/K02/Protagonist';MROOT='/Game/K02/Animations/Montages/Kyokushin';LIB='/Game/K02/Animations/FightAnimations/Manny/'
def props(o,ks):return json.loads(unreal.ToolsetLibrary.get_object_properties(o,ks))
def setprops(o,v):assert unreal.ToolsetLibrary.set_object_properties(o,json.dumps(v))
def save(o):assert A.save_loaded_asset(o,only_if_is_dirty=False)
def clone(src,dst):return unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(src,dst)
def ability(name):return unreal.load_asset(ROOT+'/Abilities/GA_K02_'+name)
def branches(mid,rows,opening=.4,closing=.6):
 m=unreal.load_asset(MROOT+'/AM_K02_Kyokushin_'+mid)
 if 'K02_Branch' in [str(x) for x in unreal.AnimationLibrary.get_animation_notify_track_names(m)]:unreal.AnimationLibrary.remove_animation_notify_track(m,'K02_Branch')
 unreal.AnimationLibrary.add_animation_notify_track(m,'K02_Branch')
 for action,tag in rows:
  st=unreal.AnimationLibrary.add_animation_notify_state_event(m,'K02_Branch',opening,closing-opening,A.load_blueprint_class(ROOT+'/Notifies/ANS_K02_ComboBranch'))
  setprops(st,{'inputActionsToContinueCombo':[{'refPath':'/Game/MACS/Inputs/Abilities/'+action+'.'+action}],'nextComboAbilitiesTAGs':{'gameplayTags':[{'tagName':'MACS_GAS.Abilities.States.WeaponClass.Fighter.Combo.'+tag}]},'bShouldFireInEditor':False})
 save(m)
def move(mid,clip,socket,abilityname,damage,start,end,root=False):
 seq=clone(LIB+clip+'_Manny',ROOT+'/Combat/Sequences/AS_K02_'+mid);unreal.AnimationLibrary.set_root_motion_enabled(seq,root);seq.set_editor_property('bForceRootLock',True);seq.set_editor_property('RootMotionRootLock',unreal.RootMotionRootLock.ANIM_FIRST_FRAME);save(seq)
 path=MROOT+'/AM_K02_Kyokushin_'+mid
 if A.does_asset_exist(path):m=unreal.load_asset(path);unreal.AnimationLibrary.remove_all_animation_notify_tracks(m)
 else:
  f=unreal.AnimMontageFactory();f.set_editor_property('SourceAnimation',seq);f.set_editor_property('TargetSkeleton',seq.get_editor_property('Skeleton'));m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],MROOT,unreal.AnimMontage,f)
 v=props(m,['slotAnimTracks','blendIn','blendOut']);v['slotAnimTracks'][0]['slotName']='FullBody';v['blendIn']['blendTime']=.075;v['blendOut']['blendTime']=.1;setprops(m,v)
 unreal.AnimationLibrary.add_animation_notify_track(m,'K02_Contact');st=unreal.AnimationLibrary.add_animation_notify_state_event(m,'K02_Contact',start/30,(end-start)/30,A.load_blueprint_class('/Game/MACS/Animations/AnimNotify/ANS_MACS_TraceForTargets'))
 setprops(st,{'traceInfo':[{'controlType':'Normal','damageType':'Smashing','socketsToTrace':socket,'damageMultiplier ':1}],'bShouldFireInEditor':False});save(m)
 bp=ability(abilityname);c=unreal.get_default_object(bp.generated_class());c.set_editor_property('AbilityMontage',m);c.set_editor_property('AbilityDamage',damage);unreal.BlueprintEditorLibrary.compile_blueprint(bp);save(bp)
 return {'id':mid,'montage':path,'clip':clip,'ability':bp.get_path_name(),'contactFrames':[start,end],'socket':socket,'rootMotion':root,'duration':m.get_play_length()}
def grant(names):
 ge=unreal.load_asset(ROOT+'/Abilities/GE_K02_Fighter');c=unreal.get_default_object(ge.generated_class());comp=next(x for x in c.get_editor_property('GEComponents') if 'AbilitiesGameplayEffect' in x.get_class().get_name());v=props(comp,['grantAbilityConfigs']);rows=v['grantAbilityConfigs'];template=rows[0]
 for name in names:
  bp=ability(name);ref=bp.generated_class().get_path_name()
  if not any(x['ability']['refPath']==ref for x in rows):
   row=json.loads(json.dumps(template));row['ability']={'refPath':ref};rows.append(row)
 setprops(comp,v);unreal.BlueprintEditorLibrary.compile_blueprint(ge);save(ge)
