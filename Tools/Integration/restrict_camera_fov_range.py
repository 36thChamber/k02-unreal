"""Reject FOV80 after elevated-target framing failure; retain validated default and wider views."""
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc=unreal.load_asset('/Game/K02/Protagonist/Blueprints/BP_K02_PlayerController');changed=[]
for g in B.list_graphs(pc):
 if g.get_name() not in ['K02ApplyComfortPreferences','K02CycleCameraFOV']:continue
 for n in B.find_nodes(g):
  for p in n.list_input_pins():
   if not p.list_connected_pins() and str(p.get_pin_name()) in ['Min','K02CameraFOV'] and p.get_pin_value() in ['80.0','80.000000','80']:
    assert p.set_pin_value('90.0');changed.append([g.get_name(),n.get_name(),str(p.get_pin_name())])
assert len(changed)==2,changed
ui=unreal.load_asset('/Game/K02/UI/Settings/WBP_K02_ComfortOptions');U=unreal.get_default_object(unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet'));ws={str(i.widget_name):i.widget for i in U.call_method('GetWidgets',args=(ui,)).widgets};ws['Help'].set_text('Selecione um valor para alternar. Sensibilidade: 0,25–2×. FOV: 90–100°.')
for bp in [pc,ui]:B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert unreal.EditorAssetLibrary.save_loaded_asset(bp,False)
print('FOV_RANGE_RESTRICTED',changed)
