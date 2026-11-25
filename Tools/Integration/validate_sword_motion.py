"""Native attack input, real damage, and socket-axis tracking in PIE."""
import unreal,json,time,datetime,uuid,math,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());W=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world();p=unreal.GameplayStatics.get_player_pawn(W,0);body=next(c for c in p.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='K02Body');inv=next(c for c in p.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name()=='BP_MACS_Inventory_Comp_C');weapon=inv.call_method('GetCurrentWeaponActor');assert weapon
sm=next(c for c in weapon.get_components_by_class(unreal.StaticMeshComponent) if c.is_visible());target=next(a for a in unreal.GameplayStatics.get_all_actors_of_class(W,unreal.Pawn) if a.get_class().get_name()=='BP_K02_TrainingDummy_C');target.set_actor_location_and_rotation(p.get_actor_location()+unreal.Vector(150,0,0),unreal.Rotator(yaw=180),False,True)
i=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'))
def health():return sum(v.current_value for v in i.call_method('GetAttributeValues',args=(target,)) if v.attribute_name in ['Health','Shield'])
class Test:
 def __init__(self):self.start=unreal.GameplayStatics.get_time_seconds(W);self.before=health();self.minimum=self.before;self.sent=False;self.rows=[];self.moves=[];self.handle=unreal.register_slate_post_tick_callback(self.tick)
 def tick(self,dt):
  try:
   t=unreal.GameplayStatics.get_time_seconds(W)-self.start
   if t>.5 and not self.sent:
    q=ROOT/'Saved/NativeInputBridge';name=str(time.time_ns())+'-'+uuid.uuid4().hex[:6];f=q/(name+'.tmp');f.write_text(json.dumps({'id':name,'key':'P','created':datetime.datetime.now(datetime.timezone.utc).isoformat()}));f.rename(q/(name+'.pending.json'));self.sent=True
   a=p.mesh.get_socket_transform('MACS_Weapon_Katana').rotation;b=body.get_socket_transform('MACS_Weapon_Katana').rotation;dot=abs(a.x*b.x+a.y*b.y+a.z*b.z+a.w*b.w);angle=math.degrees(2*math.acos(min(1.,dot)))
   m=p.mesh.get_anim_instance().get_current_active_montage()
   if m and m.get_name() not in self.moves:self.moves.append(m.get_name())
   self.minimum=min(self.minimum,health());self.rows.append({'t':t,'axis_error_deg':angle,'attached_to_body':sm.get_attach_parent()==body,'montage':m.get_name() if m else None})
   if t>3:self.finish()
  except Exception:self.finish(traceback.format_exc())
 def finish(self,error=None):
  unreal.unregister_slate_post_tick_callback(self.handle);r={'error':error,'moves':self.moves,'damage':self.before-self.minimum,'max_socket_axis_error_deg':max(v['axis_error_deg'] for v in self.rows),'attachment_stable':all(v['attached_to_body'] for v in self.rows),'samples':self.rows};r['pass']=not error and bool(self.moves) and r['damage']>0 and r['attachment_stable'] and r['max_socket_axis_error_deg']<1.
  (ROOT/'Saved/Diagnostics/Integration/sword-motion-validation.json').write_text(json.dumps(r,indent=2));unreal.log('K02_SWORD_MOTION '+str(r['pass']))
test=Test()
