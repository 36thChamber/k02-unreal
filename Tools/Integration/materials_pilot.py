"""Explicit PBR mapping from the editable source; isolated stylized surface.

No renderer changes. Normal maps are OpenGL; G is inverted on import. Packed
roughness uses G and metallic B; the unverified red channel is not treated as AO.
"""
import json
from pathlib import Path
import unreal
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
ROOT=Path(unreal.Paths.project_dir()).resolve()
SOURCE=Path('A:/K-02-ArtLab/char_design/Deliveries/Figurinos-UE5-v001/B_1')
BASE='/Game/K02/Characters/Roster/B_1'
A=unreal.EditorAssetLibrary
AT=unreal.AssetToolsHelpers.get_asset_tools()
M=unreal.MaterialEditingLibrary
source=json.loads((ROOT/'Saved/Diagnostics/Integration/B_1-source.json').read_text())
report=json.loads((SOURCE/'Validation/export-reimport.json').read_text())
images={x['image']:SOURCE/'Textures'/Path(x['path'].replace('\\','/')).name for x in report['textures']}
mesh=unreal.load_asset('/Game/K02/Validation/ImportProbeV3/B_1/Meshes/SK_B_1_Combined_v009')
masterpath='/Game/K02/Characters/Common/Materials/M_K02_Surface_v001'
master=unreal.load_asset(masterpath) if A.does_asset_exist(masterpath) else None
maskpath='/Game/K02/Characters/Common/Textures/T_K02_DefaultMasks'
if not A.does_asset_exist(maskpath):A.duplicate_asset('/Engine/EngineResources/WhiteSquareTexture',maskpath)
mask=unreal.load_asset(maskpath)
mask.set_editor_property('srgb',False)
mask.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS)
A.save_loaded_asset(mask,False)
def node(cls,x,y,**props):
    n=M.create_material_expression(master,cls,x,y)
    n.set_editor_properties(props)
    return n
def link(src,output,dst,input):assert M.connect_material_expressions(src,output,dst,input)
if not master:
    master=AT.create_asset('M_K02_Surface_v001','/Game/K02/Characters/Common/Materials',unreal.Material,unreal.MaterialFactoryNew())
    # Defaults resolve all texture parameters while the shader is compiled.
    white=unreal.load_asset('/Engine/EngineResources/WhiteSquareTexture')
    normal=unreal.load_asset('/Engine/EngineMaterials/DefaultNormal')
    assert white and normal
    bc=node(unreal.MaterialExpressionTextureSampleParameter2D,-800,-300,parameter_name='BaseColor',texture=white)
    tint=node(unreal.MaterialExpressionVectorParameter,-800,-100,parameter_name='Tint',default_value=unreal.LinearColor(1,1,1,1))
    mult=node(unreal.MaterialExpressionMultiply,-500,-300)
    link(bc,'RGB',mult,'A');link(tint,'RGB',mult,'B')
    assert M.connect_material_property(mult,'',unreal.MaterialProperty.MP_BASE_COLOR)
    packed=node(unreal.MaterialExpressionTextureSampleParameter2D,-800,200,parameter_name='PackedMR',texture=mask,sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    minimum=node(unreal.MaterialExpressionScalarParameter,-800,420,parameter_name='MinimumRoughness',default_value=.55)
    rough=node(unreal.MaterialExpressionMax,-450,200)
    link(packed,'G',rough,'A');link(minimum,'',rough,'B')
    assert M.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    metal=node(unreal.MaterialExpressionScalarParameter,-800,560,parameter_name='MetallicScale',default_value=0)
    metmult=node(unreal.MaterialExpressionMultiply,-450,520)
    link(packed,'B',metmult,'A');link(metal,'',metmult,'B')
    assert M.connect_material_property(metmult,'',unreal.MaterialProperty.MP_METALLIC)
    spec=node(unreal.MaterialExpressionScalarParameter,-450,680,parameter_name='Specular',default_value=.25)
    assert M.connect_material_property(spec,'',unreal.MaterialProperty.MP_SPECULAR)
    nm=node(unreal.MaterialExpressionTextureSampleParameter2D,-800,850,parameter_name='Normal',texture=normal,sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    strength=node(unreal.MaterialExpressionVectorParameter,-800,1100,parameter_name='NormalXY',default_value=unreal.LinearColor(.5,.5,1,1))
    nmult=node(unreal.MaterialExpressionMultiply,-450,850)
    link(nm,'RGB',nmult,'A');link(strength,'RGB',nmult,'B')
    norm=node(unreal.MaterialExpressionNormalize,-200,850);link(nmult,'',norm,'VectorInput')
    assert M.connect_material_property(norm,'',unreal.MaterialProperty.MP_NORMAL)
    M.recompile_material(master);assert A.save_loaded_asset(master,False)
from editor_toolset.toolsets.material import MaterialTools
for expression in MaterialTools.get_expressions(master):
    if isinstance(expression,unreal.MaterialExpressionTextureSampleParameter2D) and str(expression.get_editor_property('parameter_name'))=='PackedMR':
        expression.set_editor_properties({'texture':mask,'sampler_type':unreal.MaterialSamplerType.SAMPLERTYPE_MASKS})
M.recompile_material(master)
assert A.save_loaded_asset(master,False)
rows=[]
materials=list(mesh.materials)
for slot in materials:
    name=str(slot.material_slot_name)
    data=source['materials'][name]
    mi_name='MI_B_1_'+name.replace('tripo_','').replace('-','_')
    path=BASE+'/Materials/'+mi_name
    mi=unreal.load_asset(path) if A.does_asset_exist(path) else AT.create_asset(mi_name,BASE+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    M.set_material_instance_parent(mi,master)
    row={'slot':name,'material':path,'textures':{}}
    for image_node in [n for n in data['nodes'] if n['type']=='TEX_IMAGE']:
        img=image_node['image'];file=images[img];assert file.is_file(),file
        param='Normal' if 'normal' in img.lower() else ('PackedMR' if 'metallic' in img.lower() or 'ORM_' in img else 'BaseColor')
        dest=BASE+'/Textures/'+file.stem
        if not A.does_asset_exist(dest):
            task=unreal.AssetImportTask();task.set_editor_properties({'filename':str(file),'destination_path':BASE+'/Textures','destination_name':file.stem,'automated':True,'save':True,'replace_existing':False})
            AT.import_asset_tasks([task])
        tex=unreal.load_asset(dest)
        tex.set_editor_property('srgb',param=='BaseColor')
        tex.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP if param=='Normal' else (unreal.TextureCompressionSettings.TC_MASKS if param=='PackedMR' else unreal.TextureCompressionSettings.TC_DEFAULT))
        if param=='Normal':tex.set_editor_property('flip_green_channel',True)
        assert A.save_loaded_asset(tex,False)
        # UE 5.8 implementation returns false even after a successful assignment.
        M.set_material_instance_texture_parameter_value(mi,param,tex)
        assert M.get_material_instance_texture_parameter_value(mi,param)==tex
        row['textures'][param]={'source':str(file),'asset':dest,'srgb':param=='BaseColor','flip_green':param=='Normal'}
    if not row['textures']:
        values=next(n['values'] for n in data['nodes'] if n['type']=='BSDF_PRINCIPLED')
        M.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(*values['Base Color']))
        M.set_material_instance_scalar_parameter_value(mi,'MinimumRoughness',values['Roughness'])
    M.update_material_instance(mi)
    assert A.save_loaded_asset(mi,False)
    slot.material_interface=mi
    rows.append(row)
mesh.set_editor_property('materials',materials)
assert A.save_loaded_asset(mesh,False)
(ROOT/'Saved/Diagnostics/Integration/pilot-materials.json').write_text(json.dumps({'master':masterpath,'slots':rows},indent=2))
print('Mapped '+str(len(rows))+' source material slots; no global renderer changes')
