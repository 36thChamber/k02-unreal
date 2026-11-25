"""Create a UE import derivative; never overwrite the supplied FBX or Blender.

Preserves weighted bones, local bind poses, meshes, UVs and materials. Changes
only the armature container name and where the FBX stores the unit conversion.
Output must be verified in Unreal before replacing the initial import probe.
"""
import bpy
import hashlib
import json
from pathlib import Path
import sys
from mathutils import Matrix

args=sys.argv[sys.argv.index('--')+1:]
src,dst=map(Path,args[:2])
assert src.resolve()!=dst.resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(src),use_anim=False,automatic_bone_orientation=False)
rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
assert len(rigs)==1
rig=rigs[0]
unit=bpy.context.scene.unit_settings.scale_length
before={b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(v) for v in rig.matrix_world @ b.matrix_local]} for b in rig.data.bones}
assert len(before)==61
# Fold object transforms into the imported copy, then express all data in cm.
# Both mesh and bind skeleton receive the same conversion. This avoids a 100x
# skeletal root scale (FBX unit metadata alone still produced that in UE).
objects=[o for o in bpy.data.objects if o.type in {'MESH','ARMATURE'}]
world={o.name:o.matrix_world.copy() for o in objects}
for o in objects:
    o.parent=None
    o.matrix_world=world[o.name]
for o in objects:
    o.data.transform(world[o.name])
    o.matrix_world=Matrix.Identity(4)
    o.data.transform(Matrix.Scale(100*unit,4))
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=.01
bpy.context.view_layer.update()
rig.name='Armature'
for o in bpy.data.objects:o.select_set(o.type in {'MESH','ARMATURE'})
bpy.context.view_layer.objects.active=rig
dst.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.fbx(filepath=str(dst),use_selection=True,object_types={'MESH','ARMATURE'},
    add_leaf_bones=False,bake_anim=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
    global_scale=1.0,axis_forward='-Z',axis_up='Y',use_armature_deform_only=False,
    mesh_smooth_type='FACE',path_mode='STRIP')
max_pose_error=0.0
for b in rig.data.bones:
    old=Matrix(before[b.name]['matrix'])
    new=rig.matrix_world @ b.matrix_local
    error=(new.translation*.01-old.translation*unit).length
    max_pose_error=max(max_pose_error,error)
    assert (b.parent.name if b.parent else None)==before[b.name]['parent']
assert max_pose_error<1e-5,max_pose_error
r={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
   'output':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
   'bones':len(before),'bind_position_max_error_m':max_pose_error,
   'changes':['Armature container name','physical data expressed in cm; applied object transforms','FBX_SCALE_UNITS'],
   'unreal_validation':'pending'}
dst.with_suffix('.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
