import bpy
from bpy.types import Menu
from . import pie_menus

addon_keymaps = []

# -------------------- ADDON PREFERENCES -----------------------------------

class BBGPieMenuPreferences(bpy.types.AddonPreferences):
    """Preferences Panel for Keybinding"""
    bl_idname = __name__.split(".")[0]

    keymap: bpy.props.StringProperty(
        name="Keymap",
        description="Shortcut key for Collider Pie Menu",
        default="Q"
    )

    ctrl: bpy.props.BoolProperty(name="Ctrl", default=False)
    shift: bpy.props.BoolProperty(name="Shift", default=True)
    alt: bpy.props.BoolProperty(name="Alt", default=False)

    def draw(self, context):
        box = self.layout.box()
        pieMenuRow = box.row().split(factor = 0.5, align=True)
        pieMenuRow2 = box.row().split(factor = 0.5, align=True)
        pieMenuRow.label(text="Pie Menu Keybinding")

        
        pieMenuRow.prop(self, "keymap", text="")

        pieMenuRow.operator("wm.remove_keymap", text="", icon='X')

        pieMenuRow2.label(text="")
        pieMenuRow2.prop(self, "ctrl")
        pieMenuRow2.prop(self, "shift")
        pieMenuRow2.prop(self, "alt")

        box.operator("wm.save_keymap", text="Save")


# ---------------------- KEYMAP HANDLERS -----------------------------------

class SaveKeymap(bpy.types.Operator):
    """Save the keymap setting"""
    bl_idname = "wm.save_keymap"
    bl_label = "Save Keymap"

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__name__.split(".")[0]].preferences
        wm = bpy.context.window_manager

        # Remove old keymaps before adding new one
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()

        # Add new keymap
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            prefs.keymap.upper(),  # Use user-defined key
            'PRESS',
            ctrl=prefs.ctrl,
            shift=prefs.shift,
            alt=prefs.alt
        )
        kmi.properties.name = "PieMenuBBGChecks"
        addon_keymaps.append((km, kmi))

        self.report({'INFO'}, f"Keybinding Saved: {prefs.keymap.upper()}")
        return {'FINISHED'}


class RemoveKeymap(bpy.types.Operator):
    """Remove the custom keymap"""
    bl_idname = "wm.remove_keymap"
    bl_label = "Remove Keymap"

    def execute(self, context):
        # Remove existing keymaps
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()

        self.report({'INFO'}, "Keybinding Disabled!")
        return {'FINISHED'}


classes = (
    BBGPieMenuPreferences,
    SaveKeymap,
    RemoveKeymap,
    pie_menus.PieMenuBBGChecks,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc is None:
        return  # Prevent crash in background mode

    try:
        addon_name = __name__.split(".")[0]
        prefs = bpy.context.preferences.addons[addon_name].preferences

        # Create keymap
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            prefs.keymap.upper(),
            'PRESS',
            ctrl=prefs.ctrl,
            shift=prefs.shift,
            alt=prefs.alt
        )
        kmi.properties.name = "PieMenuBBGChecks"
        addon_keymaps.append((km, kmi))

    except KeyError:
        print(f"Add-on '{addon_name}' not found in preferences. Keymap not registered.")

def unregister():
    """ Remove keymaps and unregister classes """
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

