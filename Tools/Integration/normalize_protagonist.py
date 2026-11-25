import sys,json
from pathlib import Path
ROOT=Path('A:/K-02 5.8');ART=Path('A:/K-02-ArtLab/char_design');BASE=ART/'Characters/Protagonist/Integration/UE5_v001';OUT=ROOT/'Saved/Diagnostics/Integration/Protagonist';OUT.mkdir(exist_ok=True)
files=[(BASE/'Sources/SK_K02_Dogi_Combined_v001.fbx','SK_K02_Dogi_Combined_v001'),(BASE/'Sources/SK_K02_BodyForDogi_v001.fbx','SK_K02_BodyForDogi_v001'),(ART/'Characters/Protagonist/Clothing/Tripo_Dogi_v001/Exports/SK_K02_Dogi_v002.fbx','SK_K02_Dogi_v002'),(ART/'A_Definitive/K02_Skeletal.fbx','SK_K02_SourceFullBody_v001')]
rows=[]
for src,name in files:
 dst=BASE/'Derivatives'/(name+'.fbx')
 for script,args in [('normalize_fbx_units.py',[str(src),str(dst)]),('verify_fbx_derivative.py',[str(src),str(dst),str(OUT/(name+'.json'))])]:
  path=ROOT/'Tools/Integration'/script;sys.argv=[str(path),'--']+args;exec(compile(path.read_text(),str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
 rows.append({'source':str(src),'derived':str(dst),'name':name,'pass':True})
 (OUT/'derivatives.json').write_text(json.dumps(rows,indent=2))
print('Protagonist derivatives verified',len(rows))
