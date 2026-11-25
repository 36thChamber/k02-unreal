"""Own per-character collision based on preserved skin, not garment volume."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir());R={'B_1':'v009','B_2':'v005','B_3':'v002','B_K02':'v002','K02_F':'v005'}
for ident,rev in R.items():
 base='/Game/K02/Characters/Roster/'+ident+'/'+rev
 for file in ['prepare_protagonist_contact.py','fit_protagonist_trace_sockets.py']:
  s=(ROOT/'Tools/Integration'/file).read_text().replace('/Game/K02/Characters/Protagonist/Dogi_v001',base)
  s=s.replace('SK_K02_Dogi_Combined_v001','SK_'+ident+'_Combined_'+rev).replace('SK_K02_BodyForDogi_v001','SK_'+ident+'_BodyForCostume_'+rev)
  s=s.replace('IK_K02_Protagonist','IK_'+ident).replace('PA_K02_Protagonist_Query_v001','PA_'+ident+'_Query_v001')
  s=s.replace('Protagonist/contact-regions.json',ident+'-contact-regions.json').replace('protagonist-contact.json',ident+'-contact.json').replace('protagonist-socket-fit.json',ident+'-socket-fit.json')
  exec(compile(s,file,'exec'),{'__name__':'__main__'})
print('Five own query collision assets and anatomical trace centers prepared; gameplay tests pending')
