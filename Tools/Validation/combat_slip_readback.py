"""Compile own changed Blueprints and record the final serialized asset settings; PIE must be stopped."""
import unreal,json
from pathlib import Path
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
R='/Game/K02/Protagonist';A=unreal.EditorAssetLibrary
paths=[R+'/Abilities/'+n for n in ['GA_K02_Base_Combo','GA_K02_DefenseMode','GA_K02_Sprint','GE_K02_Fighter','GA_K02_Slip']]+[R+'/Blueprints/BP_K02_PlayerController',R+'/Locomotion/ABP_K02_Commun',R+'/Locomotion/ABP_K02_Player',R+'/Notifies/ANS_K02_ComboBranch',R+'/Slip/GE_K02_SlipIFrames']+['/Game/K02/Prototype/Blueprints/'+n for n in ['BP_K02_Player','BP_K02_Enemy','BP_K02_EnemyController']]
r={'compiled':[],'sequences':[],'gaits':[],'checks':{}}
def get(o,keys):return json.loads(unreal.ToolsetLibrary.get_object_properties(o,keys))
for p in paths:
 b=unreal.load_asset(p);B.compile_blueprint(b,warnings_as_errors=True);assert A.save_loaded_asset(b,only_if_is_dirty=False);r['compiled'].append(p)
for folder,key in [(R+'/Combat/Sequences','sequences'),(R+'/Locomotion/Sequences','gaits')]:
 for p in A.list_assets(folder):
  a=unreal.load_asset(p)
  if not isinstance(a,unreal.AnimSequence):continue
  if key=='gaits' and not a.get_name().startswith(('AS_K02_Move_','AS_K02_Run_')):continue
  r[key].append({'path':a.get_path_name(),'rootMotion':a.get_editor_property('bEnableRootMotion'),'length':a.get_play_length(),'frames':unreal.AnimationLibrary.get_num_frames(a)})
r['checks']['rootAuthority']=all(s['rootMotion'] for s in r['sequences'])
r['checks']['guardGaitCount']=len(r['gaits'])==16
ge=unreal.get_default_object(A.load_blueprint_class(R+'/Slip/GE_K02_SlipIFrames'));r['immunity']=get(ge,['durationPolicy','durationMagnitude']);r['immunityQueries']=[get(c,['immunityQueries']) for c in ge.get_editor_property('GEComponents') if 'Immunity' in c.get_class().get_name()]
r['checks']['immunityDuration']=abs(r['immunity']['durationMagnitude']['scalableFloatMagnitude']['value']-.14)<.0001
r['checks']['damageDefinitions']=len(r['immunityQueries'][0]['immunityQueries'])==4
r['freeBlendSpace']=get(unreal.load_asset(R+'/Locomotion/BS_K02_FreeLocomotion'),['sampleData','blendParameters'])
r['checks']['freeSpeedAxis']=r['freeBlendSpace']['blendParameters'][1]['max']==520
imc=unreal.load_asset(R+'/Inputs/IMC_K02_Abilities');r['mappings']=[]
for m in imc.get_editor_property('DefaultKeyMappings').get_editor_property('Mappings'):
 r['mappings'].append({'key':str(m.get_editor_property('Key')),'action':m.get_editor_property('Action').get_path_name(),'triggers':[o.get_path_name() for o in m.get_editor_property('Triggers')],'modifiers':[o.get_path_name() for o in m.get_editor_property('Modifiers')]})
r['actors']={}
for n in ['BP_K02_Player','BP_K02_Enemy']:
 c=unreal.get_default_object(A.load_blueprint_class('/Game/K02/Prototype/Blueprints/'+n));r['actors'][n]={'effect':c.get_editor_property('K02FighterStyleEffect').get_path_name(),'anim':c.mesh.get_editor_property('AnimClass').get_path_name(),'movement':get(c.character_movement,['maxWalkSpeed','maxAcceleration','brakingDecelerationWalking'])}
r['checks']['sharedFighter']=len(set(v['effect'] for v in r['actors'].values()))==1
s=unreal.get_default_object(A.load_blueprint_class(R+'/Abilities/GA_K02_Sprint'));r['sprint']=get(s,['blockAbilitiesWithTag','activationBlockedTags','costGameplayEffectClass']);r['checks']['sprintAllowsAttack']=not r['sprint']['blockAbilitiesWithTag']['gameplayTags']
r['pass']=all(r['checks'].values());Path('A:/K-02 5.8/Saved/Diagnostics/CombatSlip/final-readback.json').write_text(json.dumps(r,indent=2));unreal.log('K02_COMBAT_SLIP_READBACK '+str(r['pass']))
