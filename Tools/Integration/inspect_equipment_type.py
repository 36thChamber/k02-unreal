import unreal,json
from editor_toolset.toolsets.blueprint import BlueprintTools as B
x=unreal.load_asset('/Game/MACS/Classes/Components/BP_MACS_Inventory_Comp');print(x,x.get_class().get_name());print([n for n in dir(B) if 'class' in n.lower() or 'parent' in n.lower()]);print(unreal.ToolsetLibrary.get_object_properties(x,['ParentClass','GeneratedClass']))
