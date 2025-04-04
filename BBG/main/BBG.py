
import bpy
import re
import math
import bmesh
import mathutils
import pathlib
import os


#----------------OBJECT MODE ONLY--------------------------
class ObjectModeOnlyOperator(bpy.types.Operator):
    """Base class to restrict execution to Object Mode"""
    
    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.mode == 'OBJECT'

#---------------------------------------------------
# COLLIDER MATERIAL NAME
#---------------------------------------------------

ColliderMaterial_name = "COL_DEFAULT"

#---------------------------------------------------
# Guidelines TEXT
#---------------------------------------------------

GUIDELINES_TEXT_DATA = ""

class GetGuidelinesFile(bpy.types.Operator):
    bl_idname = "wm.get_guidelines"
    bl_label = "GetGuidelines"

    def execute(self, context):
        global GUIDELINES_TEXT_DATA
        
        script_path = __file__
        
        # running only if in text editor (Blender editor reasons)
        if bpy.context.space_data != None and bpy.context.space_data.type == "TEXT_EDITOR":
            script_path = bpy.context.space_data.text.filepath
        else:
            script_path = __file__
        
        
        script_dir = pathlib.Path(script_path).resolve().parent

        guidelines_file = open(os.path.join(script_dir, "guidelines.txt"), 'r')
        
        print(guidelines_file)

        GUIDELINES_TEXT_DATA = guidelines_file.read()

        guidelines_file.close()         
            
        return {'FINISHED'}


#---------------------------------------------------
# Guidelines
#---------------------------------------------------    
    
class VIEW3D_PT_CustomPanel(bpy.types.Panel):
    """Creates a Panel in the 3D View Sidebar"""
    bl_label = "BBG VR Guidelines"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "object"
    bl_category = 'BBG'
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.open_custom_text_window", text="Open Guidelines", icon='TEXT')
        
        
# Operator to Open the Custom Window
class TEXT_OT_OpenCustomWindow(bpy.types.Operator):
    """Open a window with guidelines"""
    bl_idname = "wm.open_custom_text_window"
    bl_label = "Open Text Window"
    bl_options = {'REGISTER', 'UNDO'}
    
    text_data: bpy.props.StringProperty(name="Text Data", default="")

    def execute(self, context):
        bpy.ops.wm.get_guidelines()
        self.text_data = GUIDELINES_TEXT_DATA
        
        context.window_manager.text_window_text = self.text_data  # Store for UI
        bpy.ops.wm.custom_text_popup('INVOKE_DEFAULT')
        return {'FINISHED'}

# Pop-up Window Class
class TEXT_OT_CustomTextPopup(bpy.types.Operator):
    """Custom floating window for displaying text"""
    bl_idname = "wm.custom_text_popup"
    bl_label = "BBG VR GUIDELINES"

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        
        # Display each line separately
        for line in GUIDELINES_TEXT_DATA.split("\n"):
            layout.label(text=line)  

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)


# Register
def GuidelinesRegister():
    bpy.utils.register_class(GetGuidelinesFile)
    bpy.utils.register_class(TEXT_OT_OpenCustomWindow)
    bpy.utils.register_class(TEXT_OT_CustomTextPopup)
    bpy.utils.register_class(VIEW3D_PT_CustomPanel)
    bpy.types.WindowManager.text_window_text = bpy.props.StringProperty(name="Text Window Data", default="")

def GuidelinesUnregister():
    bpy.utils.unregister_class(GetGuidelinesFile)
    bpy.utils.unregister_class(TEXT_OT_OpenCustomWindow)
    bpy.utils.unregister_class(TEXT_OT_CustomTextPopup)
    bpy.utils.unregister_class(VIEW3D_PT_CustomPanel)

    del bpy.types.WindowManager.text_window_text
#---------------------------------------------------
# /Guidelines
#---------------------------------------------------



#---------------------------------------------------
# Checks
#---------------------------------------------------

class CheckPanel(bpy.types.Panel):
    bl_label = "Checks"
    bl_idname = "scale_check"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BBG'
    bl_options = {"HEADER_LAYOUT_EXPAND"}
     
    def draw(self, context):
        layout = self.layout
        
        #SCALES BOX
        boxScale = layout.box()
        boxScale.label(text="SCALE")
        rowScale = boxScale.row() 
        rowScale.operator("object.check_scales", text="Scale Check")
        
        #MATERIALS BOX
        boxMaterials = layout.box()
        boxMaterials.label(text="MATERIALS")
        boxMaterials.row().operator("wm.format_check", text="Material Check")
        boxMaterials.row().operator("wm.texture_format_check", text="Texture Check")
        
        #CLEAN BOX
        boxClean = layout.box()
        boxClean.label(text="CLEAN")
        boxClean.row().operator("wm.clean_materials", text="Clean Materials")
        boxClean.row().operator("wm.clean_textures", text="Clean Textures")

        #OTHER/settings BOX "header"
        other_props = context.scene.other_properties
        layout.row().prop(other_props, "show_collapse", text="SETTINGS", icon="TRIA_DOWN" if other_props.show_collapse else "TRIA_RIGHT", emboss=False)

        # Collapsible content of OTHER/settings box
        if other_props.show_collapse:
            boxOther = layout.box()
            rowOther = boxOther.row() 
            #rowOther.prop(context.scene.other_properties, "include_prototype_root", text="PROTOTYPE Export")
            rowOther.prop(context.scene.other_properties, "export_mode_enum", text="Mode")
            boxOther.row().prop(context.scene.other_properties, "custom_collider_name", text="Material Name")
            boxOther.row().prop(context.scene, "include_name_MATERIAL", text="Include \"Material\"")
            #rowOther.operator("object.check_normals", text="Check Normals")


#---------------------------------------------------
# /Checks
#---------------------------------------------------


#---------------------------------------------------
# Export Check (Custom Window)
#---------------------------------------------------

class ExportChecksWindowPanel(bpy.types.Panel):
    """Export FBX Checks"""
    bl_label = "Checks"
    bl_idname = "export_window_custom_panel"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS" #right side
    bl_category = "Export" 

    @classmethod
    def poll(cls, context):
        return context.space_data.active_operator and context.space_data.active_operator.bl_idname == "EXPORT_SCENE_OT_fbx"

    def draw(self, context):
        box = self.layout.box()
        
        box.operator("export_scene.fbx_with_count", text="Run Checks")

#---------------------------------------------------
# /Export Check (Custom Window)
#---------------------------------------------------


#---------------------------------------------------
# Export Check (Custom Export)
#---------------------------------------------------
# Adds a custom Export FBX button and checks basic stuff (Root,Scale,Format)
class ExportFBXWithChecks(bpy.types.Operator):
    """Custom FBX Export"""
    bl_idname = "export_scene.fbx_with_count"
    bl_label = "Export FBX with Count"
    
    
    def execute(self, context):
        
        # Check if not in design mode
        active_export_mode = bpy.context.scene.other_properties.export_mode_enum
        
        # Mode name
        check_mode_name = self.get_mode_for_title()
    
        if active_export_mode == 'OP3':
            self.open_fbx_export_window()
            return {'CANCELLED'}
        
        # messages for popup
        check_messages= []
        check_icons= []
        
        # for scale check
        select_bool = False
        export_bool = True    
        
        #-------Run All Checks----------
        
        
        #--------------ROOT CHECK-----------------------------   
        if object_root_check():
            check_messages.append("ROOT")
            check_icons.append('CHECKMARK')
        else:
            check_messages.append("ROOT")
            check_icons.append('CANCEL')
            self.report({'ERROR'}, check_mode_name+ f" -ROOT ERROR!!!")
            
            
        # Get objects to check
        objects_to_check = []
        
        if len(context.selected_objects) > 1:
            objects_to_check = context.selected_objects
            select_bool = True
        elif len(context.selected_objects) == 1:
            objects_to_check = [context.selected_objects[0]]
        else:
            objects_to_check = [obj for obj in context.visible_objects if obj.type == 'MESH']
        
        
        #--------------MATERIALS CHECK-----------------------------   
        invalid_materials = check_material_format(objects_to_check)
        
        if invalid_materials:
            check_messages.append("MATERIALS")
            check_icons.append('CANCEL')
            self.report({'ERROR'}, check_mode_name+ f" -MATERIAL ERROR!!!")
        else:
            check_messages.append("MATERIALS")
            check_icons.append('CHECKMARK')
        
        
        
        #--------------SCALE CHECK-----------------------------   
            
        objects, error = get_objects_recursive(export_bool, select_bool)

        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}

        if objects:
            check_messages.append("SCALES")
            check_icons.append('CANCEL')
            self.report({'ERROR'}, check_mode_name+ f" -SCALES ERROR!!!")
        else:
            check_messages.append("SCALES")
            check_icons.append('CHECKMARK')
            

        #--------------COL CHECK-----------------------------        
        if not check_has_col(objects_to_check):
            check_messages.append("COLLIDERS")
            check_icons.append('SEQUENCE_COLOR_02')
            
            
            
        # IF EXPORT MODE FINAL
        if active_export_mode == 'OP1':
            
            #--------------TEXTURE CHECK-----------------------------   
            invalid_material_textures = check_albedo_texture_format(objects_to_check)
            
            if invalid_material_textures:
                check_messages.append("TEXTURES")
                check_icons.append('SEQUENCE_COLOR_02')
            
            #--------------_OLD CHECK-----------------------------
            if search_for_old_objects(objects_to_check):
                check_messages.append("_OLD")
                check_icons.append('CANCEL')
                self.report({'ERROR'}, check_mode_name+ f" -_OLD ERROR!!!")
            
                
        
        
        # SHOW CHECK POPUP
        if not any('CANCEL' in icon for icon in check_icons):  
            self.show_popup(check_messages, check_icons,check_mode_name)
            self.report({'INFO'}, f"CHECKS OK")
       
        
        # Run FBX export window
        if not is_export_window_open():
            self.open_fbx_export_window()
        
        return {'FINISHED'}
    
    # Get mode name for Check title
    def get_mode_for_title(self):
            
            active_export_mode = bpy.context.scene.other_properties.export_mode_enum
            
            match active_export_mode:
                case "OP1":
                    return "FINAL"
                case "OP2":
                    return "PROTOTYPE"
                case "OP3":
                    return "DESIGN"
                case default:
                    return ""
    
    # Run window with last export settings
    def open_fbx_export_window(self):
        wm = bpy.context.window_manager
        last_fbx_settings = wm.operator_properties_last("export_scene.fbx")

        if last_fbx_settings:
            export_args = {}
            for prop in last_fbx_settings.bl_rna.properties:
                if not prop.is_readonly and prop.identifier != "rna_type":
                    export_args[prop.identifier] = getattr(last_fbx_settings, prop.identifier)

            # Open the export window with stored settings
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT', **export_args)
        
        else:
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
    
    def show_popup(self, check_messages,check_icons, mode_name):
        """Show a pop-up message in Blender UI"""
            
        def draw(self, context):
            
            default_icon = 'INFO'  # Use a safe default
            
            for index, message in enumerate(check_messages):
                icon = check_icons[index] if index < len(check_icons) else default_icon
                self.layout.label(text=message, icon=icon)
                
        header_title = "Checks: " + mode_name
                
        bpy.context.window_manager.popup_menu(draw, title = header_title)
     

# Returns True if the FBX export window is open
def is_export_window_open():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'FILE_BROWSER':  # Export window is a file browser
                return True
    return False

# Modify the existing Export menu to include BBG operator
def menu_func_export(self, context):
    self.layout.operator(ExportFBXWithChecks.bl_idname, text="FBX BBG")

def ExportWithChecksRegister():
    bpy.utils.register_class(ExportFBXWithChecks)
    bpy.utils.register_class(ExportChecksWindowPanel)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    
def ExportWithChecksUnregister():
    bpy.utils.unregister_class(ExportFBXWithChecks)
    bpy.utils.unregister_class(ExportChecksWindowPanel)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

#---------------------------------------------------
# /Export Check (Custom Export)
#---------------------------------------------------


#---------------------------------------------------
# Scale Checks
#---------------------------------------------------
class CheckScalesOperator(ObjectModeOnlyOperator):
    """Checks scales of visible or selected objects (selects anomalies)"""
    bl_idname = "object.check_scales"
    bl_label = "Check Scales"
    
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        collection_name = "Export"
        objects, error = get_objects_recursive(False, False)

        if error:
            self.report({'ERROR'}, error)
            return {'CANCELLED'}


        if objects:
            self.report({'WARNING'}, f"Objects with scale errors:\n" + "\n".join(objects))
            self.show_popup(f"Object scale error. SEE CONSOLE", icon='ERROR')
        else:
            self.report({'INFO'}, "SCALES OK")
            self.show_popup("SCALES OK!", icon='CHECKMARK')

        return {'FINISHED'}
    
    def show_popup(self, message, icon='INFO'):
        """Show a pop-up message in Blender UI"""
        def draw(self, context):
            self.layout.label(text=message, icon=icon)
        bpy.context.window_manager.popup_menu(draw, title="Check", icon=icon)
            

def get_objects_recursive(export_bool, select_bool):
    """Returns a list of object names that don't have scale (1,1,1)"""
    objects_with_non_default_scales = []
    checked_objects = set()

    def check_object_scale(obj):
        """Recursively check an object's scale and its children"""
        if obj.name in checked_objects:
            return
        checked_objects.add(obj.name)

        effective_scale = obj.matrix_world.to_scale()
        if not (math.isclose(effective_scale.x, 1.0, rel_tol=1e-3) and
                math.isclose(effective_scale.y, 1.0, rel_tol=1e-3) and
                math.isclose(effective_scale.z, 1.0, rel_tol=1e-3)):
            objects_with_non_default_scales.append(obj.name)
            if not (export_bool):
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                
    if not select_bool:
        for obj in bpy.context.view_layer.objects:
            if obj.visible_get():  # Only check visible objects
                check_object_scale(obj)
    else:
        for obj in bpy.context.selected_objects:
            check_object_scale(obj)

    return objects_with_non_default_scales, None  # Return the list and no error

                
def ChecksRegister():
    bpy.utils.register_class(CheckScalesOperator)
    bpy.utils.register_class(CheckPanel)
    bpy.types.Scene.other_props = bpy.props.PointerProperty(type=OtherProperties)
    
def ChecksUnregister():
    bpy.utils.unregister_class(CheckScalesOperator)
    bpy.utils.unregister_class(CheckPanel)
    del bpy.types.Scene.other_props

#---------------------------------------------------
# /Scale Checks
#---------------------------------------------------



#---------------------------------------------------
# COL Check
#---------------------------------------------------
# only for export check

def check_has_col(objects_to_check):
    has_col = any("COL" in obj.name for obj in objects_to_check)
    
    return has_col

#---------------------------------------------------
# /COL Checks
#---------------------------------------------------



#---------------------------------------------------
# Format Check
#---------------------------------------------------

# Mark invalid if contains PROTOTYPE in final mode or doesn not follow naming conventions
def check_material_format(objects_to_check):
    
    # Get mode options
    active_export_mode = bpy.context.scene.other_properties.export_mode_enum

    
    invalid_materials = set()
    
    # Get mode
    if active_export_mode == 'OP1':
            pattern = re.compile(r'^(?!.*_PROTOTYPE)[A-Z]+_[^_]+_[^_]+$')      
    else:
        pattern = re.compile(r'^(?:[A-Z][^_]*_PROTOTYPE|(?!.*PROTOTYPE)[A-Z]+_[^_]+_[^_]+)$')
    
    for obj in objects_to_check:
        if obj.material_slots:
            for slot in obj.material_slots:
                if slot.material:
                    name = slot.material.name
                    if not pattern.match(name) or "COL" in name:
                        invalid_materials.add(name)
    
    return invalid_materials

# If the texture's basename does not match the material name, mark it as invalid.
def check_albedo_texture_format(objects_to_check):
    
    # Get mode options
    active_export_mode = bpy.context.scene.other_properties.export_mode_enum
    
    invalid_materials = set()
    
    for obj in objects_to_check:
        if not obj.data or not hasattr(obj.data, "materials"):
            continue

        for mat in obj.data.materials:
            if not mat or not mat.node_tree:
                continue

            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    texture_name = node.image.name
                    # Remove the file extension
                    texture_basename, _ = os.path.splitext(texture_name)
                    
                    mat_name = mat.name
                    
                    if active_export_mode == 'OP1':
                        mat_name = mat.name + "_A"
                        
                    if texture_basename != mat_name:
                        invalid_materials.add(mat.name)

    return invalid_materials


class FormatCheck(ObjectModeOnlyOperator):
    """Check material name format for all visible or selected objects"""
    bl_idname = "wm.format_check"
    bl_label = "Check Material Format"

    def execute(self, context):
        objects_to_check = []
        
        
        
        if len(context.selected_objects) > 1:
            objects_to_check = context.selected_objects
        elif len(context.selected_objects) == 1:
            objects_to_check = [context.selected_objects[0]]
        else:
            objects_to_check = [obj for obj in context.visible_objects if obj.type == 'MESH']
        
        invalid_materials = check_material_format(objects_to_check)
        
        
        
        if invalid_materials:
            self.report({'WARNING'}, f"Invalid material names:\n" + "\n".join(invalid_materials))
            self.show_popup("Invalid material names detected. SEE CONSOLE", icon='ERROR')
        else:
            self.report({'INFO'}, "MATERIAL NAMES OK")
            self.show_popup("MATERIAL NAMES OK!", icon='CHECKMARK')
        
        return {'FINISHED'}
    
    def show_popup(self, message, icon='INFO'):
        def draw(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(draw, title="Format Check", icon=icon)
      
        
class TextureFormatCheck(ObjectModeOnlyOperator):
    """Check materials texture name for all visible or selected objects"""
    bl_idname = "wm.texture_format_check"
    bl_label = "Check Materials Texture Format"

    def execute(self, context):
        objects_to_check = []      
        
        if len(context.selected_objects) > 1:
            objects_to_check = context.selected_objects
        elif len(context.selected_objects) == 1:
            objects_to_check = [context.selected_objects[0]]
        else:
            objects_to_check = [obj for obj in context.visible_objects if obj.type == 'MESH']
        
        invalid_materials = check_albedo_texture_format(objects_to_check)
        
        
        
        if invalid_materials:
            self.report({'WARNING'}, f"Materials with invalid texture:\n" + "\n".join(invalid_materials))
            self.show_popup("Invalid textures detected. SEE CONSOLE", icon='ERROR')
        else:
            self.report({'INFO'}, "TEXTURE NAMES OK")
            self.show_popup("TEXTURE NAMES OK!", icon='CHECKMARK')
        
        return {'FINISHED'}
    
    def show_popup(self, message, icon='INFO'):
        def draw(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(draw, title="Format Check", icon=icon)


def FormatCheckRegister():
    bpy.utils.register_class(FormatCheck)
    bpy.utils.register_class(TextureFormatCheck)


def FormatCheckUnregister():
    bpy.utils.unregister_class(FormatCheck)
    bpy.utils.unregister_class(TextureFormatCheck)


#---------------------------------------------------
# /Format Check
#---------------------------------------------------


#---------------------------------------------------
# Normals Check
#---------------------------------------------------
# NOT WORKING!

class CheckNormalsOperator(bpy.types.Operator):
    """Check if selected objects have normal issues"""
    bl_idname = "object.check_normals"
    bl_label = "Check Normals"

    def execute(self, context):
        self.show_popup("IN DEVELOPMENT", icon = 'ERROR')
        return {'FINISHED'}

    def show_popup(self, message, icon='INFO'):
        """Show a pop-up message in Blender UI"""
        def draw(self, context):
            self.layout.label(text=message, icon=icon)
        bpy.context.window_manager.popup_menu(draw, title="Normal Check", icon=icon)

def NormalsRegister():
    bpy.utils.register_class(CheckNormalsOperator)

def NormalsUnregister():
    bpy.utils.unregister_class(CheckNormalsOperator)

#---------------------------------------------------
# /Normals Check
#---------------------------------------------------

#---------------------------------------------------
# Root Check
#---------------------------------------------------

class OtherProperties(bpy.types.PropertyGroup):
    #keep for now, dispose of later
    include_prototype_root: bpy.props.BoolProperty(
        name="Enable Prototype Check",
        default=True
    )
    export_mode_enum: bpy.props.EnumProperty(
        name="",
        description="Select Export Mode",
        items=[
        ('OP1', "FINAL", ""),
        ('OP2', "PROTOTYPE", ""),
        ('OP3', "DESIGN", "")
        ]
    )
    custom_collider_name: bpy.props.StringProperty(
        name = "",
        description = "Collider material name",
        default = "COL_DEFAULT"
    )
    show_collapse: bpy.props.BoolProperty(
        name="Show Options",
        default=False
    )

def object_root_check():
    """Check if all selected or visible objects share the same top-level parent."""
    
    active_export_mode = bpy.context.scene.other_properties.export_mode_enum
    
    include_prototype_root = False
    
    if active_export_mode == 'OP2':
        include_prototype_root = True
    
    def get_top_parent(obj):
        """Recursively find the highest parent in the hierarchy."""
        while obj.parent:
            obj = obj.parent
        return obj
    
    # Only if in PROTOTYPE mode
    def make_extra_root_check(obj):
        root_obj = obj
        
        if (root_obj.location == mathutils.Vector((0.0, 0.0, 0.0)) and
            root_obj.rotation_euler == mathutils.Euler((0.0, 0.0, 0.0))):
            return True

        return False
    
    # Determine which objects to check
    selected_objects = bpy.context.selected_objects
    objects_to_check = selected_objects if len(selected_objects) > 1 else [obj for obj in bpy.context.view_layer.objects if obj.visible_get()]
    
    if not objects_to_check:
        return True  # No objects to check, assume valid
    
    # Get the top-most parent of the first object
    top_parent = get_top_parent(objects_to_check[0])

    # Ensure all other objects share the same top-level parent
    for obj in objects_to_check:
        if get_top_parent(obj) != top_parent:
            return False  # Found an object with a different root parent
    
    # If PROTOTYPE mode is checked in panel, execute
    if include_prototype_root:    
        if not make_extra_root_check(top_parent):
            return False
    
    return True  # All objects share the same top-level parent


def RootCheckRegister():
    
    bpy.utils.register_class(OtherProperties)
    bpy.types.Scene.other_properties = bpy.props.PointerProperty(type=OtherProperties)

def RootCheckUnregister():

    del bpy.types.Scene.other_properties
    bpy.utils.unregister_class(OtherProperties)

#---------------------------------------------------
# /Root Check
#---------------------------------------------------


#---------------------------------------------------
# UVMapsRename
#---------------------------------------------------
#Renames UV Maps of the currently selected objects

class UVMapsRenamePanel(bpy.types.Panel):
    bl_label = "UV Maps Rename"
    #bl_idname = "uv_maps_rename"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "data"
    bl_category = 'BBG'
    bl_options = {"DEFAULT_CLOSED"}
    
        
    def draw(self, context):
        layout = self.layout
        ui = layout.column_flow(columns=2, align=False)
        ui.prop(context.scene, "UVMaps_new_name", text="")
        ui.operator("wm.uv_maps_rename", text="UV Maps Rename")


class UVMapsRename(bpy.types.Operator):
    bl_label = "UV Maps Rename"
    bl_idname = "wm.uv_maps_rename"
    #bl_idname = "object.uv_maps_rename"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "data"
    bl_options = {'REGISTER', 'UNDO'}
    bl_category = 'BBG'
    
    
    def execute(self, context):
        newName = context.scene.UVMaps_new_name
        for obj in bpy.context.selected_objects:
            if hasattr(obj, "data"):
                if hasattr(obj.data, "uv_layers"):
                    for uvmap in obj.data.uv_layers:
                        uvmap.name = newName
        return {'FINISHED'}


def UVMapsRenameRegister():
    bpy.utils.register_class(UVMapsRenamePanel)
    bpy.utils.register_class(UVMapsRename)

    bpy.types.Scene.UVMaps_new_name = bpy.props.StringProperty \
    (
        name = "UVMaps_new_name",
        description = "",
        default = "UVMap"
    )

def UVMapsRenameUnregister():
    bpy.utils.unregister_class(UVMapsRenamePanel)
    bpy.utils.unregister_class(UVMapsRename)

    del bpy.types.Scene.UVMaps_new_name

#---------------------------------------------------
# /UVMapsRename
#---------------------------------------------------

#---------------------------------------------------
# Animations
#---------------------------------------------------

class AnimationsPanel(bpy.types.Panel):
    bl_label = "Animations"
    bl_idname = "panel_animations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BBG'
    bl_options = {"DEFAULT_CLOSED"}
    
    
    def draw(self, context):
        
        # Static animations
        box2 = self.layout.box()
        staticrow = box2.row().split(factor = 0.6, align=True)
        
        #label
        staticrow.label(text="Static Animation")
        # mark button
        staticrow.operator("wm.mark_static_ani", text="", icon='BOOKMARKS')
        # select button
        staticrow.operator("wm.select_static_ani", text="", icon='RESTRICT_SELECT_OFF')
        
        # Merge animations
        box = self.layout.box()
        box.label(text="MERGE ANIMATIONS")
        box.prop(context.scene, "target", text="Target")
        box.prop(context.scene, "animations", text="Animations")
        box.operator("wm.merge_animations", text="Move Animations to Target")
        
#---------------------------------------------------
# /Animations
#---------------------------------------------------

#---------------------------------------------------
# MergeAnimations
#---------------------------------------------------
#Moves animation_data.action from Animations to Target with the same name, ignoring the .00x suffix. 
#must import re


class MergeAnimations(bpy.types.Operator):
    """Move Animations to Target"""
    bl_label = "Merge Animations"
    bl_idname = "wm.merge_animations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "object"
    bl_category = 'BBG'
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        targetsParent = context.scene.target
        animationsParent = context.scene.animations

        isNone = False
        if targetsParent is None:
            print("Target is None. ")
            isNone = True
        if animationsParent is None:
            print("Animations is None. ")
            isNone = True
        if isNone:            
            return {'FINISHED'}
        
        context.scene.animations = None

        targets = [targetsParent]
        stack = [targetsParent]
        while stack:
            current = stack.pop()
            targets.append(current)
            for child in current.children:
                stack.append(child)

        animations = [animationsParent]
        stack = [animationsParent]
        while stack:
            current = stack.pop()
            animations.append(current)
            for child in current.children:
                stack.append(child)

        rex = r"\.\d+$"
        for ani in animations:
            if ani.animation_data is not None:
                found = False

                aniName = ani.name
                if len(aniName) > 4:
                    if re.match(rex, aniName[-4:]):
                        aniName = aniName[:-4]

                for tar in targets:
                    tarName = tar.name
                    if len(tarName) > 4:
                        if re.match(rex, tarName[-4:]):
                            tarName = tarName[:-4]

                    if aniName == tarName:
                        found = True
                        tar.animation_data_create()
                        tar.animation_data.action = ani.animation_data.action
                        break
                
                if found:
                    continue
                else:
                    print("Merge Animations: Object with animation \"" + aniName + "\" has no match in objects without animation. ")


        bpy.ops.object.select_all(action='DESELECT')
        for ani in animations:
            ani.select_set(True)
        bpy.ops.object.delete(use_global=False, confirm=False)

        return {'FINISHED'}

#---------------------------------------------------
# /MergeAnimations
#---------------------------------------------------


#---------------------------------------------------
# StaticAnimations
#---------------------------------------------------

class MarkStaticAnimations(bpy.types.Operator):
    """Mark selected animated objects as static"""
    bl_label = "Mark Static"
    bl_idname = "wm.mark_static_ani"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BBG'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        # Amount of shift at frame 0
        shift_amount = 0.00001

        # Iterate over all selected objects in the scene
        for obj in context.selected_objects:
            if obj.animation_data and obj.animation_data.action:
                static = True 
                
                for fcurve in obj.animation_data.action.fcurves:
                    if fcurve.data_path not in {"location", "rotation_euler"}:
                        continue

                    key_val_at_zero = None
                    key_val_at_one = None
                    key_val_at_end = None
                    key_val_at_endplus = None
                    
                    frames = sorted(kp.co.x for kp in fcurve.keyframe_points)

                    if len(frames) >= 2:
                        end_frame = frames[-1]     
                        endplus_frame = frames[-2]
                    else:
                        end_frame = None
                        endplus_frame = None

                    for kp in fcurve.keyframe_points:
                        frame = kp.co.x
                        if abs(frame - 0) < 1e-4:
                            key_val_at_zero = kp.co.y
                            
                        elif abs(frame - 1) < 1e-4:
                            key_val_at_one = kp.co.y
                            
                        elif end_frame is not None and abs(frame - end_frame) < 1e-4:
                            key_val_at_end = kp.co.y
                            
                        elif endplus_frame is not None and abs(frame - endplus_frame) < 1e-4:
                            key_val_at_endplus = kp.co.y
                            

                    # If keyframe is missing or the values differ mark as non-static.
                    if key_val_at_zero is None or key_val_at_one is None or key_val_at_end is None or key_val_at_endplus is None:
                        
                        static = False
                        break
                    
                    if abs(key_val_at_zero - key_val_at_one) > 1e-4:
                        
                        static = False
                        break
                    
                    if abs(key_val_at_end - key_val_at_endplus) > 1e-4:
                        
                        static = False
                        break

                # Mark static all valid by shifting (shift is based on orig keyframe locrots)
                if static:
                    # Get location & rotation at frame 1
                    obj.location = obj.animation_data.action.fcurves[0].evaluate(1), \
                                   obj.animation_data.action.fcurves[1].evaluate(1), \
                                   obj.animation_data.action.fcurves[2].evaluate(1)

                    obj.rotation_euler = obj.animation_data.action.fcurves[3].evaluate(1), \
                                         obj.animation_data.action.fcurves[4].evaluate(1), \
                                         obj.animation_data.action.fcurves[5].evaluate(1)

                    # Apply shift
                    obj.location = (obj.location[0] + shift_amount, obj.location[1] + shift_amount, obj.location[2] + shift_amount)
                    obj.rotation_euler = (obj.rotation_euler[0] + shift_amount, obj.rotation_euler[1] + shift_amount, obj.rotation_euler[2] + shift_amount)

                    # Insert modified keyframe at frame 0
                    obj.keyframe_insert(data_path="location", frame=0)
                    obj.keyframe_insert(data_path="rotation_euler", frame=0)

                    # Get location & rotation at endplus_frame
                    obj.location = obj.animation_data.action.fcurves[0].evaluate(endplus_frame), \
                                   obj.animation_data.action.fcurves[1].evaluate(endplus_frame), \
                                   obj.animation_data.action.fcurves[2].evaluate(endplus_frame)

                    obj.rotation_euler = obj.animation_data.action.fcurves[3].evaluate(endplus_frame), \
                                         obj.animation_data.action.fcurves[4].evaluate(endplus_frame), \
                                         obj.animation_data.action.fcurves[5].evaluate(endplus_frame)

                    # Apply shift
                    obj.location = (obj.location[0] + shift_amount, obj.location[1] + shift_amount, obj.location[2] + shift_amount)
                    obj.rotation_euler = (obj.rotation_euler[0] + shift_amount, obj.rotation_euler[1] + shift_amount, obj.rotation_euler[2] + shift_amount)

                    # Insert modified keyframe at end_frame
                    obj.keyframe_insert(data_path="location", frame=end_frame)
                    obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)
                  
        self.report({'INFO'}, f"OBJECTS MARKED")
                    
        return {'FINISHED'}

class SelectStaticAnimations(bpy.types.Operator):
    """Select all animated objects marked as static"""
    bl_label = "Select Static"
    bl_idname = "wm.select_static_ani"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BBG'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        shift_amount = 0.00001
        tol = 1e-7  # Tolerance for float
        
        bpy.ops.object.select_all(action='DESELECT')
        
        for obj in context.scene.objects:
            if obj.type != 'EMPTY':
                continue
            
            if not (obj.animation_data and obj.animation_data.action):
                continue
            
            action = obj.animation_data.action
            valid = True
            

            for data_path in ("location", "rotation_euler"):
                
                for axis in range(3):
                    fcurve = next((fc for fc in action.fcurves 
                                   if fc.data_path == data_path and fc.array_index == axis), None)
                    
                    if fcurve is None:
                        valid = False
                        break
                    
                    # Get values at 0 and 1
                    key_val_at_zero = None
                    key_val_at_one = None
                    
                    for kp in fcurve.keyframe_points:
                        
                        if abs(kp.co.x - 0) < tol:
                            key_val_at_zero = kp.co.y
                            
                        elif abs(kp.co.x - 1) < tol:
                            key_val_at_one = kp.co.y
                            
                    if key_val_at_zero is None or key_val_at_one is None:
                        valid = False
                        break  
                    
                    # Calculate the difference
                    diff = key_val_at_one - key_val_at_zero
                    
                    if(diff<0):
                        diff = diff * -1
                        
                    if abs(diff - shift_amount) > tol:
                        valid = False
                        break
                
                if not valid:
                    break
            
            # If all channels pass the check, select the object
            if valid:
                obj.select_set(True)
            else:
                obj.select_set(False)
        
        self.report({'INFO'}, f"STATIC OBJECTS SELECTED")
                
        return {'FINISHED'}

#---------------------------------------------------
# /StaticAnimations
#---------------------------------------------------



#---------------------------------------------------
# ANI regiseter
#---------------------------------------------------

def MergeAnimationsRegister():
    bpy.utils.register_class(AnimationsPanel)
    bpy.utils.register_class(MergeAnimations)
    bpy.utils.register_class(MarkStaticAnimations)
    bpy.utils.register_class(SelectStaticAnimations)

    bpy.types.Scene.target = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.animations = bpy.props.PointerProperty(type=bpy.types.Object)

def MergeAnimationsUnregister():
    bpy.utils.unregister_class(AnimationsPanel)
    bpy.utils.unregister_class(MergeAnimations)
    bpy.utils.unregister_class(MarkStaticAnimations)
    bpy.utils.unregister_class(SelectStaticAnimations)

    del bpy.types.Scene.target
    del bpy.types.Scene.animations
    
#---------------------------------------------------
# /ANI regiseter
#---------------------------------------------------



#---------------------------------------------------
# CleanMaterials
#---------------------------------------------------
#On all objects, cleans materials with the same name. Remove Collider Tools material
#must import re

class CleanMaterials(ObjectModeOnlyOperator):
    """Remove all material duplicates and COL materials in Scene"""
    bl_label = "Clean Materials"
    bl_idname = "wm.clean_materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "material"
    bl_category = 'BBG'
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        replaced_count = 0

        include_name_MATERIAL = context.scene.include_name_MATERIAL
        
        ColliderMaterial_name = bpy.context.scene.other_properties.custom_collider_name
        
        MATERIAL_name = "Material"
        
        allMaterials = {}
        rex = r"\.\d+$"
        cleanMaterials = []
        dirtyMaterials = []

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material:
                        if slot.material.name == ColliderMaterial_name:
                            obj.data.materials.clear()
                        else:
                            if slot.material not in allMaterials:
                                allMaterials[slot.material] = []
                            allMaterials[slot.material].append(obj)

        for mat, objects in allMaterials.items():
            if len(mat.name) > 4:
                if re.match(rex, mat.name[-4:]):
                    if include_name_MATERIAL:
                        dirtyMaterials.append(mat)
                    else:
                        if mat.name[:-4] == MATERIAL_name:
                            cleanMaterials.append(mat)
                        else:
                            dirtyMaterials.append(mat)
                else:
                    cleanMaterials.append(mat)
            else:
                cleanMaterials.append(mat)

        for dirtyMat in dirtyMaterials:
            found = False
            for cleanMat in cleanMaterials:
                if dirtyMat.name[:-4] == cleanMat.name:
                    found = True
                    break
            if not found:
                dirtyMat.name = dirtyMat.name[:-4]
                cleanMaterials.append(dirtyMat)
                
        for mat, objects in allMaterials.items():
            if mat not in cleanMaterials:
                for cleanMat in cleanMaterials:
                    if mat.name[:-4] == cleanMat.name:
                        for obj in objects:
                            for slot in obj.material_slots:
                                if slot.material == mat:
                                    slot.material = cleanMat
                        break

        for mat in bpy.data.materials:
            if mat not in cleanMaterials:
                bpy.data.materials.remove(mat)
                replaced_count += 1

        self.report({'INFO'}, f"{replaced_count} Materials Replaced")

        return {'FINISHED'}


def CleanMaterialsRegister():
    bpy.utils.register_class(CleanMaterials)

    bpy.types.Scene.include_name_MATERIAL = bpy.props.BoolProperty(name="include_name_MATERIAL", default=True)

def CleanMaterialsUnregister():
    bpy.utils.unregister_class(CleanMaterials)

    del bpy.types.Scene.include_name_MATERIAL

#---------------------------------------------------
# /CleanMaterials
#---------------------------------------------------


#---------------------------------------------------
# CleanTextures
#---------------------------------------------------
#On all objects, cleans materials with the same name. Remove Collider Tools material
#must import re

class CleanTextures(ObjectModeOnlyOperator):
    """Remove all material duplicates and COL materials in Scene"""
    bl_label = "Clean Textures"
    bl_idname = "wm.clean_textures"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_context = "material"
    bl_category = 'BBG'
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        replaced_count = 0

        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            
            if obj.data.materials:
                for mat in obj.data.materials:
                    if mat and mat.node_tree:
                        for node in mat.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image:
                                image = node.image
                                
                                # Check if name has a suffix (.001, .002, etc.)
                                match = re.match(r"(.+)\.\d{3}$", image.name)
                                if match:
                                    base_name = match.group(1)  # Extract base name

                                    # Check if a texture with the base name exists
                                    if base_name in bpy.data.images:
                                        node.image = bpy.data.images[base_name]  # Replace texture
                                        replaced_count += 1

        self.report({'INFO'}, f"{replaced_count} Textures Replaced")

        return {'FINISHED'}


def CleanTexturesRegister():
    bpy.utils.register_class(CleanTextures)

def CleanTexturesUnregister():
    bpy.utils.unregister_class(CleanTextures)

#---------------------------------------------------
# /CleanTextures
#---------------------------------------------------


#---------------------------------------------------
# LOD
#---------------------------------------------------
class LODObjectPickerPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "LOD Creator"
    bl_idname = "OBJECT_PT_add_lod_suffix"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BBG'
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # Object picker UI
        layout.prop(context.scene, "lod_target", text="Target")
        
        # Number of LODs input
        layout.prop(context.scene, "num_lods", text="Number of LODs")
        
        
        layout.prop(context.scene, "apply_decimate", text="Decimate")

        
        layout.prop(context.scene, "inverse_matrix", text="Inverse Matrix")


        # Button to run the operator to add LODs
        layout.operator("object.add_lod_suffix")

        # Button to remove objects with _OLD suffix
        layout.operator("object.remove_old_objects")

class AddLODSuffix(bpy.types.Operator):
    """Add _LODs to target object"""
    bl_idname = "object.add_lod_suffix"
    bl_label = "Add LODs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_object = context.scene.lod_target
        num_lods = context.scene.num_lods
        apply_decimate = context.scene.apply_decimate
        inverse_matrix = context.scene.inverse_matrix

        if not selected_object:
            self.report({'ERROR'}, "No object selected!")
            return {'CANCELLED'}
        
        if num_lods < 1:
            self.report({'ERROR'}, "Number of LODs must be at least 1!")
            return {'CANCELLED'}

        # Create an empty object with the same rotation and location as the original object
        def create_empty_for_object(obj):
            empty = bpy.data.objects.new(obj.name + "_LOD_Empty", None)  # Name with _LOD_Empty
            bpy.context.scene.cursor.location = obj.location
            empty.location = bpy.context.scene.cursor.location
            empty.rotation_euler = obj.rotation_euler
            empty.parent = obj.parent
            
            #wtf kdyz je to import tohle nesmi byt aktivni !!!
            if not inverse_matrix:
                if empty.parent:
                    empty.matrix_parent_inverse = empty.parent.matrix_world.inverted()
            
            bpy.context.collection.objects.link(empty)  # Link empty to the collection
            
            return empty

        # Transfer mesh data-block from _OLD object to _LOD0 object
        def transfer_mesh_data_block(original_obj, lod0_obj):
            lod0_obj.data = original_obj.data  # Directly reference the mesh data-block of the _OLD object
        
        # Set location and rotation of new LOD
        def set_lod_locpos(obj):
            obj.location = (0,0,0)
            obj.rotation_euler = (0,0,0)
        
        # Recursively add LOD suffix or duplicate meshes
        def add_suffix_to_mesh(obj):
            if obj.type == 'MESH' and '_COL_' not in obj.name:
                # Create an empty for the original object
                empty = create_empty_for_object(obj)

                # Rename original object if number of LODs is 1
                if num_lods == 1:
                    if not obj.name.endswith('_LOD0'):
                        obj.name = obj.name + '_LOD0'
                    obj.parent = empty
                    obj.matrix_parent_inverse = empty.matrix_world.inverted()
                    set_lod_locpos(obj)
                else:
                    # Duplicate object and rename with _LODx suffix
                    for i in range(num_lods):
                        new_obj = obj.copy()
                        new_obj.data = obj.data.copy()  # Duplicate mesh data for LODs
                        new_obj.name = obj.name + f'_LOD{i}'
                        bpy.context.collection.objects.link(new_obj)  # Link the new object to the same collection
                        # Parent LOD duplicates to the empty with "Keep Transform"
                        new_obj.parent = empty
                        new_obj.matrix_parent_inverse = empty.matrix_world.inverted()
                        set_lod_locpos(new_obj)
                        
                        # Apply Decimate modifier based on LOD level if checkbox is checked
                        if apply_decimate and '_LOD' in new_obj.name:
                            if i == 1:
                                decimate_modifier = new_obj.modifiers.new(name="Decimate", type='DECIMATE')
                                decimate_modifier.ratio = 0.7  # 0.7 for LOD1
                            elif i > 1:
                                decimate_modifier = new_obj.modifiers.new(name="Decimate", type='DECIMATE')
                                decimate_modifier.ratio = 0.4  # 0.4 for LOD2 and beyond

                        # If it's LOD0, transfer the original mesh data-block from _OLD object
                        if i == 0:
                            transfer_mesh_data_block(obj, new_obj)

                # Add _OLD suffix to the original object
                if not obj.name.endswith('_OLD') and not num_lods == 1:
                    obj.name = obj.name + '_OLD'

                # Remove _LOD_Empty suffix from the empty
                if empty.name.endswith('_LOD_Empty'):
                    empty.name = empty.name[:-len('_LOD_Empty')]

            # Recursively apply to children
            for child in obj.children:
                add_suffix_to_mesh(child)

        add_suffix_to_mesh(selected_object)

        return {'FINISHED'}

class RemoveOldObjects(bpy.types.Operator):
    """Remove all objects with _OLD suffix under Target"""
    bl_idname = "object.remove_old_objects"
    bl_label = "Remove _OLD"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_object = context.scene.lod_target
        
        if not selected_object:
            self.report({'ERROR'}, "No object selected!")
            return {'CANCELLED'}

        # Collect objects to delete
        def collect_old_objects(obj):
            objects_to_delete = []
            if obj.name.endswith('_OLD'):
                objects_to_delete.append(obj)
            for child in obj.children:
                objects_to_delete.extend(collect_old_objects(child))
            return objects_to_delete

        objects_to_delete = collect_old_objects(selected_object)

        # Delete objects
        for obj in objects_to_delete:
            bpy.data.objects.remove(obj)

        self.report({'INFO'}, f"Removed {len(objects_to_delete)} objects with _OLD suffix.")
        return {'FINISHED'}
    
    
def search_for_old_objects(objects_to_check):
    invalid_objects = []
    
    for obj in objects_to_check:
        if obj.name.endswith('_OLD'):
            invalid_objects.append(obj)
            
    return invalid_objects


def LodRegister():
    bpy.utils.register_class(AddLODSuffix)
    bpy.utils.register_class(RemoveOldObjects)
    bpy.utils.register_class(LODObjectPickerPanel)
    bpy.types.Scene.lod_target = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.num_lods = bpy.props.IntProperty(name="Number of LODs", default=2, min=1)
    bpy.types.Scene.apply_decimate = bpy.props.BoolProperty(name="Decimate", default=False)
    bpy.types.Scene.inverse_matrix = bpy.props.BoolProperty(name="", default=False)

def LodUnregister():
    bpy.utils.unregister_class(AddLODSuffix)
    bpy.utils.unregister_class(RemoveOldObjects)
    bpy.utils.unregister_class(LODObjectPickerPanel)
    del bpy.types.Scene.lod_target
    del bpy.types.Scene.num_lods
    del bpy.types.Scene.apply_decimate
    del bpy.types.Scene.inverse_matrix

#---------------------------------------------------
# /LOD
#---------------------------------------------------


#---------------------------------------------------
# LOD Groups
#---------------------------------------------------

class LODGroupsPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "LOD Groups"
    bl_idname = "lod_groups_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BBG'
    bl_options = {"DEFAULT_CLOSED"}
    
    
    
    def draw(self, context):
        
        layout = self.layout
        
        groupBox = layout.box()
        
        
        
        lod0Split = groupBox.row().split(factor = 0.3, align=True)
        lod1Split = groupBox.row().split(factor = 0.3, align=True)
        lod2Split = groupBox.row().split(factor = 0.3, align=True)
        lod3Split = groupBox.row().split(factor = 0.3, align=True)
        
        # --------------------LOD0--------------------------------
        lod0Split.label(text="LOD0")
        lod0_visible = any(obj for obj in bpy.data.objects if "_LOD0" in obj.name and not obj.hide_get())

        # visible button
        lod0_visible_operator = lod0Split.operator("object.lod_groups_toggle_visibility", text="", icon='HIDE_OFF' if lod0_visible else 'HIDE_ON')
        lod0_visible_operator.lodGroup = "_LOD0"
            
        # select button
        lod0_select_operator = lod0Split.operator("object.lod_groups_select", text="", icon='RESTRICT_SELECT_OFF')
        lod0_select_operator.lodGroup = "_LOD0"
        
        # --------------------LOD1--------------------------------
        lod1Split.label(text= "LOD1")
        lod1_visible = any(obj for obj in bpy.data.objects if "_LOD1" in obj.name and not obj.hide_get())
        
        # visible button
        lod1_visible_operator = lod1Split.operator("object.lod_groups_toggle_visibility", text="", icon='HIDE_OFF' if lod1_visible else 'HIDE_ON')
        lod1_visible_operator.lodGroup = "_LOD1"
        
        # select button
        lod1_select_operator = lod1Split.operator("object.lod_groups_select", text="", icon='RESTRICT_SELECT_OFF')
        lod1_select_operator.lodGroup = "_LOD1"
        
        # --------------------LOD2--------------------------------
        lod2Split.label(text= "LOD2")
        lod2_visible = any(obj for obj in bpy.data.objects if "_LOD2" in obj.name and not obj.hide_get())
        
        # visible button
        lod2_visible_operator = lod2Split.operator("object.lod_groups_toggle_visibility", text="", icon='HIDE_OFF' if lod2_visible else 'HIDE_ON')
        lod2_visible_operator.lodGroup = "_LOD2"
        
        # select button
        lod2_select_operator = lod2Split.operator("object.lod_groups_select", text="", icon='RESTRICT_SELECT_OFF')
        lod2_select_operator.lodGroup = "_LOD2"
        
        # --------------------LOD3--------------------------------
        lod3Split.label(text= "LOD3")
        lod3_visible = any(obj for obj in bpy.data.objects if "_LOD3" in obj.name and not obj.hide_get())
        
        # visible button
        lod3_visible_operator = lod3Split.operator("object.lod_groups_toggle_visibility", text="", icon='HIDE_OFF' if lod3_visible else 'HIDE_ON')
        lod3_visible_operator.lodGroup = "_LOD3"
        
        # select button
        lod3_select_operator = lod3Split.operator("object.lod_groups_select", text="", icon='RESTRICT_SELECT_OFF')
        lod3_select_operator.lodGroup = "_LOD3"
        
        groupBox.operator("object.unhide_lod_objects", text="RESET")
        
class LodSelectGroupOperator(bpy.types.Operator):
    """Select LOD Group"""
    bl_idname = "object.lod_groups_select"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    lodGroup: bpy.props.StringProperty(name="_LODX")
    
    def execute(self, context):
        
        target_lod = self.lodGroup.strip()
        
        lods = [obj for obj in bpy.data.objects if target_lod in obj.name]
        
        bpy.ops.object.select_all(action='DESELECT')

        lod_objects = lods

        for obj in lod_objects:
            obj.select_set(True)

        if lod_objects:
            bpy.context.view_layer.objects.active = lod_objects[-1]
        
        return {'FINISHED'}
    
    def selectLODs(self, lodsToSelect):
        
        bpy.ops.object.select_all(action='DESELECT')

        lod_objects = lodsToSelect

        for obj in lod_objects:
            obj.select_set(True)

        if lod_objects:
            bpy.context.view_layer.objects.active = lod_objects[-1]
            
class LodToggleVisibilityOperator(bpy.types.Operator):
    """Toggle visibility of LOD group"""
    bl_idname = "object.lod_groups_toggle_visibility"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    lodGroup: bpy.props.StringProperty(name="_LODX")

    def execute(self, context):
        # Ensure the search string is stripped of spaces
        target_name = self.lodGroup.strip()

        lods = [obj for obj in bpy.data.objects if target_name in obj.name]

        if not lods:
            return {'CANCELLED'}
        
        
        # Determine the current visibility state (check the first object's state)
        new_visibility = not lods[0].hide_get()

        # Toggle visibility for all matching objects
        for obj in lods:
            obj.hide_set(new_visibility)  # Hide/unhide in viewport

        return {'FINISHED'}
    
class UnhideLODObjectsOperator(bpy.types.Operator):
    """Unhide all LOD Objects"""
    bl_idname = "object.unhide_lod_objects"
    bl_label = "Unhide LOD Objects"
    
    def execute(self, context):
        # Loop through all objects in the scene
        for obj in bpy.context.scene.objects:
            if "_LOD" in obj.name and obj.hide_get():
                obj.hide_set(False)  # Unhide the object
        return {'FINISHED'}                    

def LODGroupsRegister():
    bpy.utils.register_class(LODGroupsPanel)
    bpy.utils.register_class(UnhideLODObjectsOperator)
    bpy.utils.register_class(LodSelectGroupOperator)
    bpy.utils.register_class(LodToggleVisibilityOperator)
    
def LODGroupsUnregister():
    bpy.utils.unregister_class(LODGroupsPanel)
    bpy.utils.unregister_class(UnhideLODObjectsOperator)
    bpy.utils.unregister_class(LodSelectGroupOperator)
    bpy.utils.unregister_class(LodToggleVisibilityOperator)
    

#---------------------------------------------------
# /LOD Groups
#---------------------------------------------------

#---------------------------------------------------
# OUTLINER
#---------------------------------------------------

class OutlinerDesignCollectionCreator(bpy.types.Operator):
    """Adds Collections for designers"""
    bl_idname = "object.outliner_add_design"
    bl_label = "Add design collections"

    def execute(self, context):
        make_design_collections(self)
        
        return {'FINISHED'}

def make_design_collections(self):
    
    scene = bpy.context.scene

    # Create design collection
    design_collection = bpy.data.collections.new("Design")
    scene.collection.children.link(design_collection)
    
    # Create hands collection
    hands_collection = bpy.data.collections.new("Hands")
    scene.collection.children.link(hands_collection)
    
    # Create enviro collection
    enviro_collection = bpy.data.collections.new("Enviro")
    scene.collection.children.link(enviro_collection)

    # Create pr,pa,un
    pr = bpy.data.collections.new("PR")
    pa = bpy.data.collections.new("PA")
    un = bpy.data.collections.new("UN")

    # Link subcollections to the main collection
    design_collection.children.link(pr)
    design_collection.children.link(pa)
    design_collection.children.link(un)
        
    self.report({'INFO'}, "Collections created")


# Right-click menu
def add_design_option_to_outliner_menu(self, context):
    self.layout.separator()
    self.layout.operator(OutlinerDesignCollectionCreator.bl_idname, icon='PLUS')

def AddCollectionsRegister():
    bpy.utils.register_class(OutlinerDesignCollectionCreator)
    bpy.types.OUTLINER_MT_context_menu.append(add_design_option_to_outliner_menu)
    bpy.types.OUTLINER_MT_collection.append(add_design_option_to_outliner_menu)

def AddCollectionsUnregister():
    bpy.utils.unregister_class(OutlinerDesignCollectionCreator)
    bpy.types.OUTLINER_MT_context_menu.remove(add_design_option_to_outliner_menu)
    bpy.types.OUTLINER_MT_collection.remove(add_design_option_to_outliner_menu)

#---------------------------------------------------
# /OUTLINER
#---------------------------------------------------

#---------------------------------------------------
# MATERIAL SELECTOR
#---------------------------------------------------

class SelectActiveMaterialInScene(ObjectModeOnlyOperator):
    bl_idname = "wm.select_material_in_scene"
    bl_label = "Select Material"
    bl_description = "Select all objects with this material in the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        mat = context.object.active_material
        
        if mat:
            select_objects_with_same_material(context.visible_objects, mat)
        else:
            self.report({'WARNING'}, "No active material!")
            
        return {'FINISHED'}

def select_objects_with_same_material(objects_to_check, material_to_check):
    """Select all objects in the scene that use the active material slot's material."""
    
    active_material = material_to_check

    bpy.ops.object.select_all(action='DESELECT')

    for check_obj in objects_to_check:
        if check_obj.type == 'MESH':  
            for slot in check_obj.material_slots:
                if slot.material == active_material:
                    check_obj.select_set(True)
                    break  # No need to check further slots

def add_select_material_button(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator("wm.select_material_in_scene", icon="LOOP_BACK")

def SelectActiveMaterialInSceneRegister():
    bpy.utils.register_class(SelectActiveMaterialInScene)
    bpy.types.MATERIAL_MT_context_menu.append(add_select_material_button)

def SelectActiveMaterialInSceneUnregister():
    bpy.types.MATERIAL_MT_context_menu.remove(add_select_material_button)
    bpy.utils.unregister_class(SelectActiveMaterialInScene)

#---------------------------------------------------
# /MATERIAL SELECTOR
#---------------------------------------------------

def register():
    AddCollectionsRegister()
    RootCheckRegister()
    ExportWithChecksRegister()
    GuidelinesRegister()
    ChecksRegister() 
    FormatCheckRegister()
    NormalsRegister()
    UVMapsRenameRegister()
    MergeAnimationsRegister()
    CleanMaterialsRegister()
    CleanTexturesRegister()
    LodRegister()
    LODGroupsRegister()
    SelectActiveMaterialInSceneRegister()
    
    

def unregister():
    AddCollectionsUnregister()
    RootCheckUnregister()
    ExportWithChecksUnregister()
    GuidelinesUnregister()
    ChecksUnregister()
    FormatCheckUnregister()
    NormalsUnregister()
    UVMapsRenameUnregister()
    MergeAnimationsUnregister()
    CleanMaterialsUnregister()
    CleanTexturesUnregister()
    LodUnregister()
    LODGroupsUnregister()
    SelectActiveMaterialInSceneUnregister()
    

# TURN ON IF TESTING IN BLENDER 
#if __name__ == "__main__":
#    register()
