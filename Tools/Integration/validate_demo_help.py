import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();pc=unreal.GameplayStatics.get_player_controller(w,0);hud=pc.get_hud();ui=hud.get_editor_property('UI')
fields=['BP_MACS_GAS_CharData','BP_MACS_GAS_CharData_Target','BP_MACS_GAS_ComboCounter','BP_MACS_GAS_ActionText','WB_MACS_Weapons','WB_MACS_DemoKeys']
rows={f:str(ui.get_editor_property(f).get_visibility()) for f in fields}
assert ui.get_editor_property('WB_MACS_DemoKeys').get_visibility()==unreal.SlateVisibility.COLLAPSED,rows
assert ui.get_editor_property('BP_MACS_GAS_CharData').get_visibility()!=unreal.SlateVisibility.COLLAPSED,rows
r={'pass':True,'paused':unreal.GameplayStatics.is_game_paused(w),'widgets':rows,'scope':'Readback of runtime HUD visibility; commercial assets untouched'}
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/demo-help-validation.json').write_text(json.dumps(r,indent=2));print(r)
