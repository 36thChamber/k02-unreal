"""Own mouse-look preferences screen, keyboard/gamepad-focusable native buttons."""
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;U=unreal.get_default_object(unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet'));path='/Game/K02/UI/Settings/WBP_K02_ComfortOptions'
bp=A.load_asset(path) if A.does_asset_exist(path) else U.call_method('CreateWidgetBlueprint',args=('/Game/K02/UI/Settings','WBP_K02_ComfortOptions',unreal.UserWidget.static_class()))
existing={str(i.widget_name):i for i in U.call_method('GetWidgets',args=(bp,)).widgets}
def add(cls,name,parent=None):
 i=existing.get(name) or U.call_method('AddWidget',args=(bp,cls.static_class(),name,parent,-1));return i.widget,i.slot
def variable(w):U.call_method('ToggleWidgetAsVariable',args=(bp,w,True))
bg,_=add(unreal.Border,'Backdrop');bg.set_brush_color(unreal.LinearColor(.012,.018,.025,1));bg.set_padding(unreal.Margin(32,24,32,24));bg.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_CENTER);bg.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
scale,_=add(unreal.ScaleBox,'ResponsiveScale',bg);scale.set_stretch(unreal.Stretch.SCALE_TO_FIT);scale.set_stretch_direction(unreal.StretchDirection.DOWN_ONLY)
size,_=add(unreal.SizeBox,'PanelSize',scale);size.set_width_override(880);size.set_height_override(640)
box,_=add(unreal.VerticalBox,'Content',size)
def label(name,text,size=22,parent=box,bold=False):
 w,s=add(unreal.TextBlock,name,parent);w.set_text(text);f=w.get_editor_property('font');f.set_editor_property('size',size);f.set_editor_property('typeface_font_name','Bold' if bold else 'Regular');w.set_font(f);w.set_color_and_opacity(unreal.SlateColor(specified_color=unreal.LinearColor(.9,.92,.92,1)));w.set_auto_wrap_text(False)
 if s and hasattr(s,'set_padding'):s.set_padding(unreal.Margin(0,7,0,7))
 return w
label('Title','OPÇÕES  |  CÂMERA',32,bold=True)
label('Intro','O jogo permanece pausado. Alterações são salvas neste computador.',19)
label('Help','Sensibilidade: selecione para avançar de 0,25× até 2×. Padrão: 1×.',19)
for key,text in [('SensitivityX','Sensibilidade horizontal do mouse'),('SensitivityY','Sensibilidade vertical do mouse'),('InvertX','Inverter eixo horizontal'),('InvertY','Inverter eixo vertical')]:
 row,s=add(unreal.HorizontalBox,key+'Row',box);s.set_padding(unreal.Margin(0,9,0,9));label(key+'Name',text,22,row)
 sb,_=add(unreal.SizeBox,key+'ValueSize',row);sb.set_width_override(180)
 button,_=add(unreal.Button,key,sb);button.set_editor_property('is_focusable',True);variable(button)
 value=label(key+'Value','1×' if key.startswith('Sensitivity') else 'Não',22,button,True);value.set_editor_property('justification',unreal.TextJustify.CENTER);variable(value)
label('Limits','Estas opções não alteram o lock-on nem as janelas de combate.',19)
status=label('SaveStatus','Preferências padrão.',19);variable(status)
for name,text in [('Reset','Restaurar padrões de câmera'),('Back','Voltar ao treino')]:
 b,s=add(unreal.Button,name,box);s.set_padding(unreal.Margin(0,8,0,8));b.set_editor_property('is_focusable',True);variable(b);label(name+'Label',text,24,b,True)
label('NavigationHint','Setas / direcional: navegar  ·  Enter / confirmar: selecionar  ·  Esc: voltar',18)
B.compile_blueprint(bp,warnings_as_errors=True);assert bp.get_editor_property('Status')==unreal.BlueprintStatus.BS_UP_TO_DATE;assert A.save_loaded_asset(bp,False)
# Add entry to the existing own menu. Original controls and restart stay intact.
menu=A.load_asset('/Game/K02/UI/Training/WBP_K02_TrainingMenu');existing={str(i.widget_name):i for i in U.call_method('GetWidgets',args=(menu,)).widgets};content=existing['Content'].widget
if 'Options' not in existing:
 i=U.call_method('AddWidget',args=(menu,unreal.Button.static_class(),'Options',content,-1));b=i.widget;b.set_editor_property('is_focusable',True);i.slot.set_padding(unreal.Margin(0,5,0,5));U.call_method('ToggleWidgetAsVariable',args=(menu,b,True))
 t=U.call_method('AddWidget',args=(menu,unreal.TextBlock.static_class(),'OptionsLabel',b,-1)).widget;t.set_text('Opções de câmera');font=t.get_editor_property('font');font.set_editor_property('size',24);font.set_editor_property('typeface_font_name','Bold');t.set_font(font);t.set_auto_wrap_text(False)
for name in ['ResumeLabel','RestartLabel']:
 existing[name].widget.set_auto_wrap_text(False)
# Compact help leaves room for three controls at 720p without tiny scaling.
existing['Intro'].widget.set_text('Consulte os comandos antes de retomar. Esc abre este menu novamente.')
existing['DefenseHelp'].widget.set_text('Segure Ctrl: block. Nova pressão junto do impacto: tentativa de parry.\nCtrl + nova direção: slip. Manter a combinação não repete.\nStance não é block. Contra-ataques exigem defesa confirmada.')
existing['PanelSize'].widget.set_height_override(680)
B.compile_blueprint(menu,warnings_as_errors=True);assert A.save_loaded_asset(menu,False);print('COMFORT_WIDGET_CREATED')
