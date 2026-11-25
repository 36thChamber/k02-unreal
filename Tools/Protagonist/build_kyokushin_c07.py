"""C07 gated by the real MACS CounterAttack event; own assets only."""
import unreal,json,sys
from pathlib import Path
sys.path.insert(0,'A:/K-02 5.8/Tools/Protagonist')
from kyokushin_assets import *
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert 'K-02 5.8' in unreal.Paths.project_dir()
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
D=Path('A:/K-02 5.8/Saved/Diagnostics/C07');BASE='MACS_GAS.Abilities.States.'
def compile(bp):B.compile_blueprint(bp,warnings_as_errors=True);save(bp)
def graph(bp,n):return next((g for g in B.list_graphs(bp) if g.get_name()==n),None)
def fn(bp,n,code):
 g=graph(bp,n) or unreal.BlueprintEditorLibrary.add_function_graph(bp,n);B.write_graph_dsl(g,code);return g
def T(s):return json.dumps('(TagName="'+BASE+s+'")')
def ge(name):
 path=ROOT+'/Counter/'+name;bp=unreal.load_asset(path) if A.does_asset_exist(path) else None
 if not bp:
  f=unreal.BlueprintFactory();f.set_editor_property('ParentClass',unreal.GameplayEffect);bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,ROOT+'/Counter',unreal.Blueprint,f)
 setprops(unreal.get_default_object(bp.generated_class()),{'durationPolicy':'HasDuration','durationMagnitude':{'magnitudeCalculationType':'ScalableFloat','scalableFloatMagnitude':{'value':1}}});compile(bp);return bp.generated_class().get_path_name()
OP=ge('GE_K02_ParryOpportunity');CHAIN=ge('GE_K02_C07Followup')
def count(effect):return '(GameplayEffects|GetGameplayEffectCount (Ability|GetAbilitySystemComponentFromActorInfo) '+json.dumps(effect)+' 0 true)'
def remove(effect):return '(GameplayEffects|RemoveActiveGameplayEffectbySourceEffect (Ability|GetAbilitySystemComponentFromActorInfo) '+json.dumps(effect)+' 0 -1)'
def makeability(name,source,oldtag,newtag):
 bp=clone(ROOT+'/Abilities/GA_K02_'+source,ROOT+'/Abilities/GA_K02_'+name);c=unreal.get_default_object(bp.generated_class());v=props(c,['abilityTags','activationOwnedTags'])
 for container in v.values():
  for tag in container['gameplayTags']:tag['tagName']=tag['tagName'].replace('.Combo.'+oldtag,'.Combo.'+newtag)
 setprops(c,v);compile(bp);return bp
start=makeability('C07_Punch','Combo_2_1','2.1','5.2');kick=makeability('C07_MiddleKickLeft','C08_HookBodyLeft','4.4','5.3')
# Separate punch montage so ordinary M02 branches remain unchanged.
m=clone(MROOT+'/AM_K02_Kyokushin_M02',MROOT+'/AM_K02_Kyokushin_C07_Punch');unreal.AnimationLibrary.remove_animation_notify_track(m,'K02_Branch');unreal.AnimationLibrary.add_animation_notify_track(m,'K02_Branch')
st=unreal.AnimationLibrary.add_animation_notify_state_event(m,'K02_Branch',.4,.2,A.load_blueprint_class(ROOT+'/Notifies/ANS_K02_ComboBranch'));setprops(st,{'inputActionsToContinueCombo':[{'refPath':'/Game/MACS/Inputs/Abilities/IA_MACS_HeavyAttack_2.IA_MACS_HeavyAttack_2'}],'nextComboAbilitiesTAGs':{'gameplayTags':[{'tagName':BASE+'WeaponClass.Fighter.Combo.5.3'}]},'bShouldFireInEditor':False});save(m)
c=unreal.get_default_object(start.generated_class());c.set_editor_property('AbilityMontage',m);c.set_editor_property('AbilityDamage',6)
r=move('M09','A_MiddleKick_L','foot_l_Trace_Sphere','C07_MiddleKickLeft',10,7,11,True)
km=unreal.load_asset(MROOT+'/AM_K02_Kyokushin_M09');setprops(km,props(unreal.load_asset(MROOT+'/AM_K02_Kyokushin_M10'),['blendIn','blendOut']));save(km)
for bp,effect in [(start,OP),(kick,CHAIN)]:
 g=graph(bp,'K2_CanActivateAbility') or unreal.BlueprintEditorLibrary.add_function_override(bp,'K2_CanActivateAbility')
 B.write_graph_dsl(g,'(fn CanActivateAbility (ActorInfo Handle) (return "(GameplayTags=)" (> '+count(effect)+' 0)))');compile(bp)
grant(['C07_Punch','C07_MiddleKickLeft']);compile(unreal.load_asset(ROOT+'/Abilities/GE_K02_Fighter'))
# Lifecycle stays in the existing own base, including its montage and trace cleanup.
base=unreal.load_asset(ROOT+'/Abilities/GA_K02_Base_Combo')
fn(base,'K02BeginCounterCombo','(fn K02BeginCounterCombo () (if (Check|GameplayTagCheck (Ability|GetAvatarActorFromActorInfo) '+T('WeaponClass.Fighter.Combo.5.2')+') '+remove(OP)+' '+remove(CHAIN)+' (Ability|ApplyGameplayEffectToOwner :GameplayEffectClass '+json.dumps(CHAIN)+')) (if (Check|GameplayTagCheck (Ability|GetAvatarActorFromActorInfo) '+T('WeaponClass.Fighter.Combo.5.3')+') '+remove(CHAIN)+'))');compile(base)
g=graph(base,'Gameplay Ability Graph');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);event=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_Event' and 'ActivateAbility' in n.get_node_title());out=event.find_then_pin();pins=out.list_connected_pins();assert len(pins)==1
if 'K02BeginCounterCombo' not in pins[0].get_owning_node().get_node_title().replace(' ',''):
 n=ed.add_call_function_node(base.generated_class().get_path_name()+':K02BeginCounterCombo');out.break_single_pin_link(pins[0]);assert out.try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(pins[0])
compile(base)
# Additional event listener, preserving the existing parent nodes and guard cleanup.
bp=unreal.load_asset(ROOT+'/Abilities/GA_K02_DefenseMode');fn(bp,'K02RecordParrySuccess','(fn K02RecordParrySuccess () '+remove(OP)+' (Ability|ApplyGameplayEffectToOwner :GameplayEffectClass '+json.dumps(OP)+'))');compile(bp)
g=unreal.BlueprintEditorLibrary.find_event_graph(bp);ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
if not any('K02ListenCounterSuccess' in n.get_node_title() for n in B.find_nodes(g)):
 event=B.add_event(bp,'K02ListenCounterSuccess');wait=B.create_node(g,'Ability|Tasks|WaitGameplayEvent',unreal.IntPoint(250,1500));assert wait.find_input_pin('EventTag').set_pin_value('(TagName="MACS_GAS.Abilities.Events.CounterAttack")');assert event.find_then_pin().try_create_connection(wait.find_execute_pin());record=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02RecordParrySuccess');assert wait.find_output_pin('EventReceived').try_create_connection(record.find_execute_pin());compile(bp)
 suppress=next(n for n in B.find_nodes(g) if 'K02SuppressSlipParry' in n.get_node_title().replace(' ',''));listen=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02ListenCounterSuccess');assert suppress.find_then_pin().try_create_connection(listen.find_execute_pin())
compile(bp)
pc=unreal.load_asset(ROOT+'/Blueprints/BP_K02_PlayerController')
fn(pc,'K02FighterHeavyInput','''(fn K02FighterHeavyInput ()
 (bind _asc (Ability|GetAbilitySystemComponent (Variables|DoNotEdit|GetPawnRef)))
 (if (> (GameplayEffects|GetGameplayEffectCount _asc OP 0 true) 0)
  (if (Abilities|TryActivateAbilityByClass _asc START true) (return)))
 (Abilities|TryActivateAbilityByClass _asc NORMAL true))'''.replace('OP',json.dumps(OP)).replace('START',json.dumps(start.generated_class().get_path_name())).replace('NORMAL',json.dumps(ROOT+'/Abilities/GA_K02_Combo_2_1.GA_K02_Combo_2_1_C')))
fn(pc,'K02PruneParryOpportunity','''(fn K02PruneParryOpportunity ()
 (bind _p (Variables|DoNotEdit|GetPawnRef))
 (Utilities|IsValid _p (:"Is Valid"
 (bind _asc (Ability|GetAbilitySystemComponent _p))
 (if (or (not (Check|GameplayTagCheck _p FIGHTER)) (or (Check|GameplayTagCheck _p DEAD) (or (Check|GameplayTagCheck _p CC) (Check|GameplayTagCheck _p DASH))))
  (GameplayEffects|RemoveActiveGameplayEffectbySourceEffect _asc OP 0 -1)
  (GameplayEffects|RemoveActiveGameplayEffectbySourceEffect _asc CHAIN 0 -1))
 (if (Check|GameplayTagCheck _p COMBO) (GameplayEffects|RemoveActiveGameplayEffectbySourceEffect _asc OP 0 -1))
 (if (not (Check|GameplayTagCheck _p STARTTAG)) (GameplayEffects|RemoveActiveGameplayEffectbySourceEffect _asc CHAIN 0 -1)))))'''.replace('OP',json.dumps(OP)).replace('CHAIN',json.dumps(CHAIN)).replace('FIGHTER',T('WeaponClass.Fighter')).replace('DEAD',T('Dead')).replace('CC',T('CrowdControl')).replace('DASH',T('WeaponClass.Fighter.Dash')).replace('COMBO',T('WeaponClass.Fighter.Combo')).replace('STARTTAG',T('WeaponClass.Fighter.Combo.5.2')))
compile(pc)
g=graph(pc,'Abilities Classes');ed=unreal.BlueprintGraphEditor.get_graph_editor(g)
for n in B.find_nodes(g):
 p=n.find_input_pin('InAbilityToActivate')
 if p.is_valid() and p.get_pin_value().endswith('GA_K02_Combo_2_1_C'):
  incoming=n.find_execute_pin().list_connected_pins()
  if incoming:
   node=ed.add_call_function_node(pc.generated_class().get_path_name()+':K02FighterHeavyInput')
   for pin in incoming:pin.break_single_pin_link(n.find_execute_pin());assert pin.try_create_connection(node.find_execute_pin())
   for pin in n.find_then_pin().list_connected_pins():n.find_then_pin().break_single_pin_link(pin);assert node.find_then_pin().try_create_connection(pin)
g=graph(pc,'K02CombatInputTick');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);entry=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_FunctionEntry');out=entry.find_then_pin();pins=out.list_connected_pins();assert len(pins)==1
if 'K02PruneParryOpportunity' not in pins[0].get_owning_node().get_node_title().replace(' ',''):
 n=ed.add_call_function_node(pc.generated_class().get_path_name()+':K02PruneParryOpportunity');out.break_single_pin_link(pins[0]);assert out.try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(pins[0])
compile(pc);r.update({'opportunity':OP,'followup':CHAIN,'windowSeconds':1,'input':'confirmed parry,F,T'});(D/'build.json').write_text(json.dumps(r,indent=2));unreal.log('K02_C07_BUILT')
