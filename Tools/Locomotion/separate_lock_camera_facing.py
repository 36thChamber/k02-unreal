"""Keep the fighter facing the locked target when the camera orbits around cover."""
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
def graph(n):return next((g for g in B.list_graphs(bp) if g.get_name()==n),None) or B.add_function_graph(bp,n)
g=graph('K02KeepLockedFacing')
for n in list(B.find_nodes(g)):
 if n.get_class().get_name()!='K2Node_FunctionEntry':B.delete_node(n)
B.write_graph_dsl(g,'''(fn K02KeepLockedFacing ()
 (CallFunction|K02CheckCombatLock)
 (if (Variables|Default|GetK02HasCombatLock)
  (bind _pawn (Variables|DoNotEdit|GetPawnRef))
  (bind _m (Class|Character|GetCharacterMovement _pawn))
  (Class|CharacterMovementComponent|SetOrientRotationtoMovement false _m)
  (Class|CharacterMovementComponent|SetUseControllerDesiredRotation false _m)
  (Class|Pawn|SetUseControllerRotationYaw false _pawn)
  (bind _facing (Math|Rotator|FindLookatRotation (Transformation|GetActorLocation _pawn) (Transformation|GetActorLocation (Variables|DoNotEdit|GetCurrentTarget))))
  (Transformation|SetActorRotation _pawn (Math|Rotator|MakeRotator 0 0 (.yaw _facing)) false)))''')
assert any('SetActorRotation' in ''.join(n.get_node_title().split()) for n in B.find_nodes(g))
B.compile_blueprint(bp,warnings_as_errors=True)
for name,lastTitle in [('K02ApplyFreeOrientation','K02EndGuardWithoutLock'),('K02ApplyLockedFraming','SetK02CameraOrbit')]:
 g=graph(name)
 if any('K02KeepLockedFacing' in ''.join(n.get_node_title().split()) for n in B.find_nodes(g)):continue
 n=next(n for n in B.find_nodes(g) if lastTitle in ''.join(n.get_node_title().split()));pin=n.find_then_pin();assert not pin.list_connected_pins()
 ed=unreal.BlueprintGraphEditor.get_graph_editor(g);call=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02KeepLockedFacing');assert pin.try_create_connection(call.find_execute_pin())
B.compile_blueprint(bp,warnings_as_errors=True);unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);unreal.log('K02_CAMERA_FACING_SEPARATED')
