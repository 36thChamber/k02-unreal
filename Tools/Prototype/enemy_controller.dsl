(event EventBeginPlay
  (|Parent:BeginPlay))

(event EventOnPossess (PossessedPawn)
  (AI|RunBehaviorTree self "/Game/MACS/AI/BT_MACS_Demo.BT_MACS_Demo"))

(event EventTick (DeltaSeconds))
