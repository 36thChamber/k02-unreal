"""Actual simultaneous source/target playback in the isolated simulated lab."""
import json
from pathlib import Path
import unreal
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert w
assert 'CharacterLab' in w.get_name()
rows=json.loads((Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/pilot-clips.json').read_text())
index=int(REQUEST.get('params',{}).get('index',0))
fraction=float(REQUEST.get('params',{}).get('fraction',.5))
row=rows[index]
out={}
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.SkeletalMeshActor):
    name=a.get_actor_label()
    if name not in ['Manny_Source','B_1_Stance']:continue
    c=a.skeletal_mesh_component
    anim=unreal.load_asset(row['source'] if name=='Manny_Source' else row['asset'])
    t=anim.get_play_length()*fraction
    c.play_animation(anim,True);c.set_position(t,False);c.set_play_rate(0.)
    opts=unreal.AnimPoseEvaluationOptions();opts.set_editor_property('should_retarget',False)
    pose=anim.get_anim_pose_at_time(t,opts)
    root=unreal.AnimPoseExtensions.get_bone_pose(pose,'root',unreal.AnimPoseSpaces.WORLD).translation
    a.set_actor_location(unreal.Vector(-170 if name=='Manny_Source' else 0,0,0)-root,False,True)
    out[name]={'animation':anim.get_path_name(),'time':t,'root':root.to_tuple()}
print(json.dumps(out))
