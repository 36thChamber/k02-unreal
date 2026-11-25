import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert w
pc=unreal.GameplayStatics.get_player_controller(w,0)
if not pc.get_editor_property('K02TrainingMenuOpen'):pc.call_method('K02ShowTrainingMenu')
pc.call_method('K02ShowComfortOptions')
print('CAMERA_OPTIONS_VISIBLE',pc.get_editor_property('K02ComfortOpen'))
