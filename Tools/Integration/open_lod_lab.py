import unreal
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/K02/Validation/Levels/L_K02_ProtagonistLab')
