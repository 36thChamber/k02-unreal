(fn K02RefreshStyleInput ()
  (bind _sub (PlayerController|LocalPlayerSubsystems|GetEnhancedInputLocalPlayerSubsystem self))
  (bind (_original_priority _has_original) (Input|MappingQueries|HasMappingContext _sub "/Game/MACS/Inputs/Abilities/IMC_MACS_Abilities.IMC_MACS_Abilities"))
  (bind (_fighter_priority _has_fighter) (Input|MappingQueries|HasMappingContext _sub "/Game/K02/Protagonist/Inputs/IMC_K02_Abilities.IMC_K02_Abilities"))
  (if (Check|GameplayTagCheck (Variables|DoNotEdit|GetPawnRef) "(TagName=\"MACS_GAS.Abilities.States.WeaponClass.Fighter\")")
    (if _has_original
      (Input|RemoveMappingContext _sub "/Game/MACS/Inputs/Abilities/IMC_MACS_Abilities.IMC_MACS_Abilities"))
    (if (not _has_fighter)
      (Input|AddMappingContext _sub "/Game/K02/Protagonist/Inputs/IMC_K02_Abilities.IMC_K02_Abilities" 0))
    (else
      (if _has_fighter
        (Input|RemoveMappingContext _sub "/Game/K02/Protagonist/Inputs/IMC_K02_Abilities.IMC_K02_Abilities"))
      (if (not _has_original)
        (Input|AddMappingContext _sub "/Game/MACS/Inputs/Abilities/IMC_MACS_Abilities.IMC_MACS_Abilities" 0)))))
