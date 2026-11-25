"""Stage A: body jab -> body cross -> right low kick, protagonist only."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;ROOT='/Game/K02/Protagonist';MROOT='/Game/K02/Animations/Montages/Kyokushin';LIB='/Game/K02/Animations/FightAnimations/Manny/'
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
assert not A.does_asset_exist(MROOT+'/AM_K02_Kyokushin_M01'),'C01 already exists; use targeted update scripts'
def p(o,ks):return json.loads(unreal.ToolsetLibrary.get_object_properties(o,ks))
def setp(o,v):assert unreal.ToolsetLibrary.set_object_properties(o,json.dumps(v))
def save(o):assert A.save_loaded_asset(o,only_if_is_dirty=False)
def clone(src,dst):return unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(src,dst)
notify=clone('/Game/MACS/Animations/AnimNotify/ANS_MACS_ComboWindow',ROOT+'/Notifies/ANS_K02_ComboBranch')
for g in B.list_graphs(notify):
 if g.get_name()=='Received_NotifyTick':B.write_graph_dsl(g,Path('A:/K-02 5.8/Tools/Protagonist/branch_notify_tick.dsl').read_text())
 if g.get_name()=='Received_NotifyEnd':B.write_graph_dsl(g,'(fn Received_NotifyEnd (MeshComp Animation EventReference) (return true))')
save(notify)
tracecls=A.load_blueprint_class('/Game/MACS/Animations/AnimNotify/ANS_MACS_TraceForTargets')
rows=[]
# contact bounds measured from the actual retargeted hand/foot trajectories.
configs=[('M01','A_JabBody_L_IP','hand_l_Trace_Sphere','Combo_1_1',5,7,11,[('IA_MACS_HeavyAttack_1','1.2')]),('M02','A_PunchBody_R_IP','hand_r_Trace_Sphere','Combo_1_2',6,7,11,[('IA_MACS_Kick','1.3')]),('M06','A_LowKick_R','foot_r_Trace_Sphere','Combo_1_3',8,6,10,[])]
for mid,clip,socket,ability,damage,start,end,branches in configs:
 seq=clone(LIB+clip+'_Manny',ROOT+'/Combat/Sequences/AS_K02_'+mid);unreal.AnimationLibrary.set_root_motion_enabled(seq,mid=='M06');seq.set_editor_property('bForceRootLock',True);seq.set_editor_property('RootMotionRootLock',unreal.RootMotionRootLock.ANIM_FIRST_FRAME);save(seq)
 path=MROOT+'/AM_K02_Kyokushin_'+mid
 if A.does_asset_exist(path):m=unreal.load_asset(path);unreal.AnimationLibrary.remove_all_animation_notify_tracks(m)
 else:
  f=unreal.AnimMontageFactory();f.set_editor_property('SourceAnimation',seq);f.set_editor_property('TargetSkeleton',seq.get_editor_property('Skeleton'));m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[1],MROOT,unreal.AnimMontage,f)
 v=p(m,['slotAnimTracks','blendIn','blendOut']);v['slotAnimTracks'][0]['slotName']='FullBody';v['blendIn']['blendTime']=.075;v['blendOut']['blendTime']=.1;setp(m,v)
 for t in ['K02_Contact','K02_Branch']:unreal.AnimationLibrary.add_animation_notify_track(m,t)
 st=unreal.AnimationLibrary.add_animation_notify_state_event(m,'K02_Contact',start/30,(end-start)/30,tracecls)
 setp(st,{'traceInfo':[{'controlType':'Normal','damageType':'Smashing','socketsToTrace':socket,'damageMultiplier ':1}],'bShouldFireInEditor':False})
 for action,tag in branches:
  st=unreal.AnimationLibrary.add_animation_notify_state_event(m,'K02_Branch',.4,.2,notify.generated_class())
  setp(st,{'inputActionsToContinueCombo':[{'refPath':'/Game/MACS/Inputs/Abilities/'+action+'.'+action}],'nextComboAbilitiesTAGs':{'gameplayTags':[{'tagName':'MACS_GAS.Abilities.States.WeaponClass.Fighter.Combo.'+tag}]},'bShouldFireInEditor':False})
 save(m);bp=unreal.load_asset(ROOT+'/Abilities/GA_K02_'+ability);c=unreal.get_default_object(bp.generated_class());c.set_editor_property('AbilityMontage',m);c.set_editor_property('AbilityDamage',damage);unreal.BlueprintEditorLibrary.compile_blueprint(bp);save(bp)
 rows.append({'id':mid,'clip':clip,'montage':m.get_path_name(),'ability':bp.get_path_name(),'damage':damage,'contactFrames':[start,end],'comboWindow':[.4,.6] if branches else None,'socket':socket})
# Neutral F and K remain single safe entries; they cannot interrupt an active chain.
for name,mid in [('Combo_2_1','M02'),('Kick','M06')]:
 bp=unreal.load_asset(ROOT+'/Abilities/GA_K02_'+name);unreal.get_default_object(bp.generated_class()).set_editor_property('AbilityMontage',unreal.load_asset(MROOT+'/AM_K02_Kyokushin_'+mid));unreal.BlueprintEditorLibrary.compile_blueprint(bp);save(bp)
# Remove demo special attacks from the protagonist default style, retaining mobility/defense.
ge=unreal.load_asset(ROOT+'/Abilities/GE_K02_Fighter');cdo=unreal.get_default_object(ge.generated_class());comp=next(x for x in cdo.get_editor_property('GEComponents') if 'AbilitiesGameplayEffect' in x.get_class().get_name());v=p(comp,['grantAbilityConfigs'])
allowed=['Combo_1_1','Combo_1_2','Combo_1_3','Combo_2_1','Kick','DefenseMode','Dash','Escape','Sprint','RecoveryAlly']
v['grantAbilityConfigs']=[x for x in v['grantAbilityConfigs'] if any(x['ability']['refPath'].endswith('GA_K02_'+n+'_C') for n in allowed)];setp(comp,v);unreal.BlueprintEditorLibrary.compile_blueprint(ge);save(ge)
pc=unreal.load_asset(ROOT+'/Blueprints/BP_K02_PlayerController')
for g in B.list_graphs(pc):
 for n in B.find_nodes(g):
  pin=n.find_input_pin('InAbilityToActivate')
  if pin.is_valid() and pin.get_pin_value().endswith('GA_K02_Combo_4_1_C'):
   assert pin.set_pin_value(ROOT+'/Abilities/GA_K02_Combo_2_1.GA_K02_Combo_2_1_C')
unreal.BlueprintEditorLibrary.compile_blueprint(pc);save(pc)
Path('A:/K-02 5.8/Saved/Diagnostics/kyokushin-c01-build.json').write_text(json.dumps(rows,indent=2));unreal.log('K02_KYOKUSHIN_C01_BUILT')
