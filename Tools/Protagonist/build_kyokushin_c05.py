"""C05: confirmed low block -> right straight -> right low kick. Own assets only."""
import json, sys, unreal
from pathlib import Path
sys.path.insert(0, 'A:/K-02 5.8/Tools/Protagonist')
from kyokushin_assets import *
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert 'K-02 5.8' in unreal.Paths.project_dir()
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
# C05 state tags are registered in Config/Tags/K02GameplayTags.ini.
D=Path('A:/K-02 5.8/Saved/Diagnostics/C05');D.mkdir(exist_ok=True)
BASE='MACS_GAS.Abilities.States.'
tagtool=unreal.get_default_object(unreal.load_class(None,'/Script/GameplayTagsToolset.GameplayTagsToolset'))
registered=set(tagtool.call_method('ListTags',args=(BASE+'WeaponClass.Fighter.Combo',)))
assert all(BASE+'WeaponClass.Fighter.Combo.'+t in registered for t in ['3.1','3.2']), 'Load Config/Tags/K02GameplayTags.ini before building C05'
def compile(bp):
 B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property("Status") == unreal.BlueprintStatus.BS_UP_TO_DATE,bp.get_path_name();save(bp)
def graph(bp,n):return next((g for g in B.list_graphs(bp) if g.get_name()==n),None)
def fn(bp,n,code,params=()):
 g=graph(bp,n)
 if not g:
  g=B.add_function_graph(bp,n);ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
  for name,typ in params:
   if typ=='Actor':ed.add_graph_input_parameter(name,unreal.BlueprintEditorLibrary.get_object_reference_type(unreal.Actor.static_class()))
   elif typ=='HitResult':ed.add_graph_input_parameter(name,unreal.BlueprintEditorLibrary.get_struct_type(unreal.HitResult.static_struct()))
   else:B.add_function_param(g,name,typ,True)
 for n0 in list(B.find_nodes(g)):
  if n0.get_class().get_name()!='K2Node_FunctionEntry':B.delete_node(n0)
 B.write_graph_dsl(g,code)
 return g
def T(s):return json.dumps('(TagName="'+BASE+s+'")')
def ge(name,seconds):
 path=ROOT+'/Counter/'+name;bp=unreal.load_asset(path) if A.does_asset_exist(path) else None
 if not bp:
  f=unreal.BlueprintFactory();f.set_editor_property('ParentClass',unreal.GameplayEffect);bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,ROOT+'/Counter',unreal.Blueprint,f)
 setprops(unreal.get_default_object(bp.generated_class()),{'durationPolicy':'HasDuration','durationMagnitude':{'magnitudeCalculationType':'ScalableFloat','scalableFloatMagnitude':{'value':seconds}}});compile(bp);return bp.generated_class().get_path_name()
OP=ge('GE_K02_LowBlockOpportunity',1.0);CHAIN=ge('GE_K02_C05Followup',1.0);CONTACT=ge('GE_K02_LowBlockContact',.05)
def count(effect,asc='(Ability|GetAbilitySystemComponentFromActorInfo)'):return '(GameplayEffects|GetGameplayEffectCount '+asc+' '+json.dumps(effect)+' 0 true)'
def remove(effect,asc='(Ability|GetAbilitySystemComponentFromActorInfo)'):return '(GameplayEffects|RemoveActiveGameplayEffectbySourceEffect '+asc+' '+json.dumps(effect)+' 0 -1)'
def apply(effect):return '(Ability|ApplyGameplayEffectToOwner :GameplayEffectClass '+json.dumps(effect)+')'
def makeability(name,source,oldtag,newtag):
 bp=clone(ROOT+'/Abilities/GA_K02_'+source,ROOT+'/Abilities/GA_K02_'+name);c=unreal.get_default_object(bp.generated_class());v=props(c,['abilityTags','activationOwnedTags'])
 for container in v.values():
  for tag in container['gameplayTags']:tag['tagName']=tag['tagName'].replace('.Combo.'+oldtag,'.Combo.'+newtag)
 setprops(c,v);compile(bp);return bp
start=makeability('C05_Punch','Combo_2_1','2.1','3.1');kick=makeability('C05_LowKickRight','Combo_1_3','1.3','3.2')
for mid,src in [('C05_Punch','M02'),('C05_LowKickRight','M06')]:
 m=clone(MROOT+'/AM_K02_Kyokushin_'+src,MROOT+'/AM_K02_Kyokushin_'+mid)
 for event in unreal.AnimationLibrary.get_animation_notify_events(m):
  state=event.get_editor_property('NotifyStateClass')
  if state and 'ComboBranch' in state.get_class().get_name():unreal.AnimationLibrary.remove_animation_notify_events_by_name(m,event.get_editor_property('NotifyName'))
 save(m)
branches('C05_Punch',[('IA_MACS_Kick','3.2')])
for bp,mid,effect in [(start,'C05_Punch',OP),(kick,'C05_LowKickRight',CHAIN)]:
 unreal.get_default_object(bp.generated_class()).set_editor_property('AbilityMontage',unreal.load_asset(MROOT+'/AM_K02_Kyokushin_'+mid))
 g=graph(bp,'K2_CanActivateAbility') or unreal.BlueprintEditorLibrary.add_function_override(bp,'K2_CanActivateAbility')
 B.write_graph_dsl(g,'(fn CanActivateAbility (ActorInfo Handle) (return "(GameplayTags=)" (> '+count(effect)+' 0)))');compile(bp)
grant(['C05_Punch','C05_LowKickRight']);compile(unreal.load_asset(ROOT+'/Abilities/GE_K02_Fighter'))
# Separate own check reaction, preserving the licensed retarget source.
seq=clone(LIB+'A_Block_Leg_Manny',ROOT+'/Counter/Sequences/AS_K02_LowBlock')
unreal.AnimationLibrary.set_root_motion_enabled(seq,False);seq.set_editor_property('bForceRootLock',True);save(seq)
path=ROOT+'/Counter/Montages/AM_K02_LowBlock'
if A.does_asset_exist(path):m=unreal.load_asset(path)
else:
 f=unreal.AnimMontageFactory();f.set_editor_property('SourceAnimation',seq);f.set_editor_property('TargetSkeleton',seq.get_editor_property('Skeleton'));m=unreal.AssetToolsHelpers.get_asset_tools().create_asset('AM_K02_LowBlock',ROOT+'/Counter/Montages',unreal.AnimMontage,f)
v=props(m,['slotAnimTracks','blendIn','blendOut']);v['slotAnimTracks'][0]['slotName']='FullBody';v['blendIn']['blendTime']=.08;v['blendOut']['blendTime']=.14;setprops(m,v);save(m)
# Hook only the confirmed-block execution branch. Classification also requires a
# measured low impact and an active, already integrated K02 low-kick ability.
hit=unreal.load_asset(ROOT+'/Abilities/GA_K02_HitReactions')
code='''(fn K02RecordLowBlock (Hit Attacker)
 REMOVE_CONTACT
 (bind _p (Ability|GetAvatarActorFromActorInfo))
 (bind (_blocking _penetrating _time _distance _location _impact) (Collision|BreakHitResult Hit))
 (bind _relative (- _impact (Transformation|GetActorLocation _p)))
 (bind (_x _y _z) (Math|Vector|BreakVector _relative))
 (bind _toward (- (Transformation|GetActorLocation Attacker) (Transformation|GetActorLocation _p)))
 (bind _front (Math|Vector|DotProduct _toward (Transformation|GetActorForwardVector _p)))
 (if (and (> _front 0) (and (Check|GameplayTagCheck _p FIGHTER) (and (< _z -15) (> _z -85))))
  (if (or (Check|GameplayTagCheck Attacker LOWR) (or (Check|GameplayTagCheck Attacker LOWL) (or (Check|GameplayTagCheck Attacker C05KICK) (Check|GameplayTagCheck Attacker KICK))))
   APPLY_CONTACT
   (if (not (Check|GameplayTagCheck _p COUNTER)) REMOVE_OP APPLY_OP))))'''
for k,v in {'REMOVE_CONTACT':remove(CONTACT),'REMOVE_OP':remove(OP),'APPLY_CONTACT':apply(CONTACT),'APPLY_OP':apply(OP),'FIGHTER':T('WeaponClass.Fighter'),'LOWR':T('WeaponClass.Fighter.Combo.1.3'),'LOWL':T('WeaponClass.Fighter.Combo.2.3'),'C05KICK':T('WeaponClass.Fighter.Combo.3.2'),'KICK':T('WeaponClass.Fighter.Kick'),'COUNTER':T('CounterWindow')}.items():code=code.replace(k,v)
fn(hit,'K02RecordLowBlock',code,[('Hit','HitResult'),('Attacker','Actor')]);compile(hit)
g=graph(hit,'EndAbilityIfHitCanBeBlocked');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
send=next(n for n in B.find_nodes(g) if 'SendGameplayEvent' in n.get_node_title());incoming=send.find_execute_pin().list_connected_pins()
if not any('K02RecordLowBlock' in p.get_owning_node().get_node_title().replace(' ','') for p in incoming):
 node=ed.add_call_function_node(hit.generated_class().get_path_name()+':K02RecordLowBlock')
 source=next(n for n in B.find_nodes(g) if any('HitReaction_HitResult' in p.name for p in B._get_node_info(n).output_pins))
 for p in B._get_node_info(source).output_pins:
  if 'HitReaction_HitResult' in p.name:assert source.find_output_pin(p.name).try_create_connection(node.find_input_pin('Hit'))
  if 'HitReaction_Instigator' in p.name:assert source.find_output_pin(p.name).try_create_connection(node.find_input_pin('Attacker'))
 for p in incoming:p.break_single_pin_link(send.find_execute_pin());assert p.try_create_connection(node.find_execute_pin())
 assert node.find_then_pin().try_create_connection(send.find_execute_pin())
compile(hit)
# The native block task owns montage lifetime/timer recovery. Select our full-body
# check for this contact, and rejoin its existing completion path.
guard=unreal.load_asset(ROOT+'/Abilities/GA_K02_Base_DefenseMode')
if 'K02LowBlockContact' not in B.list_variables(guard):B.add_variable(guard,'K02LowBlockContact','bool')
fn(guard,'K02HasLowBlockContact','(fn K02HasLowBlockContact () (Variables|Default|SetK02LowBlockContact (> '+count(CONTACT)+' 0)))');compile(guard)
g=graph(guard,'Gameplay Ability Graph');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
pause=next(n for n in B.find_nodes(g) if n.get_name()=='K2Node_CallFunction_15');out=pause.find_then_pin();old=out.list_connected_pins()
if not any('K02HasLowBlockContact' in p.get_owning_node().get_node_title().replace(' ','') for p in old):
 check=ed.add_call_function_node(guard.generated_class().get_path_name()+':K02HasLowBlockContact');branch=ed.add_branch_node()
 for p in old:out.break_single_pin_link(p);assert branch.find_output_pin('else').try_create_connection(p)
 assert out.try_create_connection(check.find_execute_pin());assert check.find_then_pin().try_create_connection(branch.find_execute_pin());value=B.create_node(g,'Variables|Default|GetK02LowBlockContact',unreal.IntPoint(1400,2300));assert value.find_output_pin('K02LowBlockContact').try_create_connection(branch.find_input_pin('Condition'))
 play=B.create_node(g,'Ability|Tasks|PlayMontageAndWait',unreal.IntPoint(1500,2300));assert play.find_input_pin('MontageToPlay').set_pin_value(m.get_path_name());assert play.find_input_pin('bAllowInterruptAfterBlendOut').set_pin_value('true');assert branch.find_then_pin().try_create_connection(play.find_execute_pin())
 unpause=next(n for n in B.find_nodes(g) if n.get_name()=='K2Node_CallFunction_16')
 for pname in ['OnCompleted','OnBlendOut','OnInterrupted','OnCancelled']:assert play.find_output_pin(pname).try_create_connection(unpause.find_execute_pin())
compile(guard);compile(unreal.load_asset(ROOT+'/Abilities/GA_K02_DefenseMode'))
base=unreal.load_asset(ROOT+'/Abilities/GA_K02_Base_Combo')
fn(base,'K02BeginLowBlockCombo','(fn K02BeginLowBlockCombo () (if (Check|GameplayTagCheck (Ability|GetAvatarActorFromActorInfo) '+T('WeaponClass.Fighter.Combo.3.1')+') '+remove(OP)+' '+remove(CHAIN)+' '+apply(CHAIN)+') (if (Check|GameplayTagCheck (Ability|GetAvatarActorFromActorInfo) '+T('WeaponClass.Fighter.Combo.3.2')+') '+remove(CHAIN)+'))');compile(base)
g=graph(base,'Gameplay Ability Graph');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);n=next(n for n in B.find_nodes(g) if 'K02BeginCounterCombo' in n.get_node_title().replace(' ',''));out=n.find_then_pin();old=out.list_connected_pins()
if not any('K02BeginLowBlockCombo' in p.get_owning_node().get_node_title().replace(' ','') for p in old):
 hook=ed.add_call_function_node(base.generated_class().get_path_name()+':K02BeginLowBlockCombo')
 for p in old:out.break_single_pin_link(p);assert hook.find_then_pin().try_create_connection(p)
 assert out.try_create_connection(hook.find_execute_pin())
compile(base)
pc=unreal.load_asset(ROOT+'/Blueprints/BP_K02_PlayerController')
PAR=ROOT+'/Counter/GE_K02_ParryOpportunity.GE_K02_ParryOpportunity_C'
fn(pc,'K02FighterHeavyInput','''(fn K02FighterHeavyInput ()
 (bind _asc (Ability|GetAbilitySystemComponent (Variables|DoNotEdit|GetPawnRef)))
 (if (> PAR_COUNT 0) (if (Abilities|TryActivateAbilityByClass _asc PAR_ABILITY true) (return)))
 (if (> OP_COUNT 0) (if (Abilities|TryActivateAbilityByClass _asc C05_ABILITY true) (return)))
 (Abilities|TryActivateAbilityByClass _asc NORMAL true))'''.replace('PAR_COUNT',count(PAR,'_asc')).replace('OP_COUNT',count(OP,'_asc')).replace('PAR_ABILITY',json.dumps(ROOT+'/Abilities/GA_K02_C07_Punch.GA_K02_C07_Punch_C')).replace('C05_ABILITY',json.dumps(start.generated_class().get_path_name())).replace('NORMAL',json.dumps(ROOT+'/Abilities/GA_K02_Combo_2_1.GA_K02_Combo_2_1_C')))
fn(pc,'K02PruneLowBlockOpportunity','''(fn K02PruneLowBlockOpportunity ()
 (bind _p (Variables|DoNotEdit|GetPawnRef))
 (Utilities|IsValid _p (:"Is Valid"
 (bind _asc (Ability|GetAbilitySystemComponent _p))
 (if (or (not (Check|GameplayTagCheck _p FIGHTER)) (or (Check|GameplayTagCheck _p DEAD) (or (Check|GameplayTagCheck _p CC) (Check|GameplayTagCheck _p DASH)))) REMOVE_OP REMOVE_CHAIN)
 (if (Check|GameplayTagCheck _p COMBO) REMOVE_OP)
 (if (not (Check|GameplayTagCheck _p STARTTAG)) REMOVE_CHAIN))))'''.replace('REMOVE_OP',remove(OP,'_asc')).replace('REMOVE_CHAIN',remove(CHAIN,'_asc')).replace('FIGHTER',T('WeaponClass.Fighter')).replace('DEAD',T('Dead')).replace('CC',T('CrowdControl')).replace('DASH',T('WeaponClass.Fighter.Dash')).replace('COMBO',T('WeaponClass.Fighter.Combo')).replace('STARTTAG',T('WeaponClass.Fighter.Combo.3.1')))
compile(pc)
g=graph(pc,'K02CombatInputTick');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);n=next(n for n in B.find_nodes(g) if 'K02PruneParryOpportunity' in n.get_node_title().replace(' ',''));out=n.find_then_pin();old=out.list_connected_pins()
if not any('K02PruneLowBlockOpportunity' in p.get_owning_node().get_node_title().replace(' ','') for p in old):
 hook=ed.add_call_function_node(pc.generated_class().get_path_name()+':K02PruneLowBlockOpportunity')
 for p in old:out.break_single_pin_link(p);assert hook.find_then_pin().try_create_connection(p)
 assert out.try_create_connection(hook.find_execute_pin())
compile(pc)
(D/'build.json').write_text(json.dumps({'opportunity':OP,'followup':CHAIN,'contact':CONTACT,'windowSeconds':1,'input':'confirmed low block,F,K','classification':'front-facing attacker plus actual impact -85 < z relative capsule < -15 plus active K02 low kick'},indent=2))
unreal.log('K02_C05_BUILT')
