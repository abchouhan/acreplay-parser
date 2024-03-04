import json
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

from . import acrp_import


class ACRI_OT_import_acrjson(Operator, ImportHelper):
    bl_idname = "acri.import_acrjson"
    bl_label = "Import .json"
    bl_description = "Import AC Replay animation data (*.json) that was outputted by AC Replay Parser"
    
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    def set_path(self, context, path):
        context.scene.acrjson_filepath = path

    def execute(self, context):
        self.set_path(context, self.filepath)

        try:
            with open(context.scene.acrjson_filepath, 'r') as f:
                first_three_lines = f.readline()+f.readline()+f.readline()[0:-2]+"}"
                data = json.loads(first_three_lines)
        except:
            self.set_path(context, "")
            self.report({'ERROR'}, "Invalid .json file!")
            return {'CANCELLED'}

        frames = data["numFrames"]
        hz = data["recordingInterval"]

        if (frames is None) or (hz is None):
            self.set_path(context, "")
            self.report({'ERROR'}, "Invalid .json file!")
            return {'CANCELLED'}

        context.scene.num_frames = frames
        context.scene.recording_interval = hz

        return {'FINISHED'}

class ACRI_OT_animate(Operator):
    bl_idname = "acri.animate"
    bl_label = "Animate"
    bl_description = "Apply animation data to selected objects"

    def execute(self, context):
        context.window.cursor_set("WAIT")

        scn = context.scene
        with open(scn.acrjson_filepath, 'r') as f:
            data = json.loads(f.read())
        acrp_import.animate(scn, data)

        context.window.cursor_modal_restore()
        return {'FINISHED'}


classes = (ACRI_OT_import_acrjson,ACRI_OT_animate,)
register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
