"""Compile and read the C05 integration with PIE stopped; no source asset edits."""
import unreal,json,sys
from pathlib import Path
sys.path.insert(0,'A:/K-02 5.8/Tools/Protagonist')
from kyokushin_assets import props,ROOT,MROOT,A,save
from editor_toolset.toolsets.blueprint import BlueprintTools as B
assert 'K-02 5.8' in unreal.Paths.project_dir()
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
paths=[ROOT+'/Abilities/'+n for n in ['GA_K02_HitReactions','GA_K02_Base_DefenseMode','GA_K02_DefenseMode','GA_K02_Base_Combo','GE_K02_Fighter','GA_K02_C05_Punch','GA_K02_C05_LowKickRight']]+[ROOT+'/Blueprints/BP_K02_PlayerController']+[ROOT+'/Counter/'+n for n in ['GE_K02_LowBlockOpportunity','GE_K02_C05Followup','GE_K02_LowBlockContact']]
r={'blueprints':{},'abilities':{},'effects':{},'montages':{},'graphs':{}}
for path in paths:
 bp=unreal.load_asset(path);B.compile_blueprint(bp,warnings_as_errors=True)
 status=bp.get_editor_property('Status');assert status==unreal.BlueprintStatus.BS_UP_TO_DATE,(path,status)
 save(bp);r['blueprints'][path]=str(status)
 for g in B.list_graphs(bp):
  if g.get_name() in ['K02RecordLowBlock','K02PruneLowBlockOpportunity','K02FighterHeavyInput','K02BeginLowBlockCombo','K02HasLowBlockContact','CheckAbilityCost']:
   r['graphs'][path+':'+g.get_name()]=str(B.read_graph_dsl(g))
 if '/Abilities/GA_K02_C05_' in path:r['abilities'][path]=props(unreal.get_default_object(bp.generated_class()),['abilityTags','activationOwnedTags','activationRequiredTags','activationBlockedTags','AbilityMontage','CostGameplayEffectClass'])
 if '/Counter/GE_' in path:r['effects'][path]=props(unreal.get_default_object(bp.generated_class()),['durationPolicy','durationMagnitude'])
for path in [MROOT+'/AM_K02_Kyokushin_C05_Punch',MROOT+'/AM_K02_Kyokushin_C05_LowKickRight',ROOT+'/Counter/Montages/AM_K02_LowBlock']:
 m=unreal.load_asset(path);r['montages'][path]={'properties':props(m,['blendIn','blendOut','slotAnimTracks']),'events':[]}
 for e in unreal.AnimationLibrary.get_animation_notify_events(m):
  st=e.get_editor_property('NotifyStateClass');row={'name':str(e.get_editor_property('NotifyName')),'stateClass':st.get_class().get_name() if st else None}
  if st and 'ComboBranch' in st.get_class().get_name():row['branch']=props(st,['inputActionsToContinueCombo','nextComboAbilitiesTAGs'])
  r['montages'][path]['events'].append(row)
r['pass']=all('BS_UP_TO_DATE' in v for v in r['blueprints'].values())
Path('A:/K-02 5.8/Saved/Diagnostics/C05/final-readback.json').write_text(json.dumps(r,indent=2));unreal.log('K02_C05_READBACK_FINAL '+str(r['pass']))
