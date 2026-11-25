"""Own-controller free-camera wall fallback. Does not change control yaw or lock solver."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
def graph(n):return next((g for g in B.list_graphs(bp) if g.get_name()==n),None)
for n,t in [('K02FreeCameraActive','bool'),('K02FreeCameraAlpha','float'),('K02FreeCameraBaseOffset','vector')]:
 if n not in B.list_variables(bp):B.add_variable(bp,n,t)
B.compile_blueprint(bp,warnings_as_errors=True)
common='''(bind _pawn (Variables|DoNotEdit|GetPawnRef))
(bind _arm (Utilities|Casting|CastToSpringArmComponent (Actor|GetComponentByClass _pawn "/Script/Engine.SpringArmComponent")))
(bind _camera (Utilities|Casting|CastToCameraComponent (Actor|GetComponentByClass _pawn "/Script/Engine.CameraComponent")))'''
reset='''(fn K02ResetFreeCamera ()
(if (Variables|Default|GetK02FreeCameraActive)
COMMON
(Class|SpringArmComponent|SetTargetOffset (Variables|Default|GetK02FreeCameraBaseOffset) _arm)
(Transformation|SetRelativeRotation _camera (Math|Rotator|MakeRotator 0 0 0) false :bTeleport true)
(Variables|Default|SetK02FreeCameraAlpha 0)
(Variables|Default|SetK02FreeCameraActive false)))'''.replace('COMMON',common)
update='''(fn K02UpdateFreeCamera ()
(if (and (not (Variables|Default|GetK02HasCombatLock)) (not (Variables|Default|GetK02CameraLocked)))
COMMON
(if (not (Variables|Default|GetK02FreeCameraActive))
(Variables|Default|SetK02FreeCameraBaseOffset (Class|SpringArmComponent|GetTargetOffset _arm))
(Variables|Default|SetK02FreeCameraActive true))
(bind _pivot (+ (Transformation|GetWorldLocation _arm) (Variables|Default|GetK02FreeCameraBaseOffset)))
(bind _rotation (Pawn|GetControlRotation self))
(bind _span (Class|SpringArmComponent|GetTargetArmLength _arm))
(bind _end (+ (- _pivot (* (Math|Vector|GetForwardVector _rotation) _span)) (Math|Vector|RotateVector (Class|SpringArmComponent|GetSocketOffset _arm) _rotation)))
(bind (_hit _blocked) (Collision|SphereTraceByChannel :Start _pivot :End _end :Radius 16 :TraceChannel "TraceTypeQuery2" :bTraceComplex false :DrawDebugType "None" :bIgnoreSelf true))
(bind (_blocking _penetrating _time) (Collision|BreakHitResult _hit))
(bind _clearance (* _span (Math|Float|SelectFloat _time 1 _blocked)))
(bind _wanted (Math|Float|Clamp(Float) (/ (- 140.0 _clearance) 100.0) 0 1))
(Variables|Default|SetK02FreeCameraAlpha (Math|Interpolation|FInterpTo (Variables|Default|GetK02FreeCameraAlpha) _wanted (Utilities|Time|GetWorldDeltaSeconds) 8))
(bind (_ceiling _ceilingBlocked) (Collision|SphereTraceByChannel :Start _pivot :End (+ _pivot (Math|Vector|MakeVector 0 0 160)) :Radius 16 :TraceChannel "TraceTypeQuery2" :bTraceComplex false :DrawDebugType "None" :bIgnoreSelf true))
(bind (_cb _cp _ct) (Collision|BreakHitResult _ceiling))
(bind _alpha (* (Variables|Default|GetK02FreeCameraAlpha) (Math|Float|SelectFloat _ct 1 _ceilingBlocked)))
(Class|SpringArmComponent|SetTargetOffset (+ (Variables|Default|GetK02FreeCameraBaseOffset) (Math|Vector|MakeVector 0 0 (* 160.0 _alpha))) _arm)
(bind _pitch (- (Math|Float|Clamp(Float) (+ (.pitch _rotation) (* (- -62.0 (.pitch _rotation)) _alpha)) -80 60) (.pitch _rotation)))
(Transformation|SetRelativeRotation _camera (Math|Rotator|MakeRotator 0 _pitch 0) false :bTeleport true)))'''.replace('COMMON',common)
for n,code in [('K02ResetFreeCamera',reset),('K02UpdateFreeCamera',update)]:
 g=graph(n) or unreal.BlueprintEditorLibrary.add_function_graph(bp,n)
 B.write_graph_dsl(g,code)
 # Camera traces ignore all components of this pawn, including contact queries.
 for trace in B.find_nodes(g):
  if 'SphereTraceByChannel' not in ''.join(trace.get_node_title().split()):continue
  ed=unreal.BlueprintGraphEditor.get_graph_editor(g);arr=B.create_node(g,'Utilities|Array|MakeArray',unreal.IntPoint(0,0))
  pawn=ed.add_get_member_variable_node('PawnRef')
  assert arr.find_output_pin_by_index(0).try_create_connection(trace.find_input_pin('ActorsToIgnore'))
  assert pawn.find_output_pin_by_index(0).try_create_connection(arr.find_input_pin('[0]'))
 B.compile_blueprint(bp,warnings_as_errors=True)
 for node in B.find_nodes(g):
  if node.get_node_title() in ['float * float','float / float','float + float','float - float','int * int','int / int']:
   assert all(node.find_input_pin(pin).list_connected_pins() for pin in ['A','B']), 'Disconnected math input: '+node.get_node_title()
# Append only to existing free-orientation chain; preserve every prior node.
g=graph('K02ApplyFreeOrientation')
if not any('K02UpdateFreeCamera' in n.get_node_title().replace(' ','') for n in B.find_nodes(g)):
 last=next(n for n in B.find_nodes(g) if 'K02KeepLockedFacing' in n.get_node_title().replace(' ',''));pin=last.find_then_pin();assert not pin.list_connected_pins()
 n=unreal.BlueprintGraphEditor.get_graph_editor(g).add_call_function_node(bp.generated_class().get_path_name()+':K02UpdateFreeCamera');assert pin.try_create_connection(n.find_execute_pin())
g=graph('K02EnterCameraLock')
if not any('K02ResetFreeCamera' in n.get_node_title().replace(' ','') for n in B.find_nodes(g)):
 ed=unreal.BlueprintGraphEditor.get_graph_editor(g);entry=ed.find_graph_entry_pin();old=entry.list_connected_pins();assert len(old)==1
 n=ed.add_call_function_node(bp.generated_class().get_path_name()+':K02ResetFreeCamera');entry.break_single_pin_link(old[0]);assert entry.try_create_connection(n.find_execute_pin());assert n.find_then_pin().try_create_connection(old[0])
B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/free-camera-implementation.json').write_text(json.dumps({'height_cm':160,'fallback_world_pitch_degrees':-62,'interpolation':8,'obstruction_start_cm':140,'full_response_cm':40,'trace_radius_cm':16,'control_rotation_changed':False,'lock_solver_changed':False,'status':'compiled, validation pending'},indent=2))
print('K02_FREE_CAMERA_COMPILED')
