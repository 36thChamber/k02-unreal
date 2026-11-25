"""Non-interactive own combat notice; does not block the camera or input."""
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;U=unreal.get_default_object(unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet'));path='/Game/K02/UI/Combat/WBP_K02_CombatNotice'
assert not A.does_asset_exist(path)
bp=U.call_method('CreateWidgetBlueprint',args=('/Game/K02/UI/Combat','WBP_K02_CombatNotice',unreal.UserWidget.static_class()));root=U.call_method('AddWidget',args=(bp,unreal.CanvasPanel.static_class(),'Root',None,-1)).widget
info=U.call_method('AddWidget',args=(bp,unreal.Border.static_class(),'NoticeBackground',root,-1));border=info.widget;slot=info.slot;slot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(.5,.1),maximum=unreal.Vector2D(.5,.1)));slot.set_alignment(unreal.Vector2D(.5,0));slot.set_position(unreal.Vector2D(0,0));slot.set_auto_size(True)
border.set_brush_color(unreal.LinearColor(.012,.018,.025,.94));border.set_padding(unreal.Margin(18,10,18,10))
size=U.call_method('AddWidget',args=(bp,unreal.SizeBox.static_class(),'NoticeSize',border,-1)).widget;size.set_width_override(720)
t=U.call_method('AddWidget',args=(bp,unreal.TextBlock.static_class(),'NoticeText',size,-1)).widget;t.set_text('');t.set_auto_wrap_text(True);t.set_editor_property('justification',unreal.TextJustify.CENTER);font=t.get_editor_property('font');font.set_editor_property('size',23);font.set_editor_property('typeface_font_name','Bold');t.set_font(font);t.set_color_and_opacity(unreal.SlateColor(specified_color=unreal.LinearColor(1,.88,.64,1)));U.call_method('ToggleWidgetAsVariable',args=(bp,t,True))
B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert A.save_loaded_asset(bp,False);print('COMBAT_NOTICE_CREATED')
