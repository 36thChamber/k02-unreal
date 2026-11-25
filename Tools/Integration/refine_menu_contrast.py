"""Match own menus to high-contrast dark controls; align value columns."""
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
U=unreal.get_default_object(unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet'));A=unreal.EditorAssetLibrary
for path in ['/Game/K02/UI/Settings/WBP_K02_ComfortOptions','/Game/K02/UI/Training/WBP_K02_TrainingMenu']:
 bp=A.load_asset(path);widgets={str(i.widget_name):i for i in U.call_method('GetWidgets',args=(bp,)).widgets}
 for name,i in widgets.items():
  w=i.widget
  if isinstance(w,unreal.Button):
   style=w.get_editor_property('widget_style')
   for field,tint in [('normal',(.035,.06,.085,1)),('hovered',(.10,.19,.28,1)),('pressed',(.07,.14,.21,1))]:
    brush=style.get_editor_property(field);brush.set_editor_property('tint_color',unreal.SlateColor(specified_color=unreal.LinearColor(*tint)));style.set_editor_property(field,brush)
   w.set_style(style)
 if 'ComfortOptions' in path:
  for key in ['SensitivityX','SensitivityY','InvertX','InvertY']:
   i=widgets[key+'Name'];i.slot.set_size(unreal.SlateChildSize(size_rule=unreal.SlateSizeRule.FILL,value=1));i.slot.set_padding(unreal.Margin(0,0,24,0));i.slot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
 B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert A.save_loaded_asset(bp,False)
print('OWN_MENU_CONTRAST_ALIGNED')
