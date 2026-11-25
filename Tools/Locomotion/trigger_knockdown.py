"""Manual editor-only playtest helper. Run in PIE, then hold WASD during the MACS knockdown."""
import unreal,re
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();assert w,'Run PIE first'
p=unreal.GameplayStatics.get_player_pawn(w,0);assert p,'Player missing'
targets=[a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Character) if a!=p];assert targets,'An instigator/dummy is required'
s=p.call_method('GetHitReaction');text=s.export_text();text=re.sub(r'ControlType_[^=]*=NewEnumerator\d+',lambda m:m.group(0).split('=')[0]+'=NewEnumerator3',text);text=re.sub(r'Instigator_[^=]*=(?:"[^"]*"|None)',lambda m:m.group(0).split('=')[0]+'="'+targets[0].get_path_name()+'"',text);s.import_text(text);p.call_method('SetHitReactionOnServer',args=(s,));unreal.log('K02 manual real knockdown: focus the viewport and hold WASD until recovery starts; no key selects neutral.')
