"""Buffered combo inputs and explicit Ctrl block/slip, own controller only."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
A=unreal.EditorAssetLibrary;R='/Game/K02/Protagonist';assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
def graph(bp,name):return next((g for g in B.list_graphs(bp) if g.get_name()==name),None)
def fn(bp,name,code):
 g=graph(bp,name) or unreal.BlueprintEditorLibrary.add_function_graph(bp,name);B.write_graph_dsl(g,code);return g
def compile(bp):B.compile_blueprint(bp,warnings_as_errors=True)
def save(bp):assert A.save_loaded_asset(bp,only_if_is_dirty=False)
def T(s):return json.dumps('(TagName="MACS_GAS.Abilities.States.'+s+'")')
pc=unreal.load_asset(R+'/Blueprints/BP_K02_PlayerController')
keys=[('P','LeftMouseButton'),('F','RightMouseButton'),('K','E'),('T','R')]
for name,key in keys:
 if 'K02Buffered'+name not in B.list_variables(pc):B.add_variable(pc,'K02Buffered'+name,'float')
compile(pc);c=unreal.get_default_object(pc.generated_class())
for name,key in keys:c.set_editor_property('K02Buffered'+name,-100)
code='''(fn K02CombatInputTick ()
 (bind _pawn (Variables|DoNotEdit|GetPawnRef))
 (Utilities|IsValid _pawn (:"Is Valid"
 (if (Check|GameplayTagCheck _pawn FIGHTER)
  (bind _asc (Ability|GetAbilitySystemComponent _pawn))
  (bind _now (Utilities|Time|GetTimeSeconds))
  (if (Check|GameplayTagCheck _pawn COMBO)
   CAPTURE)
  (if (Game|Player|IsInputKeyDown self "LeftControl")
   (if (and (or (or (Game|Player|IsInputKeyDown self "W") (Game|Player|IsInputKeyDown self "S")) (or (Game|Player|IsInputKeyDown self "A") (Game|Player|IsInputKeyDown self "D")))
     (or (Game|Player|WasInputKeyJustPressed self "LeftControl") (or (or (Game|Player|WasInputKeyJustPressed self "W") (Game|Player|WasInputKeyJustPressed self "S")) (or (Game|Player|WasInputKeyJustPressed self "A") (Game|Player|WasInputKeyJustPressed self "D")))))
    (Abilities|TryActivateAbilityByClass _asc "/Game/K02/Protagonist/Abilities/GA_K02_Slip.GA_K02_Slip_C" true)
    (else
     (if (and (not (Check|GameplayTagCheck _pawn GUARD)) (and (not (Check|GameplayTagCheck _pawn COMBO)) (not (Check|GameplayTagCheck _pawn DASH))))
      (Abilities|TryActivateAbilityByClass _asc "/Game/K02/Protagonist/Abilities/GA_K02_DefenseMode.GA_K02_DefenseMode_C" true))))
   (else
    (if (and (Game|Player|WasInputKeyJustReleased self "LeftControl") (Check|GameplayTagCheck _pawn GUARD))
     (Ability|SendGameplayEventToActor _pawn "(TagName=\\\"MACS_GAS.Abilities.Events.EndAbility\\\")"))))))))'''
# Ignore initial click of a newly started move. Subsequent taps are held until a legal branch window.
cap=[]
for name,key in keys:cap.append('(if (and (> (Animation|Montage|MontageGetPosition (Components|SkeletalMesh|GetAnimInstance (Class|Character|GetMesh _pawn)) (Animation|GetCurrentMontage _pawn)) 0.08) (Game|Player|WasInputKeyJustPressed self "'+key+'")) (Variables|Default|SetK02Buffered'+name+' _now))')
code=code.replace('CAPTURE','\n'.join(cap))
for k,v in [('FIGHTER','WeaponClass.Fighter'),('COMBO','WeaponClass.Fighter.Combo'),('GUARD','WeaponClass.Fighter.DefenseMode'),('DASH','WeaponClass.Fighter.Dash')]:code=code.replace(k,T(v))
fn(pc,'K02CombatInputTick',code)
g=graph(pc,'K02ConsumeBufferedKey') or unreal.BlueprintEditorLibrary.add_function_graph(pc,'K02ConsumeBufferedKey')
if not any(n.get_class().get_name()=='K2Node_FunctionResult' for n in B.find_nodes(g)):
 B.add_struct_function_param(g,'Key',unreal.load_object(None,'/Script/InputCore.Key'),True)
 B.add_function_param(g,'ReturnValue','bool',False)
code='(fn K02ConsumeBufferedKey (Key)\n'
for name,key in keys:code+=' (if (and (CallFunction|K02KeysEqual self Key "'+key+'") (<= (- (Utilities|Time|GetTimeSeconds) (Variables|Default|GetK02Buffered'+name+')) 0.35)) (Variables|Default|SetK02Buffered'+name+' -100) (return true))\n'
code+=' (return false))';B.write_graph_dsl(g,code);compile(pc)
# Inject into the existing Tick, preserving camera and user-edited nodes.
g=graph(pc,'EventGraph');ed=unreal.BlueprintGraphEditor.get_graph_editor(g);event=next(n for n in B.find_nodes(g) if n.get_class().get_name()=='K2Node_Event' and n.get_node_title()=='Event Tick');pin=event.find_then_pin();targets=pin.list_connected_pins();assert len(targets)==1
if 'K02CombatInputTick' not in targets[0].get_owning_node().get_node_title().replace(' ',''):
 n=ed.add_call_function_node(pc.generated_class().get_path_name()+':K02CombatInputTick');pin.break_single_pin_link(targets[0]);assert pin.try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(targets[0])
compile(pc);save(pc)
# The native Support action used to reject block outside lock-on. Own tick now handles Ctrl with deterministic precedence.
exec(Path('A:/K-02 5.8/Tools/Protagonist/restore_combat_mapping.py').read_text())
# Per-owner buffer, consumed once only at legal montage branches. AI uses the same branch data.
bp=unreal.load_asset(R+'/Notifies/ANS_K02_ComboBranch');code=Path('A:/K-02 5.8/Tools/Protagonist/buffered_branch_notify.dsl').read_text()
B.write_graph_dsl(graph(bp,'Received_NotifyTick'),code);compile(bp);save(bp)
unreal.log('K02_COMBAT_INPUT_BUILT')
