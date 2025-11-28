import os
import bpy
from bpy.types import Panel


class ACRI_PT_panel(Panel):
    bl_label = "AC Replay Importer 0.3.0"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"
    bl_context = "objectmode"
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        props = scn.acreplay_importer_props
        acrcsv_filepath = props.acrcsv_filepath
        recording_interval = props.recording_interval
        
        row = layout.row()
        row.operator("scene.acreplay_import_csv", text="Import .csv", icon="FILE")

        if acrcsv_filepath:
            row = layout.row()
            layout.label(text=os.path.split(acrcsv_filepath)[1])
            if recording_interval != 0:
                layout.label(text=(f"Frame Rate: {str((1000.0 / recording_interval))}"))

        row = layout.row()
        layout.prop(props, "target_framerate")
        row = layout.row()
        layout.prop_search(props, "chassis_object", scn, "objects", icon="AUTO")
        layout.prop_search(props, "wheelfl_object", scn, "objects", icon="DISC")
        layout.prop_search(props, "wheelfr_object", scn, "objects", icon="DISC")
        layout.prop_search(props, "wheelrl_object", scn, "objects", icon="DISC")
        layout.prop_search(props, "wheelrr_object", scn, "objects", icon="DISC")
        layout.label(text="For static elements near the wheel that don't rotate (e.g., brake calipers):")
        layout.prop_search(props, "wheelstaticfl_object", scn, "objects")
        layout.prop_search(props, "wheelstaticfr_object", scn, "objects")
        layout.prop_search(props, "wheelstaticrl_object", scn, "objects")
        layout.prop_search(props, "wheelstaticrr_object", scn, "objects")

        if acrcsv_filepath:
            row = layout.row()
            row.operator("scene.acreplay_animate", text="Animate", icon="NONE")


classes = [ACRI_PT_panel]
register, unregister = bpy.utils.register_classes_factory(classes)
