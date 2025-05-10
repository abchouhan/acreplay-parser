import json
from math import ceil
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

from . import acrp_import


class ACRI_OT_import_acrjson(Operator, ImportHelper):
    bl_idname = "scene.acreplay_import_json"
    bl_label = "Import .json"
    bl_description = "Import AC Replay animation data (*.json) that was outputted by AC Replay Parser"
    
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    def set_path(self, context, path):
        context.scene.acreplay_importer_props.acrjson_filepath = path

    def execute(self, context):
        self.set_path(context, self.filepath)

        try:
            with open(context.scene.acreplay_importer_props.acrjson_filepath, 'r') as f:
                first_three_lines = f.readline()+f.readline()+f.readline()[0:-2]+"}"
                data = json.loads(first_three_lines)
        except:
            self.set_path(context, "")
            self.report({'ERROR'}, "Invalid .json file!")
            return {'CANCELLED'}

        if "numFrames" not in data or "recordingInterval" not in data:
            self.set_path(context, "")
            self.report({'ERROR'}, "Invalid .json file!")
            return {'CANCELLED'}

        frames = data["numFrames"]
        hz = data["recordingInterval"]

        context.scene.acreplay_importer_props.num_frames = frames
        context.scene.acreplay_importer_props.recording_interval = hz

        return {'FINISHED'}

class ACRI_OT_animate(Operator):
    bl_idname = "scene.acreplay_animate"
    bl_label = "Animate"
    bl_description = "Apply animation data to selected objects"

    def execute(self, context):
        context.window.cursor_set("WAIT")

        props = context.scene.acreplay_importer_props
        with open(props.acrjson_filepath, 'r') as f:
            data = json.loads(f.read())
        status = acrp_import.animate(self, props, data)

        if 'FINISHED' in status:
            context.window.cursor_modal_restore()
            context.scene.frame_end = ceil(props.target_framerate*props.num_frames*props.recording_interval/1000.0)
        return status


classes = (ACRI_OT_import_acrjson,ACRI_OT_animate,)
register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
