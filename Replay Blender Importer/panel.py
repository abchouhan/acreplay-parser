import os
import bpy
from bpy.types import Panel
from math import ceil


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
        layout.prop(props, "start_frame")
        if acrcsv_filepath and recording_interval != 0:
            layout.label(text=(f"End Frame: {props.start_frame+ceil(props.target_framerate*props.num_frames*recording_interval/1000.0)-1}"))
        row = layout.row()
        layout.prop_search(props, "chassis_object", scn, "objects", icon="AUTO")
        layout.prop_search(props, "wheelfl_object", scn, "objects", icon="DISC")
        layout.prop_search(props, "wheelfr_object", scn, "objects", icon="DISC")
        layout.prop_search(props, "wheelrl_object", scn, "objects", icon="DISC")
        layout.prop_search(props, "wheelrr_object", scn, "objects", icon="DISC")
        layout.label(text="For objects that move with the wheel but don't rotate (e.g., brake calipers, suspension objects):")
        layout.prop_search(props, "wheelstaticfl_object", scn, "objects")
        layout.prop_search(props, "wheelstaticfr_object", scn, "objects")
        layout.prop_search(props, "wheelstaticrl_object", scn, "objects")
        layout.prop_search(props, "wheelstaticrr_object", scn, "objects")

        # If csv file selected and at least one object selected, show Animate button
        if acrcsv_filepath and (props.chassis_object is not None or \
            props.wheelfl_object is not None or props.wheelfr_object is not None or \
            props.wheelrl_object is not None or props.wheelrr_object is not None or \
            props.wheelstaticfl_object is not None or props.wheelstaticfr_object is not None or \
            props.wheelstaticrl_object is not None or props.wheelstaticrr_object is not None):
                row = layout.row()
                row.operator("scene.acreplay_animate", text="Animate", icon="NONE")


classes = [ACRI_PT_panel]
register, unregister = bpy.utils.register_classes_factory(classes)
