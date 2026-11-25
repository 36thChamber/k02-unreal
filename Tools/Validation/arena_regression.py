import unreal, json
from pathlib import Path
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
assert w
p=unreal.GameplayStatics.get_player_pawn(w,0)
a=unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)
ins=unreal.get_default_object(unreal.load_class(None,'/Script/GASToolsets.AbilitySystemInspectorToolset'))
r={'player':p.get_class().get_name(),'tags':list(ins.call_method('GetActiveTags',args=(p,))),'actors':[]}
for x in a:
 if x.get_class().get_name().startswith('BP_K02_'):
  d={'name':x.get_name(),'class':x.get_class().get_name(),'location':str(x.get_actor_location())}
  if isinstance(x,unreal.Pawn):
   c=x.get_controller();d['controller']=c.get_class().get_name() if c else None
   d['team']=x.get_editor_property('TeamID')
   d['tags']=list(ins.call_method('GetActiveTags',args=(x,)))
  r['actors'].append(d)
en=next(x for x in a if x.get_class().get_name()=='BP_K02_Enemy_C')
path=unreal.NavigationSystemV1.find_path_to_location_synchronously(w,p.get_actor_location(),en.get_actor_location())
r['nav_valid']=bool(path and path.is_valid());r['nav_points']=len(path.path_points) if path else 0
r['navmesh_count']=len(unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RecastNavMesh))
assert r['player']=='BP_K02_Player_C'
assert 'MACS_GAS.Abilities.States.WeaponClass.Fighter' in r['tags']
assert r['nav_valid'] and r['nav_points']>=2
assert any(x.get('controller')=='BP_K02_EnemyController_C' for x in r['actors'])
r['status']='pass'
Path('A:/K-02 5.8/Saved/Diagnostics/arena-regression.json').write_text(json.dumps(r,indent=2))
unreal.log('K02_ARENA_REGRESSION '+json.dumps(r))
