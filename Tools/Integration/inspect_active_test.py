import unreal,gc,json
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
r={'world':str(w),'paused':unreal.GameplayStatics.is_game_paused(w),'game_time':unreal.GameplayStatics.get_time_seconds(w),'real_time':unreal.GameplayStatics.get_real_time_seconds(w),'dilation':unreal.GameplayStatics.get_global_time_dilation(w),'delta':unreal.GameplayStatics.get_world_delta_seconds(w),'window':unreal.SystemLibrary.get_game_name()}
for o in gc.get_objects():
 if type(o).__name__=='SettledTree':
  r['test']={k:str(getattr(o,k,None)) for k in ['clock','i','wait','start','cur','rows','cases']}
print(json.dumps(r,indent=2))
