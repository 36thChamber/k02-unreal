"""K02 guard-compatible gaits, grounded commitment, shared AI style and GAS slip. Stop PIE; backup first."""
import unreal,json,copy
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;R='/Game/K02/Protagonist';D=Path('A:/K-02 5.8/Saved/Diagnostics/CombatSlip');assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
def get(o,k):return json.loads(unreal.ToolsetLibrary.get_object_properties(o,k))
def put(o,v):assert unreal.ToolsetLibrary.set_object_properties(o,json.dumps(v))
def save(o):assert A.save_loaded_asset(o,only_if_is_dirty=False)
def clone(src,dst):return unreal.load_asset(dst) if A.does_asset_exist(dst) else A.duplicate_asset(src,dst)
def graph(bp,name):return next((g for g in B.list_graphs(bp) if g.get_name()==name),None)
def fn(bp,name,code):
 g=graph(bp,name) or unreal.BlueprintEditorLibrary.add_function_graph(bp,name);B.write_graph_dsl(g,code);return g
def compile(bp):B.compile_blueprint(bp,warnings_as_errors=True)
def tag(s):return json.dumps('(TagName="'+s+'")')
F='MACS_GAS.Abilities.States.WeaponClass.Fighter';COMBO=F+'.Combo'
# Root motion is also the authority for stationary punches: zero root displacement replaces input velocity.
seqs=[]
for p in A.list_assets(R+'/Combat/Sequences'):
 a=unreal.load_asset(p)
 if isinstance(a,unreal.AnimSequence):unreal.AnimationLibrary.set_root_motion_enabled(a,True);save(a);seqs.append(a.get_path_name())
# Stop inherited velocity at activation, before the montage starts extracting root motion.
base=unreal.load_asset(R+'/Abilities/GA_K02_Base_Combo')
fn(base,'K02PlantForAttack','''(fn K02PlantForAttack ()
 (Components|Movement|StopMovementImmediately (Actor|GetComponentByClass (Ability|GetAvatarActorFromActorInfo) "/Script/Engine.CharacterMovementComponent")))''')
compile(base)
g=graph(base,'Gameplay Ability Graph');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);event=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_Event' and 'ActivateAbility' in n.get_node_title());outs=event.find_then_pin().list_connected_pins();assert len(outs)==1
if 'K02PlantForAttack' not in outs[0].get_owning_node().get_node_title().replace(' ',''):
 n=ed.add_call_function_node(base.generated_class().get_path_name()+':K02PlantForAttack');event.find_then_pin().break_single_pin_link(outs[0]);assert event.find_then_pin().try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(outs[0])
compile(base);save(base)
# Manual block is intentional even outside lock-on; automatic stance still requires lock-on.
defense=unreal.load_asset(R+'/Abilities/GA_K02_DefenseMode');fn(defense,'K02CheckGuardLock','(fn K02CheckGuardLock () (Variables|Default|SetK02GuardAllowed true))');compile(defense);save(defense)
# Directional slip montages. Short, planted, no synthetic launch/trail/capsule teleport.
montages={}
for name,clip in [('Forward','A_Slip_Up_L_Step'),('Backward','A_Slip_Back'),('Left','A_Slip_Left'),('Right','A_Slip_Right')]:
 a=clone('/Game/K02/Animations/FightAnimations/Manny/'+clip+'_Manny',R+'/Slip/Sequences/AS_K02_Slip_'+name);unreal.AnimationLibrary.set_root_motion_enabled(a,True);a.set_editor_property('bForceRootLock',True);a.set_editor_property('RootMotionRootLock',unreal.RootMotionRootLock.ANIM_FIRST_FRAME);save(a)
 p=R+'/Slip/Montages/AM_K02_Slip_'+name
 if A.does_asset_exist(p):m=unreal.load_asset(p)
 else:
  f=unreal.AnimMontageFactory();f.set_editor_property('SourceAnimation',a);f.set_editor_property('TargetSkeleton',a.get_editor_property('Skeleton'));m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(p.rsplit('/',1)[1],p.rsplit('/',1)[0],unreal.AnimMontage,f)
 v=get(m,['slotAnimTracks','blendIn','blendOut']);v['slotAnimTracks'][0]['slotName']='FullBody'
 for key,t in [('blendIn',.07),('blendOut',.12)]:v[key].update(blendTime=t,blendOption='HermiteCubic')
 put(m,v);m.set_editor_property('RateScale',max(1,a.get_play_length()/.48));save(m);montages[name]=m.get_path_name()
# Immunity matches only native incoming damage definitions: healing, buffs and ability costs still work.
p=R+'/Slip/GE_K02_SlipIFrames'
if A.does_asset_exist(p):ge=unreal.load_asset(p)
else:
 f=unreal.BlueprintFactory();f.set_editor_property('ParentClass',unreal.GameplayEffect);ge=unreal.AssetToolsHelpers.get_asset_tools().create_asset('GE_K02_SlipIFrames',R+'/Slip',unreal.Blueprint,f)
c=unreal.get_default_object(ge.generated_class());put(c,{'durationPolicy':'HasDuration','durationMagnitude':{'magnitudeCalculationType':'ScalableFloat','scalableFloatMagnitude':{'value':.14}}})
components=list(c.get_editor_property('GEComponents'));imm=next((x for x in components if 'Immunity' in x.get_class().get_name()),None)
if not imm:imm=unreal.new_object(unreal.load_class(None,'/Script/GameplayAbilities.ImmunityGameplayEffectComponent'),outer=c);components.append(imm);c.set_editor_property('GEComponents',components)
queries=[]
for n in ['Health','Shield','Stamina','CrawlingHealth']:queries.append({'effectDefinition':{'refPath':'/Game/MACS/GAS/Effects/SetByCaller/GE_MACS_SetByCaller_CalculateDamage_'+n+'.GE_MACS_SetByCaller_CalculateDamage_'+n+'_C'}})
put(imm,{'immunityQueries':queries});compile(ge);save(ge)
# Dedicated GAS ability: immunity starts at 0.04s, ends at 0.18s; the rest is vulnerable recovery.
p=R+'/Abilities/GA_K02_Slip'
if A.does_asset_exist(p):slip=unreal.load_asset(p)
else:
 f=unreal.BlueprintFactory();f.set_editor_property('ParentClass',unreal.GameplayAbility);slip=unreal.AssetToolsHelpers.get_asset_tools().create_asset('GA_K02_Slip',R+'/Abilities',unreal.Blueprint,f)
c=unreal.get_default_object(slip.generated_class());put(c,{'instancingPolicy':'InstancedPerActor','netExecutionPolicy':'LocalPredicted','activationOwnedTags':{'gameplayTags':[{'tagName':F+'.Dash'},{'tagName':'MACS_GAS.Abilities.States.UsingAbility.Fighter'}]},'activationRequiredTags':{'gameplayTags':[{'tagName':F},{'tagName':'MACS_GAS.Abilities.States.IsGroundMovement'}]},'activationBlockedTags':{'gameplayTags':[{'tagName':s} for s in [COMBO,F+'.Dash',F+'.Escape','MACS_GAS.Abilities.States.Dead','MACS_GAS.Abilities.States.CrowdControl','MACS_GAS.Abilities.States.GetUp']]},'cancelAbilitiesWithTag':{'gameplayTags':[{'tagName':F+'.DefenseMode'},{'tagName':F+'.Sprint'}]},'blockAbilitiesWithTag':{'gameplayTags':[{'tagName':F}]}})
# Reuse native directional selection variable on the actor; controller sets it camera-relative.
if 'K02SlipMontage' not in B.list_variables(slip):
 typ=unreal.BlueprintEditorLibrary.get_object_reference_type(unreal.AnimMontage);assert unreal.BlueprintEditorLibrary.add_member_variable(slip,'K02SlipMontage',typ)
compile(slip)
code='''(fn K02SelectSlip ()
 (Variables|Default|SetK02SlipMontage "BACKWARD")
 (bind _pawn (Utilities|Casting|CastToPawn (Ability|GetAvatarActorFromActorInfo)))
 (bind _pc (Utilities|Casting|CastToPlayerController (Pawn|GetController _pawn)))
 (Utilities|IsValid _pc (:"Is Valid"
 (bind _f (- (Game|Player|GetInputAnalogKeyState _pc "W") (Game|Player|GetInputAnalogKeyState _pc "S")))
 (bind _r (- (Game|Player|GetInputAnalogKeyState _pc "D") (Game|Player|GetInputAnalogKeyState _pc "A")))
 (bind _world (+ (* (Math|Vector|GetForwardVector (Pawn|GetControlRotation _pc)) _f) (* (Math|Vector|GetRightVector (Pawn|GetControlRotation _pc)) _r)))
 (bind _forward (Math|Vector|DotProduct _world (Transformation|GetActorForwardVector _pawn)))
 (bind _right (Math|Vector|DotProduct _world (Transformation|GetActorRightVector _pawn)))
 (if (>= (* _forward _forward) (* _right _right))
 (if (> _forward 0) (Variables|Default|SetK02SlipMontage "FORWARD") (else (Variables|Default|SetK02SlipMontage "BACKWARD")))
 (else (if (> _right 0) (Variables|Default|SetK02SlipMontage "RIGHT") (else (Variables|Default|SetK02SlipMontage "LEFT"))))))))'''
for k,v in montages.items():code=code.replace(k.upper(),v)
fn(slip,'K02SelectSlip',code);compile(slip)
g=graph(slip,'EventGraph');B.write_graph_dsl(g,'''(event Ability|EventActivateAbility
 (Ability|CommitAbility)
 (Components|Movement|StopMovementImmediately (Actor|GetComponentByClass (Ability|GetAvatarActorFromActorInfo) "/Script/Engine.CharacterMovementComponent"))
 (CallFunction|K02SelectSlip)
 (Ability|Tasks|PlayMontageAndWait "None" (Variables|Default|GetK02SlipMontage) :bAllowInterruptAfterBlendOut true
  (:then (Ability|Tasks|WaitDelay 0.04 (:OnFinish (Ability|ApplyGameplayEffectToOwner :GameplayEffectClass "/Game/K02/Protagonist/Slip/GE_K02_SlipIFrames.GE_K02_SlipIFrames_C"))))
  (:OnCompleted (Ability|EndAbility)) (:OnInterrupted (Ability|EndAbility)) (:OnCancelled (Ability|EndAbility))))''');compile(slip);save(slip)
# Grant once through existing Fighter effect.
ge=unreal.load_asset(R+'/Abilities/GE_K02_Fighter');c=unreal.get_default_object(ge.generated_class());comp=next(x for x in c.get_editor_property('GEComponents') if 'AbilitiesGameplayEffect' in x.get_class().get_name());v=get(comp,['grantAbilityConfigs']);rows=v['grantAbilityConfigs']
if not any('GA_K02_Slip_C' in json.dumps(row) for row in rows):row=copy.deepcopy(rows[0]);row['ability']={'refPath':slip.generated_class().get_path_name()};rows.append(row)
put(comp,v);compile(ge);save(ge)
(D/'built.json').write_text(json.dumps({'rootAuthoritySequences':seqs,'slipMontages':montages,'immunitySeconds':.14,'immunityStart':.04},indent=2));unreal.log('K02_COMBAT_SLIP_ASSETS_BUILT')
