"""Read runtime HUD properties/components without changing marketplace assets."""
import unreal,json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert w
pc=unreal.GameplayStatics.get_player_controller(w,0);p=unreal.GameplayStatics.get_player_pawn(w,0);hud=pc.get_hud();ui=hud.get_editor_property('UI');r={'pass':True,'hud':{},'overhead':[]}
for key in ['BP_MACS_GAS_CharData','BP_MACS_GAS_CharData_Target']:
 u=ui.get_editor_property(key);r['hud'][key]={'class':u.get_class().get_path_name(),'properties':json.loads(unreal.ToolsetLibrary.get_object_properties(u,[]))}
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Character):
 for c in a.get_components_by_class(unreal.WidgetComponent):
  u=c.get_user_widget_object();r['overhead'].append({'actor':a.get_class().get_name(),'component':c.get_name(),'widget':u.get_class().get_path_name() if u else None})
(Path(unreal.Paths.project_dir())/'Saved/Diagnostics/Integration/runtime-hud-widgets.json').write_text(json.dumps(r,indent=2));print('HUD_WIDGETS_READ')
