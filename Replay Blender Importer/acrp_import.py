import os
import bpy
from math import radians
from mathutils import Quaternion
import numpy as np


use_slots = (4, 4, 0) <= bpy.app.version


class custom_property:
    def __init__(self, name, subtype, default, limits, interpolation, func=None, items=None, desc=None):
        self.name = name
        self.subtype = subtype
        self.default = default
        self.limits = limits
        self.interpolation = interpolation
        self.func = func
        self.items = items
        self.desc = desc
    def assign(self, ui_prop):
        if self.subtype == "ENUM":
            ui_prop.update(
                default=self.default,
                min=self.limits[0],
                max=self.limits[1],
                items=self.items,
                description=self.desc)
        elif type(self.default) is bool:
            ui_prop.update(
                subtype=self.subtype,
                default=self.default,
                description=self.desc)
        else:
            ui_prop.update(
                subtype=self.subtype,
                default=self.default,
                min=self.limits[0],
                max=self.limits[1],
                description=self.desc)


f2_range = (np.finfo('f2').min, np.finfo('f2').max)
u4_range = (np.iinfo('u4').min, np.iinfo('u4').max)

chassis_properties = [
    custom_property("gas",                    "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("brake",                  "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("velocity",               "VELOCITY", [0.0,0.0,0.0], f2_range,   "LINEAR"),
    custom_property("rpm",                    "NONE",          0.0, f2_range,        "LINEAR"),
    custom_property("steerAngle",             "ANGLE",         0.0, (-360.0, 360.0), "LINEAR",   np.vectorize(lambda x: -radians(x))),
    custom_property("gear",                   "NONE",            0, ( -1, 254),      "CONSTANT", lambda x: x-1, desc="-1: reverse, 0: neutral, 1: 1st gear, 2: 2nd gear, etc"),
    custom_property("boost",                  "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/0.51),
    custom_property("fuel",                   "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("fuelPerLap",             "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55, desc="Amount of fuel predicted to be used, based on average per-lap fuel consumption (100% on first lap)"),
    custom_property("lights",                 "NONE",        False, None,            "CONSTANT", desc="Whether headlights, taillights, instrument lights, etc. are on"),
    custom_property("horn",                   "NONE",        False, None,            "CONSTANT"),
    custom_property("dirt",                   "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55, desc="Amount of dirt on car body"),
    custom_property("damageFront",            "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("damageFrontDeformation", "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55, desc="Hood + bumper damage"),
    custom_property("damageRear",             "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("damageLeft",             "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("damageRight",            "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("engineHealth",           "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("gearboxBeingDamaged",    "NONE",        False, None,            "CONSTANT", desc="Whether the gearbox is being damaged (e.g., when changing gears without clutch)"),
    custom_property("bodyworkNoise",          "NONE",          0.0, f2_range,        "LINEAR",   desc="Amount of mechanical noise (in-game audio units) the car is making"),
    custom_property("drivetrainSpeed",        "NONE",          0.0, f2_range,        "LINEAR"),
    custom_property("currentLap",             "NONE",            1, (  1, 256),      "CONSTANT", lambda x: x+1),
    custom_property("currentLapTime",         "TIME_ABSOLUTE", 0.0, u4_range,        "LINEAR",   lambda x: x/1000.0),
    custom_property("lastLapTime",            "TIME_ABSOLUTE", 0.0, u4_range,        "LINEAR",   lambda x: x/1000.0),
    custom_property("bestLapTime",            "TIME_ABSOLUTE", 0.0, u4_range,        "LINEAR",   lambda x: x/1000.0),
    custom_property("cameraDir",              "ENUM",            0, (  0, 3),        "CONSTANT", None,
                    [("FORWARD",  "Forward",  ""),
                     ("LEFT",	  "Left",     ""),
                     ("RIGHT",	  "Right",    ""),
                     ("BACKWARD", "Backward", "")],
                    desc="Direction the in-game camera is pointing")
]
wheel_properties = [
    custom_property("dirt",                   "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR", desc="Amount of dirt on wheel"),
    custom_property("angularVelocity",   	  "NONE",          0.0, f2_range,        "LINEAR"),
    custom_property("slipAngle",              "NONE",          0.0, f2_range,        "LINEAR", desc="Angle of heading vs. angle of travel.\nAC typically reports this as zero"),
    custom_property("slipRatio",              "NONE",          0.0, f2_range,        "LINEAR", desc="Actual angular velocity vs. pure rolling angular velocity"),
    custom_property("ndSlip",                 "NONE",          0.0, f2_range,        "LINEAR"),
    custom_property("load",                   "NONE",          0.0, f2_range,        "LINEAR", desc="Load on wheel in Newtons")
]
extra_properties = [
    custom_property("clutch",                 "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: (255-x)/2.55),
    custom_property("handbrake",              "PERCENTAGE",    0.0, (0.0, 100.0),    "LINEAR",   lambda x: x/2.55),
    custom_property("wipers",                 "ENUM",            0, (  0, 4),        "CONSTANT", None,
                    [("OFF",	 "Off",     ""),
                     ("SLOWEST", "Slowest", ""),
                     ("SLOW",	 "Slow",    ""),
                     ("FAST",    "Fast",    ""),
                     ("FASTEST", "Fastest", "")],
                    desc="Front and rear windshield wipers"),
    custom_property("turnSignals",            "ENUM",            0, (  0, 4),        "CONSTANT", None,
                    [("OFF",	  "Off",      "", "", 0),
                     ("LEFT",	  "Left",     "", "BACK", 1),
                     ("RIGHT",	  "Right",    "", "FORWARD", 2),
                     ("HAZARDS",  "Hazards",  "", "ARROW_LEFTRIGHT", 3),
                     ("HAZARDS+", "Hazards+", "Hazards + extra dashboard hazard light", "MARKER", 4)]),

    custom_property("highBeams",              "NONE",        False, None,            "CONSTANT", np.vectorize(lambda x: not x), desc="Whether high-beam lights are on"),
    custom_property("extraOptionA",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionB",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionC",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionD",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionE",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionF",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionG",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionH",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionI",           "NONE",        False, None,            "CONSTANT"),
    custom_property("extraOptionJ",           "NONE",        False, None,            "CONSTANT")
]


def keyframe_loc_rot(obj, action, frames, num_frames, loc, rot):
    anim_data = obj.animation_data_create()
    anim_data.action = action
    if use_slots:
        slot = action.slots.get(f"OB{obj.name}")
        if slot is None:
            slot = action.slots.new(id_type="OBJECT", name=obj.name)
        channelbag = action.layers[0].strips[0].channelbag(slot, ensure=True)
        transforms_group = channelbag.groups.get("Object Transforms")
        if transforms_group is None:
            transforms_group = channelbag.groups.new("Object Transforms")
        anim_data.action_slot = slot
    interpolation_values = np.full(shape=num_frames, fill_value=bpy.types.Keyframe.bl_rna.properties["interpolation"].enum_items["LINEAR"].value)

    # Keyframe translations
    for i in range(0, 3):
        if use_slots:
            fc_loc = channelbag.fcurves.new(data_path="location", index=i)
            fc_loc.group = transforms_group
        else:
            fc_loc = action.fcurves.new(data_path="location", index=i, action_group="Object Transforms")
        fc_loc.keyframe_points.add(count=num_frames)
        co = np.zeros(num_frames*2)
        co[0::2] = frames
        co[1::2] = loc[i]
        fc_loc.keyframe_points.foreach_set("co", co)
        fc_loc.keyframe_points.foreach_set("interpolation", interpolation_values)
        fc_loc.update()

    obj.rotation_mode = "QUATERNION"
    quat = np.zeros(shape=(num_frames, 4))
    x = (1.0, 0.0, 0.0)
    y = (0.0, 1.0, 0.0)
    z = (0.0, 0.0, 1.0)

    for i in range(0, num_frames):
        # Convert YXZ Euler angles (ZXY in Blender) to a quaternion
        quat[i][:] = (Quaternion(z, rot[2][i]) @
                      Quaternion(x, rot[0][i]) @
                      Quaternion(y, rot[1][i]))[:]
        # Negate the quaternion if it results in a smaller delta between frames
        # This (usually) prevents incorrect interpolation
        # TODO investigate interpolation issues
        if i > 0:
            diff = np.linalg.norm(quat[i][:]-quat[i-1][:])
            negated_diff = np.linalg.norm(-1*quat[i][:]-quat[i-1][:])
            if negated_diff < diff:
                quat[i][:] *= -1
    quat = np.transpose(quat)

    # Keyframe rotations
    for i in range(0, 4):
        if use_slots:
            fc_rot = channelbag.fcurves.new(data_path="rotation_quaternion", index=i)
            fc_rot.group = transforms_group
        else:
            fc_rot = action.fcurves.new(data_path="rotation_quaternion", index=i, action_group="Object Transforms")
        fc_rot.keyframe_points.add(count=num_frames)
        co = np.zeros(num_frames*2)
        co[0::2] = frames
        co[1::2] = quat[i]
        fc_rot.keyframe_points.foreach_set("co", co)
        fc_rot.keyframe_points.foreach_set("interpolation", interpolation_values)
        fc_rot.update()

def keyframe_custom_property(obj, action, frames, num_frames, prop, data):
    interpolation_values = np.full(shape=num_frames, fill_value=bpy.types.Keyframe.bl_rna.properties["interpolation"].enum_items[prop.interpolation].value)
    if prop.name not in obj:
        obj[prop.name] = prop.default
    ui_prop = obj.id_properties_ui(prop.name)
    prop.assign(ui_prop)


    if len(data) == num_frames:
        indices = 1
    else: # To handle multi-dimensional properties (e.g., velocity)
        indices = len(data)

    for i in range(0, indices):
        if use_slots:
            slot = action.slots.get(f"OB{obj.name}")
            if slot is None:
                slot = action.slots.new(id_type="OBJECT", name=obj.name)
            channelbag = action.layers[0].strips[0].channelbag(slot, ensure=True)
            custom_props_group = channelbag.groups.get("Custom Properties")
            if custom_props_group is None:
                custom_props_group = channelbag.groups.new("Custom Properties")
            fc = channelbag.fcurves.new(data_path=f'["{prop.name}"]', index=i)
            fc.group = custom_props_group
        else:
            fc = action.fcurves.new(data_path=f'["{prop.name}"]', index=i, action_group="Custom Properties")
        fc.keyframe_points.add(count=num_frames)
        co = np.zeros(num_frames*2)
        co[0::2] = frames

        if indices == 1:
            if prop.func is not None: co[1::2] = prop.func(data)
            else: co[1::2] = data
        else:
            if prop.func is not None: co[1::2] = prop.func(data[i])
            else: co[1::2] = data[i]

        fc.keyframe_points.foreach_set("co", co)
        fc.keyframe_points.foreach_set("interpolation", interpolation_values)
        fc.update()

def animate(self, acrp_props, data):
    # Get first 32 chars of filename as action names are limited to 63 chars
    filename = os.path.split(acrp_props.acrcsv_filepath)[1][:32]
    name_index = 0
    if use_slots:
        new_filename = filename
        while True: # Create a new action with a unique name given the filename
            action = bpy.data.actions.get(new_filename)
            if action is None:
                action = bpy.data.actions.new(new_filename)
                layer = action.layers.new("Layer")
                strip = layer.strips.new(type="KEYFRAME")
                break
            else:
                name_index += 1
                new_filename = f"{filename}.{str(name_index).zfill(3)}"
        filename = new_filename
        action = bpy.data.actions.get(filename)
    else:
        action = None

    fields = data.dtype.fields

    if "position.x" not in fields or "position.y" not in fields or "position.z" not in fields:
        self.report({'ERROR'}, ".csv file does not contain chassis position data!")
        return {'CANCELLED'}
    if "rotation.x" not in fields or "rotation.y" not in fields or "rotation.z" not in fields:
        self.report({'ERROR'}, ".csv file does not contain chassis rotation data!")
        return {'CANCELLED'}

    factor = acrp_props.target_framerate/(1000.0/acrp_props.recording_interval)
    frames = [factor*i+acrp_props.start_frame for i in range(0, acrp_props.num_frames)]

    if acrp_props.chassis_object:
        if action is None:
            action = bpy.data.actions.new("Chassis Action")
        keyframe_loc_rot(acrp_props.chassis_object, action, frames, acrp_props.num_frames,
                [data["position.x"], -data["position.z"], data["position.y"]],  # Swap Y and Z axes for Blender, and negate Z axis
                [-data["rotation.x"], data["rotation.z"], -data["rotation.y"]]) # Swap Y and Z axes for Blender, and negate X and Y axes
        for prop in chassis_properties:
            if prop.name in fields:
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, data[prop.name])
            elif prop.name == "velocity" and "velocity.x" in fields and "velocity.y" in fields and "velocity.z" in fields:
                # Swap Y and Z axes for Blender, and negate Z axis
                velocity = [data["velocity.x"], -data["velocity.z"], data["velocity.y"]]
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, velocity)
            else:
                self.report({'ERROR'}, f".csv file does not contain {prop.name} column")
        for prop in extra_properties:
            if prop.name in fields:
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, data[prop.name])
            elif prop.name == "highBeams" and "lowBeams" in fields:
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, data["lowBeams"])

    if acrp_props.wheelfl_object is None and acrp_props.wheelstaticfl_object is None and \
        acrp_props.wheelfr_object is None and acrp_props.wheelstaticfr_object is None and \
        acrp_props.wheelrl_object is None and acrp_props.wheelstaticrl_object is None and \
        acrp_props.wheelrr_object is None and acrp_props.wheelstaticrr_object is None:
        return {'FINISHED'}

    wheels = ["FL", "FR", "RL", "RR"]
    for i in range(len(wheels)):
        wheel = f"wheel{wheels[i]}"
        pos_str = f"{wheel}.position"
        rot_str = f"{wheel}.rotation"
        pos_static_str = f"{wheel}.staticPosition"
        rot_static_str = f"{wheel}.staticRotation"

        if f"{pos_str}.x" in fields and f"{pos_str}.y" in fields and f"{pos_str}.z" in fields and \
            f"{rot_str}.x" in fields and f"{rot_str}.y" in fields and f"{rot_str}.z" in fields and \
            f"{pos_static_str}.x" in fields and f"{pos_static_str}.y" in fields and f"{pos_static_str}.z" in fields and \
            f"{rot_static_str}.x" in fields and f"{rot_static_str}.y" in fields and f"{rot_static_str}.z" in fields:
            # Swap Y and Z axes for Blender, and negate Z axis
            pos_arr = [ data[f"{pos_str}.x"],
                       -data[f"{pos_str}.z"],
						data[f"{pos_str}.y"]]
            pos_static_arr = [ data[f"{pos_static_str}.x"],
							  -data[f"{pos_static_str}.z"],
                               data[f"{pos_static_str}.y"]]
            # Swap Y and Z axes for Blender, and negate X and Y axes
            rot_arr = [-data[f"{rot_str}.x"],
                        data[f"{rot_str}.z"],
					   -data[f"{rot_str}.y"]]
            rot_static_arr = [-data[f"{rot_static_str}.x"],
                               data[f"{rot_static_str}.z"],
                              -data[f"{rot_static_str}.y"]]

            match i:
                case 0:
                    obj = acrp_props.wheelfl_object
                    static_obj = acrp_props.wheelstaticfl_object
                case 1:
                    obj = acrp_props.wheelfr_object
                    static_obj = acrp_props.wheelstaticfr_object
                case 2:
                    obj = acrp_props.wheelrl_object
                    static_obj = acrp_props.wheelstaticrl_object
                case 3:
                    obj = acrp_props.wheelrr_object
                    static_obj = acrp_props.wheelstaticrr_object
                case _:
                    obj = None
                    static_obj = None

            if obj is not None:
                if action is None:
                    action = bpy.data.actions.new(f"{wheels[i]} Wheel Action")
                keyframe_loc_rot(obj, action, frames, acrp_props.num_frames, pos_arr, rot_arr)
                for prop in wheel_properties:
                    if f"{wheel}.{prop.name}" in fields:
                        keyframe_custom_property(obj, action, frames, acrp_props.num_frames, prop, data[f"{wheel}.{prop.name}"])
                    else:
                        self.report({'ERROR'}, f".csv file does not contain {wheel}.{prop.name} column")
            if static_obj is not None:
                if action is None:
                    action = bpy.data.actions.new(f"{wheels[i]} Wheel Static Action")
                keyframe_loc_rot(static_obj, action, frames, acrp_props.num_frames, pos_static_arr, rot_static_arr)
        else:
            self.report({'ERROR'}, ".csv file does not contain complete wheel position/rotation data!")
            return {'CANCELLED'}

    return {'FINISHED'}
