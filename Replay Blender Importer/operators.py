import csv
import numpy as np
from math import ceil
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

from . import acrp_import


class ACRI_OT_import_acrcsv(Operator, ImportHelper):
    bl_idname = "scene.acreplay_import_csv"
    bl_label = "Import .csv"
    bl_description = "Import AC Replay animation data (*.csv) that was outputted by AC Replay Parser"

    filename_ext = ".csv"

    filter_glob: StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def set_path(self, context, path):
        context.scene.acreplay_importer_props.acrcsv_filepath = path

    def execute(self, context):
        self.set_path(context, self.filepath)

        try:
            with open(context.scene.acreplay_importer_props.acrcsv_filepath, 'r', newline='') as f:
                frames_str = f.readline().split()[1:]
                hz_str = f.readline().split()[1:]
                if frames_str[0] != "numFrames" or hz_str[0] != "recordingInterval":
                    self.set_path(context, "")
                    self.report({'ERROR'}, "Missing headers! Make sure the .csv file was created with AC Replay Parser 0.3.0")
                    return {'CANCELLED'}
                frames = int(frames_str[1])
                hz = int(hz_str[1])
        except:
            self.set_path(context, "")
            self.report({'ERROR'}, "Invalid .csv file!")
            return {'CANCELLED'}

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

        with open(props.acrcsv_filepath, 'r', newline='') as f:
            def fix_bools(data):
                return [x if x != 'true' and x != 'false' else (1 if x == 'true' else 0) for x in data]

            next(f)
            next(f)
            data_iter = csv.reader(f, delimiter = ',', quotechar = '"')
            data = [tuple(fix_bools(data)) for data in data_iter]
            base_types = [
                ('u4'), # frame
                ('f4'), ('f4'), ('f4'), # position
                ('f2'), ('f2'), ('f2'), # rotation
                ('f2'), ('f2'), ('f2'), # velocity
                ('f4'), ('f4'), ('f4'), # wheelFL.staticPosition
                ('f4'), ('f4'), ('f4'), # wheelFR.staticPosition
                ('f4'), ('f4'), ('f4'), # wheelRL.staticPosition
                ('f4'), ('f4'), ('f4'), # wheelRR.staticPosition
                ('f2'), ('f2'), ('f2'), # wheelFL.staticRotation
                ('f2'), ('f2'), ('f2'), # wheelFR.staticRotation
                ('f2'), ('f2'), ('f2'), # wheelRL.staticRotation
                ('f2'), ('f2'), ('f2'), # wheelRR.staticRotation
                ('f4'), ('f4'), ('f4'), # wheelFL.position
                ('f4'), ('f4'), ('f4'), # wheelFR.position
                ('f4'), ('f4'), ('f4'), # wheelRL.position
                ('f4'), ('f4'), ('f4'), # wheelRR.position
                ('f2'), ('f2'), ('f2'), # wheelFL.rotation
                ('f2'), ('f2'), ('f2'), # wheelFR.rotation
                ('f2'), ('f2'), ('f2'), # wheelRL.rotation
                ('f2'), ('f2'), ('f2'), # wheelRR.rotation
                ('f2'), ('f2'), ('f2'), ('f2'), # wheelXX.angularVelocity
                ('f2'), ('f2'), ('f2'), ('f2'), # wheelXX.slipAngle
                ('f2'), ('f2'), ('f2'), ('f2'), # wheelXX.slipRatio
                ('f2'), ('f2'), ('f2'), ('f2'), # wheelXX.ndSlip
                ('f2'), ('f2'), ('f2'), ('f2'), # wheelXX.load
                ('u1'), ('u1'), ('u1'), ('u1'), # wheelXX.dirt
                ('f2'), # steerAngle
                ('f2'), # bodyworkNoise
                ('f2'), # drivetrainSpeed
                ('u1'), ('u4'), ('u4'), ('u4'), # currentLap, currentLapTime, lastLapTime, bestLapTime
                ('u1'), ('u1'), ('f2'), # fuel, fuelPerLap, rpm
                ('u1'), ('u1'), ('u1'), ('u1'), # gear, gas, brake, boost
                ('u1'), ('u1'), ('u1'), ('u1'), ('u1'), # damageX
                ('b'), ('b'), ('u1'), ('u1'), ('b'), ('u1'), # lights, horn, cameraDir, engineHealth, gearboxBeingDamaged, dirt
			]
            extra_types = [
                ('u1'), ('u1'), ('u1'), ('u1'), ('b'), # clutch, handbrake, wipers, turnSignals, lowBeams
                ('b'), ('b'), ('b'), ('b'), ('b'), ('b'), ('b'), ('b'), ('b'), ('b') # extraOptionX
            ]

            if len(base_types) == len(data[0]): types = base_types
            elif len(base_types)+len(extra_types) == len(data[0]): types = base_types+extra_types
            else:
                self.set_path(context, "")
                self.report({'ERROR'}, "Column count mismatch! Make sure the .csv file was created with AC Replay Parser 0.3.0")
                return {'CANCELLED'}
            dtypes = np.dtype(list(zip(data[0], types)))
            data_array = np.array(data[1:], dtype=dtypes)
            status = acrp_import.animate(self, props, data_array)

        if 'FINISHED' in status:
            context.window.cursor_modal_restore()
            context.scene.frame_start = min(context.scene.frame_start, props.start_frame)
            context.scene.frame_end = max(context.scene.frame_end, props.start_frame+ceil(props.target_framerate*props.num_frames*props.recording_interval/1000.0)-1)
        return status


classes = [ACRI_OT_import_acrcsv, ACRI_OT_animate]
register, unregister = bpy.utils.register_classes_factory(classes)
