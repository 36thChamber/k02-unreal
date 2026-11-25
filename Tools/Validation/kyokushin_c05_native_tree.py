"""Existing C01-C04/C08 through window inputs, through an external native-input worker.

The old test's AttachThreadInput/SetForegroundWindow path could block the editor.
This changes the automation only, retaining its sequences/contact assertions.
"""
from pathlib import Path
base=Path('A:/K-02 5.8/Tools/Validation/kyokushin_tree_regression.py').read_text().split('k02_tree_test=')[0]
base=base.replace('kyokushin-tree-results.json','C05/existing-tree.json')
params=globals().get('REQUEST',{}).get('params',{})
output=params.get('output','existing-tree')
assert output.replace('-','').replace('_','').isalnum()
base=base.replace('C05/existing-tree.json','C05/'+output+'.json')
base=base.replace("row.pop('frameTimes')", "row['maxFrameMs']=max(row['frameTimes'])*1000;row.pop('frameTimes')")
begin=base.index('  windows=[]')
end=base.index('  name,inputs',begin)
base=base[:begin]+'''  windows=[]
  def visit(h,p):
   pid=ctypes.c_ulong();ctypes.windll.user32.GetWindowThreadProcessId(h,ctypes.byref(pid));buf=ctypes.create_unicode_buffer(512);ctypes.windll.user32.GetWindowTextW(h,buf,512)
   if pid.value==os.getpid() and 'Unreal Editor' in buf.value:windows.append(h)
   return True
  ctypes.windll.user32.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)(visit),0)
  assert windows
  self.input_hwnd=windows[0]
  unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')
'''+base[end:]
# Keep all keys in the same window event path; do not send global desktop input.
base=base.replace("else:assert self.slate.call_method('PressKey',args=('E' if key=='K' else 'R',))", "else:\n   vk=0x45 if key=='K' else 0x52\n   ctypes.windll.user32.PostMessageW(self.input_hwnd,0x100,vk,(ctypes.windll.user32.MapVirtualKeyW(vk,0)<<16)|1)\n   self.key_release=(self.clock+.05,vk)")
base=base.replace("assert self.slate.call_method('PressKey',args=('R',));", "self.pulse('T');")
# Do not change focus/capture from a Slate tick; this can deadlock the Editor.
base=base.replace("  unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetInputMode_GameOnly',args=(self.pc,True));unreal.GameplayStatics.set_viewport_mouse_capture_mode(self.w,unreal.MouseCaptureMode.CAPTURE_PERMANENTLY_INCLUDING_INITIAL_MOUSE_DOWN)\n",'')
base=base.replace("  unreal.get_default_object(unreal.load_class(None,'/Script/UMG.WidgetBlueprintLibrary')).call_method('SetFocusToGameViewport')\n",'')
base=base.replace('   self.clock=now\n', '''   self.clock=now
   if getattr(self,'key_release',None) and now>=self.key_release[0]:
    vk=self.key_release[1];ctypes.windll.user32.PostMessageW(self.input_hwnd,0x101,vk,(ctypes.windll.user32.MapVirtualKeyW(vk,0)<<16)|0xC0000001);self.key_release=None
''')
exec(base,globals())
s=Path('A:/K-02 5.8/Tools/Validation/kyokushin_c08_regression.py').read_text()
exec(s[s.index('class C08TreeTest'):].split('k02_c08_test=C08TreeTest()')[0],globals())
class SettledTree(C08TreeTest):
 def __init__(self):
  self.progress_wall=time.monotonic();super().__init__()
  for actor in unreal.GameplayStatics.get_all_actors_of_class(self.w,unreal.Pawn):
   if actor not in [self.p,self.target]:
    actor.set_actor_location(unreal.Vector(10000,10000,92),False,True)
  self.pawn_path=self.p.get_path_name()
  if params.get('trace_after_body'):
   trace=next(c for c in self.p.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name()=='BP_MACS_TraceComp_C');body=next(c for c in self.p.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='K02Body');trace.add_tick_prerequisite_component(body)

 def pulse(self,key):
  import datetime,uuid
  queue=Path('A:/K-02 5.8/Saved/NativeInputBridge');queue.mkdir(exist_ok=True)
  ident=str(time.time_ns())+'-'+uuid.uuid4().hex[:6]
  job={'id':ident,'key':key,'created':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  tmp=queue/(ident+'.tmp');tmp.write_text(json.dumps(job));tmp.rename(queue/(ident+'.pending.json'))
  self.cur.setdefault('native_inputs',[]).append(ident)
 def begin(self):
  super().begin()
  if self.cur:
   self.start=self.clock+.5
   if self.cur['case'].startswith('C03') and not self.cur['far'] and params.get('c03_distance'):
    self.target.set_actor_location(unreal.Vector(-710+float(params['c03_distance']),-500,92),False,True)
   if self.cur['case'].startswith('C02') and not self.cur['far'] and params.get('c02_distance'):
    self.target.set_actor_location(unreal.Vector(-710+float(params['c02_distance']),-500,92),False,True)
   self.cur['initial_distance_cm']=self.p.get_actor_location().distance(self.target.get_actor_location())
 def tick(self,dt):
  try:
   wall=time.monotonic();now=unreal.GameplayStatics.get_time_seconds(self.w)
   if now>self.clock:self.progress_wall=wall
   elif wall-self.progress_wall>3:
    self.finish('World clock stalled; native inputs were independently released');return
   if self.cur and self.cur['case'].startswith('C02') and params.get('capture_contact'):
    body=next((c for c in self.p.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name()=='K02Body'),None);m=self.p.mesh.get_anim_instance().get_current_active_montage()
    if body and m:
     self.cur.setdefault('anatomical_contact',[]).append({'t':self.clock-self.start,'montage':m.get_name(),'position':self.p.mesh.get_anim_instance().montage_get_position(m),'hand_l':body.get_socket_location('hand_l_Trace_Sphere').to_tuple(),'hand_r':body.get_socket_location('hand_r_Trace_Sphere').to_tuple(),'source_l':self.p.mesh.get_socket_location('hand_l_Trace_Sphere').to_tuple(),'target':self.target.get_actor_location().to_tuple(),'player':self.p.get_actor_location().to_tuple(),'target_montage':str(self.target.mesh.get_anim_instance().get_current_active_montage())})
     if params.get('capture_geometry') and 'M04' in m.get_name():
      hand=body.get_socket_location('hand_r_Trace_Sphere');pa=self.target.mesh.get_skinned_asset().get_editor_property('physics_asset');closest=[]
      for bone in unreal.get_default_object(unreal.load_class(None,'/Script/PhysicsToolsets.PhysicsAssetToolset')).call_method('GetBodyNames',args=(pa,)):
       dist,point=self.target.mesh.get_closest_point_on_collision(hand,bone)
       if dist>=0:closest.append({'bone':str(bone),'distance':dist,'point':point.to_tuple()})
      trace=next(c for c in self.p.get_components_by_class(unreal.ActorComponent) if c.get_class().get_name()=='BP_MACS_TraceComp_C');sample=self.cur['anatomical_contact'][-1];sample['closest_body']=min(closest,key=lambda x:x['distance']) if closest else None;sample['tracing']=trace.get_editor_property('IsTracing');sample['target_already_hit']=self.target in trace.get_editor_property('HittedActors');sample['target_pelvis']=self.target.mesh.get_socket_location('pelvis').to_tuple();sample['last_trace_positions']=[v.to_tuple() for v in trace.get_editor_property('LastTracePositions')];sample['trace_components']=[{'name':c.get_name(),'location':c.get_world_location().to_tuple(),'radius':c.get_scaled_sphere_radius()} for c in self.p.get_components_by_class(unreal.SphereComponent) if c.get_attach_parent()==body]

   super().tick(dt)
  except Exception:self.finish(traceback.format_exc())
k02_c08_test=SettledTree()
exec(s.split('k02_c08_test=C08TreeTest()')[1],globals())
if params.get('cases'):
 k02_c08_test.cases=[c for c in k02_c08_test.cases if c[0] in params['cases']]*int(params.get('repeat',1))
