import bpy

bl_info = {"name": "Hand Drawn NPR", "category": "Render"}


class MainPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Hand Drawn NPR"
    bl_idname = "RENDER_PT_hand_drawn_main_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        self.layout.label(text="Lorem ipsum dolor sit amet...")


def register():
    bpy.utils.register_class(MainPanel)


def unregister():
    bpy.utils.unregister_class(MainPanel)


if __name__ == "__main__":
    register()
