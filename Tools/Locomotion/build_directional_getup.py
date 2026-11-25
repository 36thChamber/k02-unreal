import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
bp=unreal.load_asset('/Game/K02/Protagonist/Abilities/GA_K02_HitReactions');assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
g=next((g for g in B.list_graphs(bp) if g.get_name()=='K02SelectDirectionalGetUp'),None) or unreal.BlueprintEditorLibrary.add_function_graph(bp,'K02SelectDirectionalGetUp')
R='/Game/K02/Protagonist/Montages/AM_K02_GetUp_'
code='''(fn K02SelectDirectionalGetUp ()
 (Variables|MACS|SetGetUpMontage "NEUTRAL")
 (bind _pawn (Utilities|Casting|CastToPawn (Ability|GetAvatarActorFromActorInfo)))
 (bind _pc (Utilities|Casting|CastToPlayerController (Pawn|GetController _pawn)))
 (bind _f (- (Game|Player|GetInputAnalogKeyState _pc "W") (Game|Player|GetInputAnalogKeyState _pc "S")))
 (bind _r (- (Game|Player|GetInputAnalogKeyState _pc "D") (Game|Player|GetInputAnalogKeyState _pc "A")))
 (bind _world (+ (* (Math|Vector|GetForwardVector (Pawn|GetControlRotation _pc)) _f) (* (Math|Vector|GetRightVector (Pawn|GetControlRotation _pc)) _r)))
 (bind _forward (Math|Vector|DotProduct _world (Transformation|GetActorForwardVector _pawn)))
 (bind _right (Math|Vector|DotProduct _world (Transformation|GetActorRightVector _pawn)))
 (if (> (+ (* _forward _forward) (* _right _right)) 0.1)
  (if (>= (* _forward _forward) (* _right _right))
   (if (> _forward 0) (Variables|MACS|SetGetUpMontage "FORWARD") (else (Variables|MACS|SetGetUpMontage "BACKWARD")))
   (else (if (> _right 0) (Variables|MACS|SetGetUpMontage "RIGHT") (else (Variables|MACS|SetGetUpMontage "LEFT")))))))'''
for name in ['Neutral','Forward','Backward','Right','Left']:code=code.replace(name.upper(),R+name+'.AM_K02_GetUp_'+name)
B.write_graph_dsl(g,code);B.compile_blueprint(bp,warnings_as_errors=True)
# Insert before the existing MACS get-up task, preserving knockdown timing, GAS, and escape cancellation.
game=next(g for g in B.list_graphs(bp) if g.get_name()=='Gameplay Ability Graph');ed=unreal.BlueprintGraphEditor.get_graph_editor(game)
event=next(n for n in B.find_nodes(game) if n.get_class().get_name()=='K2Node_CustomEvent' and ''.join(n.get_node_title().split())=='PlayGetUpMontage')
pin=event.find_then_pin();targets=pin.list_connected_pins();assert len(targets)==1

if 'K02SelectDirectionalGetUp' not in ''.join(targets[0].get_owning_node().get_node_title().split()):
 call=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02SelectDirectionalGetUp');pin.break_single_pin_link(targets[0]);assert pin.try_create_connection(call.find_execute_pin());assert call.find_then_pin().try_create_connection(targets[0])
B.compile_blueprint(bp,warnings_as_errors=True);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
Path('A:/K-02 5.8/Saved/Diagnostics/LockRecovery/getup-selection.dsl').write_text(B.read_graph_dsl(g));unreal.log('K02_DIRECTIONAL_GETUP_BUILT')
