"""Assign per-character source materials to all Combined and modular variants."""
import unreal,json
from pathlib import Path
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir());PKG=Path('A:/K-02-ArtLab/char_design/Deliveries/Figurinos-UE5-v001')
A=unreal.EditorAssetLibrary;AT=unreal.AssetToolsHelpers.get_asset_tools();M=unreal.MaterialEditingLibrary
master=unreal.load_asset('/Game/K02/Characters/Common/Materials/M_K02_Surface_v001');assert master
manifest=json.loads((ROOT/'Saved/Diagnostics/Integration/protagonist-import.json').read_text());cache={};rows=[]
for entry in manifest:
 ident=entry['id'];BASE='/Game/K02/Characters/Protagonist/'+entry['revision'];mesh=unreal.load_asset(entry['asset'])
 source=json.loads((ROOT/'Saved/Diagnostics/Integration'/'K02-source.json').read_text())
 blend=Path(source['source']);images={n['image']:(blend.parent/n['file'][2:].replace('\\','/')).resolve() for m in source['materials'].values() for n in m['nodes'] if n['type']=='TEX_IMAGE'}
 materials=list(mesh.materials)
 for slot in materials:
  name=str(slot.material_slot_name);key=ident+':'+name
  if key in cache:slot.material_interface=cache[key];continue
  data=source['materials'][name];mi_name='MI_'+ident+'_'+name.replace('tripo_','').replace('-','_').replace('.','_')
  path=BASE+'/Materials/'+mi_name
  mi=unreal.load_asset(path) if A.does_asset_exist(path) else AT.create_asset(mi_name,BASE+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
  M.set_material_instance_parent(mi,master);row={'id':ident,'slot':name,'material':path,'textures':{}}
  for image_node in [n for n in data['nodes'] if n['type']=='TEX_IMAGE']:
   img=image_node['image'];file=images[img];assert file.is_file(),file
   param='Normal' if 'normal' in img.lower() else ('PackedMR' if 'metallic' in img.lower() or 'ORM_' in img else 'BaseColor')
   dest=BASE+'/Textures/'+file.stem
   if not A.does_asset_exist(dest):
    task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(file),'destination_path':BASE+'/Textures','destination_name':file.stem,'automated':True,'save':True,'replace_existing':False});AT.import_asset_tasks([task])
   tex=unreal.load_asset(dest);assert tex
   tex.set_editor_properties({'srgb':param=='BaseColor','compression_settings':unreal.TextureCompressionSettings.TC_NORMALMAP if param=='Normal' else (unreal.TextureCompressionSettings.TC_MASKS if param=='PackedMR' else unreal.TextureCompressionSettings.TC_DEFAULT)})
   if param=='Normal':tex.set_editor_property('flip_green_channel',True)
   A.save_loaded_asset(tex,False);M.set_material_instance_texture_parameter_value(mi,param,tex);assert M.get_material_instance_texture_parameter_value(mi,param)==tex
   row['textures'][param]={'source':str(file),'asset':dest,'srgb':param=='BaseColor','flip_green':param=='Normal'}
  values=next((n['values'] for n in data['nodes'] if n['type']=='BSDF_PRINCIPLED'),{})
  if not row['textures']:
   M.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*values.get('Base Color',[1,1,1,1])))
   M.set_material_instance_scalar_parameter_value(mi,'MinimumRoughness',max(.55,values.get('Roughness',.55)))
  # Preserve intentionally metallic small pieces, no generalized plastic sheen.
  if values.get('Metallic',0)>.5:M.set_material_instance_scalar_parameter_value(mi,'MetallicScale',values['Metallic'])
  M.update_material_instance(mi);assert A.save_loaded_asset(mi,False);cache[key]=mi;slot.material_interface=mi;rows.append(row)
 mesh.set_editor_property('materials',materials);assert A.save_loaded_asset(mesh,False)
 (ROOT/'Saved/Diagnostics/Integration/protagonist-materials.json').write_text(json.dumps({'master':master.get_path_name(),'materials':rows},indent=2))
print('Assigned',len(rows),'materials across',len(manifest),'meshes')
