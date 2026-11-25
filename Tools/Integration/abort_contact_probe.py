import unreal,gc
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0)
for obj in gc.get_objects():
 if type(obj).__name__=='SettledTree' and getattr(obj,'p',None)==p:
  unreal.unregister_slate_post_tick_callback(obj.handle);print('Unregistered failed contact observer');obj.finish('Contact observer API error: get_physics_asset unavailable; test aborted, not gameplay approval')
