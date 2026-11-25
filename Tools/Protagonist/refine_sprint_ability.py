"""Own sprint lifecycle: native GAS cost, paced movement, no demo ghost trail or camera shake."""
import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
bp=unreal.load_asset('/Game/K02/Protagonist/Abilities/GA_K02_Sprint')
c=unreal.get_default_object(bp.generated_class())
assert unreal.ToolsetLibrary.set_object_properties(c,json.dumps({'blockAbilitiesWithTag':{'gameplayTags':[]}}))
if 'K02SprintBaseSpeed' not in B.list_variables(bp):B.add_variable(bp,'K02SprintBaseSpeed','float')
B.compile_blueprint(bp,warnings_as_errors=True)
g=next((g for g in B.list_graphs(bp) if g.get_name()=='K02SprintCostLoop'),None) or unreal.BlueprintEditorLibrary.add_function_graph(bp,'K02SprintCostLoop')
B.write_graph_dsl(g,'''(fn K02SprintCostLoop ()
 (if (and (> (Math|Vector|VectorLength (Transformation|GetVelocity (Ability|GetAvatarActorFromActorInfo))) 10)
          (not (AI|Components|NavMovement|IsFalling (Actor|GetComponentByClass (Ability|GetAvatarActorFromActorInfo) "/Script/Engine.CharacterMovementComponent"))))
  (if (not (Ability|CommitAbilityCost :BroadcastCommitEvent true)) (Ability|EndAbility))
  (else (Ability|EndAbility))))''');B.compile_blueprint(bp,warnings_as_errors=True)
g=next(g for g in B.list_graphs(bp) if g.get_name()=='EventGraph');B.write_graph_dsl(g,'''(event Ability|EventActivateAbility
 (if (Ability|CommitAbility)
  (Variables|Default|SetK02SprintBaseSpeed (Class|CharacterMovementComponent|GetMaxWalkSpeed (Actor|GetComponentByClass (Ability|GetAvatarActorFromActorInfo) "/Script/Engine.CharacterMovementComponent")))
  (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "K02SprintCostLoop" :Time 0.1 :bLooping true)
  (Ability|Tasks|WaitGameplayEvent "(TagName=\\\"MACS_GAS.Abilities.Events.EndAbility\\\")"
   (:then (Ability|Tasks|WaitGameplayTagAdd "(TagName=\\\"MACS_GAS.Abilities.States.CrowdControl\\\")" (:Added (Ability|EndAbility))))
   (:EventReceived (Ability|EndAbility)))
  (else (Ability|EndAbility))))
(event Ability|EventOnEndAbility (bWasCancelled)
 (Utilities|Time|ClearTimerbyFunctionName :Object self :FunctionName "K02SprintCostLoop")
 (Class|CharacterMovementComponent|SetMaxWalkSpeed :self (Actor|GetComponentByClass (Ability|GetAvatarActorFromActorInfo) "/Script/Engine.CharacterMovementComponent") :MaxWalkSpeed (Variables|Default|GetK02SprintBaseSpeed)))''')
B.compile_blueprint(bp,warnings_as_errors=True);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('K02_SPRINT_LIFECYCLE_READY')
