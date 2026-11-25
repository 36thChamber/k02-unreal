import unreal
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0)
b=next(c for c in p.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='K02Body')
b.set_relative_location(unreal.Vector(),False,True)
print('Runtime only: remove trial -5cm presentation offset')
