import unreal
path='/Game/MACS/Classes/Components/BP_MACS_Inventory_Comp'
data=unreal.EditorAssetLibrary.find_asset_data(path)
print('ParentClass',data.get_tag_value('ParentClass'),'NativeParentClass',data.get_tag_value('NativeParentClass'))
