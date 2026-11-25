import unreal,json
from pathlib import Path
r={}
def prop(obj,key):
 try:return str(obj.get_editor_property(key))
 except Exception:return "not exposed"
for i in [1,2,3]:
 p='/Game/MACS/Animations/Fighter/AM_MACS_Fighter_Combo_1_'+str(i)+'_UE5';m=unreal.load_asset(p)
 events=[]
 for e in unreal.AnimationLibrary.get_animation_notify_events(m):
  n=e.get_editor_property('Notify');s=e.get_editor_property('NotifyStateClass')
  events.append({'name':str(e.get_editor_property('NotifyName')),'object':(s or n).get_path_name() if s or n else None,'class':(s or n).get_class().get_path_name() if s or n else None,'time':unreal.AnimationLibrary.get_anim_notify_event_trigger_time(e),'duration':unreal.AnimationLibrary.get_anim_notify_event_duration(e)})
 r[p]={'length':m.get_play_length(),'tracks':prop(m,'SlotAnimTracks'),'notify_tracks':[str(x) for x in unreal.AnimationLibrary.get_animation_notify_track_names(m)],'notifies':events,'sections':prop(m,'CompositeSections'),'blend_in':prop(m,'BlendIn'),'blend_out':prop(m,'BlendOut')}
for name in ['A_JabHead_L_IP','A_PunchHead_R_IP','A_HookHead_L_IP']:
 a=unreal.load_asset('/Game/K02/Animations/FightAnimations/Manny/'+name+'_Manny');r[name]={'length':a.get_play_length(),'frames':unreal.AnimationLibrary.get_num_frames(a)}
Path('A:/K-02 5.8/Saved/Diagnostics/fighter-combo-inspect.json').write_text(json.dumps(r,indent=2));unreal.log('K02_COMBO_INSPECT_COMPLETE')
