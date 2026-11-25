"""Create own focused training pause UI; no commercial widget edits."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
A=unreal.EditorAssetLibrary;path='/Game/K02/UI/Training/WBP_K02_TrainingMenu'
# Resuming this own, not-yet-integrated layout is safe; no commercial UI is touched.
U=unreal.get_default_object(unreal.load_class(None,'/Script/UMGToolSet.UMGToolSet'))
bp=A.load_asset(path) if A.does_asset_exist(path) else U.call_method('CreateWidgetBlueprint',args=('/Game/K02/UI/Training','WBP_K02_TrainingMenu',unreal.UserWidget.static_class()))
assert bp
widgets={}
existing={str(i.widget_name):i for i in U.call_method('GetWidgets',args=(bp,)).widgets}
def add(cls,name,parent=None):
 if name in existing:
  info=existing[name];widgets[name]=info.widget;return info.widget,info.slot
 info=U.call_method('AddWidget',args=(bp,cls.static_class(),name,parent,-1));widgets[name]=info.widget;return info.widget,info.slot
bg,_=add(unreal.Border,'Backdrop');bg.set_brush_color(unreal.LinearColor(.012,.018,.025,1));bg.set_padding(unreal.Margin(32,24,32,24));bg.set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_CENTER);bg.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
scale,_=add(unreal.ScaleBox,'ResponsiveScale',bg);scale.set_stretch(unreal.Stretch.SCALE_TO_FIT);scale.set_stretch_direction(unreal.StretchDirection.DOWN_ONLY)
size,_=add(unreal.SizeBox,'PanelSize',scale);size.set_width_override(880);size.set_height_override(640)
box,_=add(unreal.VerticalBox,'Content',size)
def label(name,text,size,color=(.9,.92,.92,1),bold=False,parent=box):
 w,slot=add(unreal.TextBlock,name,parent);w.set_text(text);font=w.get_editor_property('font');font.set_editor_property('size',size)
 font.set_editor_property('typeface_font_name','Bold' if bold else 'Regular')
 w.set_font(font);w.set_color_and_opacity(unreal.SlateColor(specified_color=unreal.LinearColor(*color)));w.set_auto_wrap_text(True)
 if slot and hasattr(slot,'set_padding'):slot.set_padding(unreal.Margin(0,5,0,5))
 return w
label('Title','K-02  |  TREINO',36,bold=True)
label('State','JOGO PAUSADO',20,(.85,.67,.38,1),True)
label('Intro','Comece pelo dummy. A arena só avança quando você retoma o jogo.',21)
label('Controls','W A S D  ·  mover      Mouse  ·  olhar      Shift  ·  correr\nL  ·  ativar / desativar lock-on      Espaço  ·  saltar\nClique esquerdo  ·  soco      Clique direito  ·  golpe / contra-ataque\nE  ·  chute      R  ·  chute forte      F  ·  coletar / equipar\nDuplo F  ·  descartar arma      Duplo direcional  ·  esquiva',21)
label('Defense','DEFESA E LEITURA',22,bold=True)
label('DefenseHelp','Segure Ctrl para bloquear. Uma nova pressão junto do impacto tenta parry.\nCtrl + nova entrada direcional executa slip; manter a combinação não repete.\nA fighting stance do lock-on não é block. Contra-ataques exigem defesa confirmada.',20)
for name,text in [('Resume','Retomar treino'),('Restart','Reiniciar arena')]:
 button,slot=add(unreal.Button,name,box);slot.set_padding(unreal.Margin(0,5,0,5));button.set_editor_property('is_focusable',True);U.call_method('ToggleWidgetAsVariable',args=(bp,button,True))
 style=button.get_editor_property('widget_style')
 for field,tint in [('normal',(.06,.08,.10,1)),('hovered',(.15,.22,.28,1)),('pressed',(.1,.16,.22,1))]:
  brush=style.get_editor_property(field);brush.set_editor_property('tint_color',unreal.SlateColor(specified_color=unreal.LinearColor(*tint)));style.set_editor_property(field,brush)
 button.set_style(style)
 textw=label(name+'Label',text,24,bold=True,parent=button);textw.set_editor_property('justification',unreal.TextJustify.CENTER)
 button.get_content_slot().set_padding(unreal.Margin(12,10,12,10)) if hasattr(button,'get_content_slot') else None
label('NavigationHint','Esc / botão Menu  ·  pausa     Setas / direcional  ·  navegar     Enter / confirmar  ·  selecionar',17,(.7,.76,.8,1))
B.compile_blueprint(bp,warnings_as_errors=True);B.get_default_object(bp).set_editor_property('is_focusable',True);assert A.save_loaded_asset(bp,False)
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/training-menu-created.json').write_text(json.dumps({'asset':path,'widgets':list(widgets),'status':'Layout compiled; controller binding pending'},indent=2));print('TRAINING_MENU_LAYOUT_SAVED')
