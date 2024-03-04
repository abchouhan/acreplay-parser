import os
import bpy
from bpy.types import Panel


class ACRI_PT_panel(Panel):
    bl_label = "AC Replay Importer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        acrjson_filepath = scn.acrjson_filepath
        recording_interval = scn.recording_interval
        
        row = layout.row()
        row.operator("acri.import_acrjson", text="Import .json", icon='FILE')

        if acrjson_filepath:
            row = layout.row()
            layout.label(text=os.path.split(acrjson_filepath)[1])
            if recording_interval != 0:
                layout.label(text=('Frame Rate: ' + str((1000.0 / recording_interval))))

        row = layout.row()
        layout.prop(scn, "target_framerate")
        row = layout.row()
        layout.prop_search(scn, "chassis_object", scn, "objects", text="Chassis", icon='AUTO')
        layout.prop_search(scn, "wheelfl_object", scn, "objects", text="Wheel FL", icon='DISC')
        layout.prop_search(scn, "wheelfr_object", scn, "objects", text="Wheel FR", icon='DISC')
        layout.prop_search(scn, "wheelrl_object", scn, "objects", text="Wheel RL", icon='DISC')
        layout.prop_search(scn, "wheelrr_object", scn, "objects", text="Wheel RR", icon='DISC')

        if acrjson_filepath:
            row = layout.row()
            row.operator("acri.animate", text="Animate", icon='NONE')


classes = (ACRI_PT_panel,)
register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
