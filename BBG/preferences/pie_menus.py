import bpy
from bpy.types import Menu


# ------------------------- CHECKS PIE MENU DRAW ------------------------------------

class PieMenuBBGChecks(Menu):
    bl_label = "Check Menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("object.check_scales", text="Scale Check", icon='ORIENTATION_LOCAL')
        pie.operator("wm.clean_materials", text="Clean Materials", icon= 'BRUSH_DATA')
        pie.operator("wm.format_check", text="Material Check", icon='MATERIAL')
        pie.operator("wm.texture_format_check", text="Texture Check", icon='TEXTURE')        
        