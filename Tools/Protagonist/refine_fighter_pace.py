"""Keep Fighter arm guard on moving gaits; tune pace and share own moveset with arena AI."""
import unreal,json,math
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;R='/Game/K02/Protagonist';assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
def graph(bp,name):return next((g for g in B.list_graphs(bp) if g.get_name()==name),None)
def save(o):assert A.save_loaded_asset(o,only_if_is_dirty=False)
def compile(o):B.compile_blueprint(o,warnings_as_errors=True)
def T(s):return json.dumps('(TagName="MACS_GAS.Abilities.States.'+s+'")')
# Keep lower-body authored steps and torso weight transfer; copy only arm/finger guard tracks.
idle=unreal.load_asset('/Game/MACS/Animations/Fighter/AS_MACS_Fighter_Idle');opt=unreal.AnimPoseEvaluationOptions();opt.set_editor_property('should_retarget',False)
pose=idle.get_anim_pose_at_time(0,opt);bones=[str(b) for b in unreal.AnimPoseExtensions.get_bone_names(pose) if any(s in str(b) for s in ['clavicle_','upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_']) and not str(b).startswith('ik_')]
rows=[]
for p in A.list_assets(R+'/Locomotion/Sequences'):
 name=p.rsplit('/',1)[-1].split('.')[0]
 if not (name.startswith('AS_K02_Move_') or name.startswith('AS_K02_Run_')):continue
 a=unreal.load_asset(p);n=unreal.AnimationLibrary.get_num_frames(a);poses=[idle.get_anim_pose_at_time(idle.get_play_length()*i/n,opt) for i in range(n+1)]
 ctrl=a.controller
 for b in bones:
  ts=[unreal.AnimPoseExtensions.get_bone_pose(s,b,unreal.AnimPoseSpaces.LOCAL) for s in poses];assert ctrl.set_bone_track_keys(b,[t.translation for t in ts],[t.rotation for t in ts],[t.scale3d for t in ts])
 save(a);rows.append({'sequence':a.get_path_name(),'guardBones':len(bones),'frames':n})
# Actual speeds rather than only slowing animation playback, preserving planted-foot cadence.
sprint=unreal.load_asset(R+'/Abilities/GA_K02_Sprint');unreal.get_default_object(sprint.generated_class()).set_editor_property('SprintSpeed',520);compile(sprint);save(sprint)
defense=unreal.load_asset(R+'/Abilities/GA_K02_DefenseMode');unreal.get_default_object(defense.generated_class()).set_editor_property('MaxWalkSpeedWhenDefend',210);compile(defense);save(defense)
for name in ['BP_K02_Player','BP_K02_Enemy']:
 bp=unreal.load_asset('/Game/K02/Prototype/Blueprints/'+name);c=unreal.get_default_object(bp.generated_class());c.set_editor_property('MaxWalkSpeed',420 if 'Player' in name else 320);c.character_movement.set_editor_property('MaxWalkSpeed',420 if 'Player' in name else 320)
 c.character_movement.set_editor_property('MaxAcceleration',1600);c.character_movement.set_editor_property('BrakingDecelerationWalking',1600)
 g=graph(bp,'K02FighterPace') or unreal.BlueprintEditorLibrary.add_function_graph(bp,'K02FighterPace')
 code='''(fn K02FighterPace ()
  (if (and (Check|GameplayTagCheck self FIGHTER) (not (Check|GameplayTagCheck self CRAWL)))
   (bind _move (Actor|GetComponentByClass self "/Script/Engine.CharacterMovementComponent"))
   (if (Check|GameplayTagCheck self GUARD)
    (Class|CharacterMovementComponent|SetMaxWalkSpeed :self _move :MaxWalkSpeed 210)
    (else
     (Class|CharacterMovementComponent|SetMaxWalkSpeed :self _move :MaxWalkSpeed BASE)
     (if (Check|GameplayTagCheck self SPRINT) (Class|CharacterMovementComponent|SetMaxWalkSpeed :self _move :MaxWalkSpeed 520))
     PLAYERLOCK))))'''
 lock='''(bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Pawn|GetController self)))
 (Utilities|IsValid _pc (:"Is Valid"
  (if (> (Class|BPK02PlayerController|GetLockonMode _pc) 0)
   (Class|CharacterMovementComponent|SetMaxWalkSpeed :self _move :MaxWalkSpeed 240)
   (if (Check|GameplayTagCheck self SPRINT) (Class|CharacterMovementComponent|SetMaxWalkSpeed :self _move :MaxWalkSpeed 320)))))''' if 'Player' in name else ''
 code=code.replace('PLAYERLOCK',lock).replace('BASE','420' if 'Player' in name else '320')
 for key,val in [('FIGHTER','WeaponClass.Fighter'),('SPRINT','WeaponClass.Fighter.Sprint'),('GUARD','WeaponClass.Fighter.DefenseMode'),('CRAWL','Crawling')]:code=code.replace(key,T(val))
 B.write_graph_dsl(g,code);compile(bp)
 eg=graph(bp,'EventGraph');ed=unreal.BlueprintGraphEditor.get_graph_editor(eg);tick=next(n for n in B.find_nodes(eg) if n.get_node_title()=='Event Tick');pin=tick.find_then_pin()
 if not pin.list_connected_pins():n=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02FighterPace');assert pin.try_create_connection(n.find_execute_pin())
 if name=='BP_K02_Enemy':
  c=unreal.get_default_object(bp.generated_class())
  c.set_editor_property('K02FighterStyleEffect',A.load_blueprint_class(R+'/Abilities/GE_K02_Fighter'));c.mesh.set_editor_property('AnimClass',A.load_blueprint_class(R+'/Locomotion/ABP_K02_Player'))
  # Native hit data stays authoritative; own reactions use the same protagonist montages.
  g=graph(bp,'OnRep_HitReaction')
  if g:unreal.BlueprintEditorLibrary.remove_function_graph(bp,'OnRep_HitReaction')
  g=unreal.BlueprintEditorLibrary.add_function_override(bp,'OnRep_HitReaction');assert g
  B.write_graph_dsl(g,'''(fn OnRep_HitReaction ()
   (if (Pawn|IsLocallyControlled)
    (if (Check|GameplayTagCheck self FIGHTER)
     (Abilities|TryActivateAbilityByClass (Ability|GetAbilitySystemComponent self) "/Game/K02/Protagonist/Abilities/GA_K02_HitReactions.GA_K02_HitReactions_C")
     (else (Abilities|TryActivateAbilityByClass (Ability|GetAbilitySystemComponent self) "/Game/MACS/GAS/Abilities/Commun/GA_MACS_Commun_HitReactions.GA_MACS_Commun_HitReactions_C")))))'''.replace('FIGHTER',T('WeaponClass.Fighter')))
 compile(bp);save(bp)
# Same common graph for player and AI, but AI does not require a PlayerController.
bp=unreal.load_asset(R+'/Locomotion/ABP_K02_Commun');g=graph(bp,'EventGraph');B.write_graph_dsl(g,'''(event EventBlueprintUpdateAnimation (DeltaTimeX)
 (Variables|Default|SetK02CombatStance false)
 (bind _pawn (Utilities|Casting|CastToPawn (Animation|GetOwningActor)))
 (if (not (Pawn|IsPlayerControlled _pawn))
  (Variables|Default|SetK02CombatStance true)
  (else
   (if (Check|GameplayTagCheck _pawn GUARD) (Variables|Default|SetK02CombatStance true))
   (bind _pc (Utilities|Casting|CastToBP_K02_PlayerController (Pawn|GetController _pawn)))
   (Utilities|IsValid _pc (:"Is Valid"
    (if (> (Class|BPK02PlayerController|GetLockonMode _pc) 0)
     (Utilities|IsValid (Class|BPK02PlayerController|GetCurrentTarget _pc) (:"Is Valid" (Variables|Default|SetK02CombatStance true)))))))))'''.replace('GUARD',T('WeaponClass.Fighter.DefenseMode')));compile(bp);save(bp)
Path('A:/K-02 5.8/Saved/Diagnostics/CombatSlip/gaits.json').write_text(json.dumps(rows,indent=2));unreal.log('K02_FIGHTER_PACE_SHARED')
