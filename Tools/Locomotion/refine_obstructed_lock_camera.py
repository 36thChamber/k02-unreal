"""Frame the fighter and locked opponent; score camera orbits against world collision."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(),'Stop PIE first'
bp=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController')
def graph(n):return next((g for g in B.list_graphs(bp) if g.get_name()==n),None) or B.add_function_graph(bp,n)
for n,t in [('K02CameraPivot','vector'),('K02CameraSpan','float'),('K02CameraFacing','float'),('K02CameraBestScore','float'),('K02CameraBestYaw','float'),('K02CameraOrbit','float'),('K02CameraBestOrbit','float')]:
 try:B.add_variable(bp,n,t)
 except Exception as e:
  if 'exist' not in str(e).lower():raise
cg=graph('K02ConsiderCameraOrbit')
if len([p for n in B.find_nodes(cg) for p in B._get_node_info(n).output_pins if p.name=='Offset'])==0:B.add_function_param(cg,'Offset','float',True)
for n in list(B.find_nodes(cg)):
 if n.get_class().get_name()!='K2Node_FunctionEntry':B.delete_node(n)
B.write_graph_dsl(cg,'''(fn K02ConsiderCameraOrbit (Offset)
 (bind _pawn (Variables|DoNotEdit|GetPawnRef))
 (bind _target (Variables|DoNotEdit|GetCurrentTarget))
 (bind _pivot (Variables|Default|GetK02CameraPivot))
 (bind _span (Variables|Default|GetK02CameraSpan))
 (bind _yaw (+ (Variables|Default|GetK02CameraFacing) Offset))
 (bind _rot (Math|Rotator|MakeRotator 0 -15 _yaw))
 (bind _end (- _pivot (* (Math|Vector|GetForwardVector _rot) _span)))
 (bind (_hit _blocked) (Collision|SphereTraceByChannel :Start _pivot :End _end :Radius 16 :TraceChannel "TraceTypeQuery2" :bTraceComplex false :DrawDebugType "None" :bIgnoreSelf true))
 (bind (_blocking _penetrating _time) (Collision|BreakHitResult _hit))
 (bind _fraction (Math|Float|SelectFloat _time 1 _blocked))
 (bind _score (+ (- (* 1000 _fraction) (Math|Float|Absolute(Float) Offset)) (Math|Float|SelectFloat 50 0 (< (Math|Float|Absolute(Float) (- Offset (Variables|Default|GetK02CameraOrbit))) 1))))
 (if (> _score (Variables|Default|GetK02CameraBestScore))
  (Variables|Default|SetK02CameraBestScore _score)
  (Variables|Default|SetK02CameraBestYaw _yaw)
  (Variables|Default|SetK02CameraBestOrbit Offset)))''')
assert any('SetK02CameraBestOrbit' in ''.join(n.get_node_title().split()) for n in B.find_nodes(cg)),'Incomplete camera scorer'
trace=next(n for n in B.find_nodes(cg) if 'SphereTraceByChannel' in ''.join(n.get_node_title().split()))
a=B.create_node(cg,'Utilities|Array|MakeArray',unreal.IntPoint(0,0));B.add_node_pin(a)
for i,term in enumerate(['PawnRef','CurrentTarget']):
 n=next(n for n in B.find_nodes(cg) if n.get_class().get_name()=='K2Node_VariableGet' and term in ''.join(n.get_node_title().split()))
 assert n.find_output_pin_by_index(0).try_create_connection(a.find_input_pin('['+str(i)+']'))
assert a.find_output_pin_by_index(0).try_create_connection(trace.find_input_pin('ActorsToIgnore'))
B.compile_blueprint(bp,warnings_as_errors=True)
body='''(if (not (Input|IsLookInputIgnored self)) (Input|SetIgnoreLookInput self true))
(bind _pawn (Variables|DoNotEdit|GetPawnRef))
(bind _arm (Utilities|Casting|CastToSpringArmComponent (Actor|GetComponentByClass _pawn "/Script/Engine.SpringArmComponent")))
(bind _target (Variables|DoNotEdit|GetCurrentTarget))
(bind _a (Transformation|GetActorLocation _pawn))
(bind _b (Transformation|GetActorLocation _target))
(bind _mid (+ (* (+ _a _b) 0.5) (Math|Vector|MakeVector 0 0 35)))
(bind _face (Math|Rotator|FindLookatRotation _a _b))
(Variables|Default|SetK02CameraPivot _mid)
(bind (_probe _inside) (Collision|SphereTraceByChannel :Start _mid :End (+ _mid (Math|Vector|MakeVector 0 0 1)) :Radius 20 :TraceChannel "TraceTypeQuery2" :bTraceComplex false :DrawDebugType "None" :bIgnoreSelf true))
(if _inside (Variables|Default|SetK02CameraPivot (+ _a (Math|Vector|MakeVector 0 0 35))))
(Variables|Default|SetK02CameraSpan (+ 440 (* 1.05 (Math|Vector|Distance(Vector) _a _b))))
(Variables|Default|SetK02CameraFacing (.yaw _face))
(Variables|Default|SetK02CameraBestScore -10000)
'''
for angle in [0,45,-45,90,-90,135,-135,180]:body+='(CallFunction|K02ConsiderCameraOrbit :Offset '+str(angle)+')\n'
body+='''(Class|SpringArmComponent|SetEnableCameraLag false _arm)
(Class|SpringArmComponent|SetEnableCameraRotationLag false _arm)
(Class|SpringArmComponent|SetSocketOffset (Math|Vector|MakeVector 0 0 0) _arm)
(Class|SpringArmComponent|SetTargetOffset (- (Variables|Default|GetK02CameraPivot) (Transformation|GetWorldLocation _arm)) _arm)
(Class|SpringArmComponent|SetTargetArmLength (Variables|Default|GetK02CameraSpan) _arm)
(Pawn|SetControlRotation self (Math|Interpolation|RInterpTo (Pawn|GetControlRotation self) (Math|Rotator|MakeRotator 0 -15 (Variables|Default|GetK02CameraBestYaw)) (Utilities|Time|GetWorldDeltaSeconds) 8))
(Transformation|SetActorRotation _pawn (Math|Rotator|MakeRotator 0 0 (.yaw _face)) false)
(Variables|Default|SetK02CameraOrbit (Variables|Default|GetK02CameraBestOrbit))'''
fg=graph('K02ApplyLockedFraming')
for n in list(B.find_nodes(fg)):
 if n.get_class().get_name()!='K2Node_FunctionEntry':B.delete_node(n)
B.write_graph_dsl(fg,'(fn K02ApplyLockedFraming () '+body+')')
trace=next(n for n in B.find_nodes(fg) if 'SphereTraceByChannel' in ''.join(n.get_node_title().split()))
a=B.create_node(fg,'Utilities|Array|MakeArray',unreal.IntPoint(0,0));B.add_node_pin(a)
for i,term in enumerate(['PawnRef','CurrentTarget']):
 n=next(n for n in B.find_nodes(fg) if n.get_class().get_name()=='K2Node_VariableGet' and term in ''.join(n.get_node_title().split()))
 assert n.find_output_pin_by_index(0).try_create_connection(a.find_input_pin('['+str(i)+']'))
assert a.find_output_pin_by_index(0).try_create_connection(trace.find_input_pin('ActorsToIgnore'))
B.compile_blueprint(bp,warnings_as_errors=True)
unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('K02_OBSTRUCTED_CAMERA_BUILT')
