"""Skin-derived query bodies and mesh-only MACS trace sockets. No cloth collision."""
import unreal,json,math
from pathlib import Path
from editor_toolset.toolsets.skeletal_mesh import SkeletalMeshTools as S
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir());BASE='/Game/K02/Characters/Protagonist/Dogi_v001';A=unreal.EditorAssetLibrary
mesh=unreal.load_asset(BASE+'/Meshes/SK_K02_Dogi_Combined_v001');body=unreal.load_asset(BASE+'/Meshes/SK_K02_BodyForDogi_v001')
p=unreal.get_default_object(unreal.load_class(None,'/Script/PhysicsToolsets.PhysicsAssetToolset'))
path=BASE+'/Rig/PA_K02_Protagonist_Query_v001';pa=unreal.load_asset(path) if A.does_asset_exist(path) else None
if not pa:
 pa=p.call_method('CreateFromMesh',args=(mesh.get_path_name().split('.')[0],False));assert pa
 assert A.rename_asset(pa.get_path_name(),path)
pa=unreal.load_asset(path);assert pa
# Own newly introduced asset only; caller must back it up before later refinement.
for c in list(p.call_method('GetConstraints',args=(pa,))):p.call_method('RemoveConstraint',args=(pa,c.bone1_name,c.bone2_name))
for b in list(p.call_method('GetBodyNames',args=(pa,))):p.call_method('RemoveBody',args=(pa,b))
rc=unreal.IKRigController.get_controller(unreal.load_asset(BASE+'/Rig/IK_K02_Protagonist'))
regions=json.loads((ROOT/'Saved/Diagnostics/Integration/Protagonist/contact-regions.json').read_text())['regions'];rows=[]
def quantile(a,q):return sorted(a)[int((len(a)-1)*q)]
children={b+s:c+s for s in ['_l','_r'] for b,c in [('upperarm','lowerarm'),('lowerarm','hand'),('thigh','calf'),('calf','foot')]}
for b,r in regions.items():
 if r['samples']<10:continue
 t=rc.get_ref_pose_transform_of_bone(b);p.call_method('AddBody',args=(pa,b))
 points=[unreal.Vector(*v) for v in r['points_cm']]
 if b in children:
  start=t.translation;end=rc.get_ref_pose_transform_of_bone(children[b]).translation;axis=(end-start).normal()
  along=[(v-start).dot(axis) for v in points];lo,hi=quantile(along,.03),quantile(along,.97)
  radial=[(v-(start+axis*a)).length() for v,a in zip(points,along)];radius=quantile(radial,.85)
  center=unreal.MathLibrary.inverse_transform_location(t,start+axis*((lo+hi)*.5));direction=unreal.MathLibrary.inverse_transform_direction(t,axis)
  rotation=unreal.MathLibrary.make_rot_from_z(direction);length=max(0.,hi-lo-2*radius)
  p.call_method('SetCapsule',args=(pa,b,'SkinContact',center,rotation,radius,length));kind='capsule'
 else:
  # Torso, hands and feet: robust bone-local bounds of the skin, not garment.
  local=[unreal.MathLibrary.inverse_transform_location(t,v) for v in points]
  lo=[quantile([v.to_tuple()[i] for v in local],.03) for i in range(3)];hi=[quantile([v.to_tuple()[i] for v in local],.97) for i in range(3)]
  center=unreal.Vector(*[(x+y)*.5 for x,y in zip(lo,hi)]);ext=[max(1.,y-x) for x,y in zip(lo,hi)]
  p.call_method('SetBox',args=(pa,b,'SkinContact',center,unreal.Rotator(),*ext));kind='box'
 # This asset is queried for actual visible-body contacts. Ragdoll authority
 # remains the existing MACS source mesh; do not run duplicate simulation.
 p.call_method('SetBodyPhysicsMode',args=(pa,b,unreal.BodyPhysicsMode.KINEMATIC))
 rows.append({'bone':b,'shape':kind,'source_vertices':r['samples'],'center_local_cm':center.to_tuple()})
for m in [mesh,body]:
 m.set_editor_property('physics_asset',pa)
 for b in ['hand_l','hand_r','foot_l','foot_r']:
  name=b+'_Trace_Sphere';sock=m.find_socket(name)
  if not sock:sock=S.add_socket(m,name,b)
  if not sock:sock=m.find_socket(name)
  assert sock
  # Keep approved MACS sphere radius initially; no reach inflation.
  sock.set_editor_properties({'relative_location':unreal.Vector(),'relative_rotation':unreal.Rotator(pitch=0,yaw=0,roll=20),'relative_scale':unreal.Vector(1,1,1)})
 assert A.save_loaded_asset(m,False)
assert A.save_loaded_asset(pa,False)
(ROOT/'Saved/Diagnostics/Integration/protagonist-contact.json').write_text(json.dumps({'physics':path,'bodies':rows,'trace_radius_cm':20,'scope':'query-only skin regions; contact and ragdoll gameplay validation pending'},indent=2))
print('Prepared skin contact bodies',len(rows))
