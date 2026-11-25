import unreal,json
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();a=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Character) if a.get_class().get_name()=='BP_K02_Enemy_C');ins=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'))
print('enemy',a.get_path_name());print('tags',list(ins.call_method('GetActiveTags',args=(a,))));print('montage',a.mesh.get_anim_instance().get_current_active_montage())
