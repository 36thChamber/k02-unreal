import unreal
W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();pc=unreal.GameplayStatics.get_player_controller(W,0);m=pc.get_editor_property('K02TrainingMenu');b=m.get_editor_property('Resume')
print('before',b.has_keyboard_focus(),b.get_editor_property('is_focusable'),b.get_is_enabled(),b.get_visibility())
unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetInputMode_UIOnlyEx',args=(pc,b,unreal.MouseLockMode.DO_NOT_LOCK,True))
b.set_user_focus(pc);b.set_keyboard_focus();print('after',b.has_keyboard_focus())
