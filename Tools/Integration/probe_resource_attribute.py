import unreal
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();p=unreal.GameplayStatics.get_player_pawn(w,0)
a=unreal.GameplayAttribute();a.import_text('(AttributeName="Resource",Attribute="/Script/MAUT.MAUT_AttributeSet:Resource",AttributeOwner="/Script/MAUT.MAUT_AttributeSet")')
print(a.export_text());print(unreal.get_default_object(unreal.load_class(None,'/Script/GameplayAbilities.AbilitySystemBlueprintLibrary')).call_method('GetFloatAttribute',args=(p,a)))
