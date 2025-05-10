import os
import bpy
from math import pi
from mathutils import Quaternion
import numpy as np


use_slots = (4, 4, 0) <= bpy.app.version


class custom_property:
    def __init__(self, name, subtype, default, limits, interpolation, func, desc=None):
        self.name = name
        self.subtype = subtype
        self.default = default
        self.limits = limits
        self.interpolation = interpolation
        self.func = func
        self.desc= desc
    def assign(self, ui_prop):
        if type(self.default) is bool:
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


legacy_properties = [
    custom_property("speedX",                 "NONE",          0.0, (-10000.0, 10000.0), "LINEAR",   lambda x: x),
    custom_property("speedY",                 "NONE",          0.0, (-10000.0, 10000.0), "LINEAR",   lambda x: x),
    custom_property("headlights",             "NONE",        False, None,                "LINEAR",   lambda x: x),
    custom_property("steering",               "ANGLE",         0.0, (-360.0, 360.0),     "LINEAR",   lambda x: -x*pi/180.0)
]
chassis_properties = [
    custom_property("gas",                    "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("brake",                  "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("velocity",        "VELOCITY",   [0.0,0.0,0.0], (-10000.0, 10000.0), "LINEAR",   lambda x: x),
    custom_property("rpm",                    "NONE",          0.0, (0.0, 10000.0),      "LINEAR",   lambda x: x),
    custom_property("steerAngle",             "ANGLE",         0.0, (-360.0, 360.0),     "LINEAR",   lambda x: -x*pi/180.0),
    custom_property("gear",                   "NONE",            0, ( -1, 10000),        "CONSTANT", lambda x: x-1, "-1: reverse, 0: neutral, 1: 1st gear, 2: 2nd gear, etc"),
    custom_property("boost",                  "FACTOR",        0.0, (0.0, 1.0),          "LINEAR",   lambda x: x/255),
    custom_property("fuel",                   "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("fuelPerLap",             "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55, "Amount of fuel predicted to be used, based on average per-lap fuel consumption"),
    custom_property("lights",                 "NONE",        False, None,                "CONSTANT", lambda x: x, "Whether headlights, taillights, instrument lights, etc. are on"),
    custom_property("horn",                   "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("dirt",                   "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55, "Amount of dirt on car body"),
    custom_property("damageFront",            "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("damageFrontDeformation", "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55, "Hood + bumper damage"),
    custom_property("damageRear",             "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("damageLeft",             "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("damageRight",            "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("engineHealth",           "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("gearboxBeingDamaged",    "NONE",        False, None,                "CONSTANT", lambda x: x, "Whether the gearbox is being damaged (e.g. when changing gears without clutch)"),
    custom_property("bodyworkNoise",          "NONE",          0.0, (0.0, 10000.0),      "LINEAR",   lambda x: x, "Amount of mechanical noise (in-game audio units) the car is making"),
    custom_property("drivetrainSpeed",        "NONE",          0.0, (0.0, 10000.0),      "LINEAR",   lambda x: x),
    custom_property("currentLap",             "NONE",            1, (  1, 255),          "CONSTANT", lambda x: x),
    custom_property("currentLapTime",         "TIME_ABSOLUTE", 0.0, (0.0, 10000.0),      "LINEAR",   lambda x: x/1000.0),
    custom_property("lastLapTime",            "TIME_ABSOLUTE", 0.0, (0.0, 10000.0),      "LINEAR",   lambda x: x/1000.0),
    custom_property("bestLapTime",            "TIME_ABSOLUTE", 0.0, (0.0, 10000.0),      "LINEAR",   lambda x: x/1000.0),
    custom_property("cameraDir",              "NONE",            0, (  0, 3),            "CONSTANT", lambda x: x, "Direction the in-game camera is pointing.\n0: forward, 1: left, 2: right, 3: backward")
]
wheel_properties = [
    custom_property("tireDirt",               "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x, "Amount of dirt on tire"),
    custom_property("wheelAngularVelocity",   "NONE",          0.0, (-10000.0, 10000.0), "LINEAR",   lambda x: x),
    custom_property("slipAngle",              "NONE",          0.0, (-10000.0, 10000.0), "LINEAR",   lambda x: x, "Angle of heading vs. angle of travel.\nAC typically reports this as zero"),
    custom_property("slipRatio",              "NONE",          0.0, (-10000.0, 10000.0), "LINEAR",   lambda x: x, "Actual angular velocity vs. pure rolling angular velocity"),
    custom_property("ndSlip",                 "NONE",          0.0, (-10000.0, 10000.0), "LINEAR",   lambda x: x),
    custom_property("load",                   "NONE",          0.0, (-10000.0, 10000.0), "LINEAR",   lambda x: x, "Load on wheel in Newtons")
]
extra_properties = [
    custom_property("clutch",                 "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: (255-x)/2.55),
    custom_property("handbrake",              "PERCENTAGE",    0.0, (0.0, 100.0),        "LINEAR",   lambda x: x/2.55),
    custom_property("wipers",                 "NONE",            0, (  0, 4),            "CONSTANT", lambda x: x, "Front and rear windshield wipers.\n0: off, 1: lowest speed, ..., 4: highest speed"),
    custom_property("turnSignals",            "NONE",            0, (  0, 4),            "CONSTANT", lambda x: x, "0: off, 1: left, 2: right, 3: only hazards, 4: hazards + extra dashboard hazard light"),
    custom_property("highBeams",              "NONE",        False, None,                "CONSTANT", np.vectorize(lambda x: not x), "Whether high-beam lights are on"),
    custom_property("extraOptionA",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionB",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionC",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionD",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionE",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionF",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionG",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionH",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionI",           "NONE",        False, None,                "CONSTANT", lambda x: x),
    custom_property("extraOptionJ",           "NONE",        False, None,                "CONSTANT", lambda x: x)
]


def keyframe_loc_rot(obj, action, frames, num_frames, loc, rot):
    anim_data = obj.animation_data_create()
    anim_data.action = action
    if use_slots:
        slot = action.slots.get("OB"+obj.name)
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
        # This prevents incorrect interpolation
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
        if use_slots:
            slot = action.slots.get("OB"+obj.name)
            if slot is None:
                slot = action.slots.new(id_type="OBJECT", name=obj.name)
            channelbag = action.layers[0].strips[0].channelbag(slot, ensure=True)
            custom_props_group = channelbag.groups.get("Custom Properties")
            if custom_props_group is None:
                custom_props_group = channelbag.groups.new("Custom Properties")
            fc = channelbag.fcurves.new(data_path='["' + prop.name + '"]', index=0)
            fc.group = custom_props_group
        else:
            fc = action.fcurves.new(data_path='["' + prop.name + '"]', index=0, action_group="Custom Properties")
        fc.keyframe_points.add(count=num_frames)
        co = np.zeros(num_frames*2)
        co[0::2] = frames
        co[1::2] = prop.func(data)
        fc.keyframe_points.foreach_set("co", co)
        fc.keyframe_points.foreach_set("interpolation", interpolation_values)
        fc.update()
    elif len(data[0]) == num_frames:
        for i in range(0, len(data)):
            if use_slots:
                slot = action.slots.get("OB"+obj.name)
                if slot is None:
                    slot = action.slots.new(id_type="OBJECT", name=obj.name)
                channelbag = action.layers[0].strips[0].channelbag(slot, ensure=True)
                custom_props_group = channelbag.groups.get("Custom Properties")
                if custom_props_group is None:
                    custom_props_group = channelbag.groups.new("Custom Properties")
                fc = channelbag.fcurves.new(data_path='["' + prop.name + '"]', index=i)
                fc.group = custom_props_group
            else:
                fc = action.fcurves.new(data_path='["' + prop.name + '"]', index=i, action_group="Custom Properties")
            fc.keyframe_points.add(count=num_frames)
            co = np.zeros(num_frames*2)
            co[0::2] = frames
            co[1::2] = prop.func(data[i])
            fc.keyframe_points.foreach_set("co", co)
            fc.keyframe_points.foreach_set("interpolation", interpolation_values)
            fc.update()

def animate(self, acrp_props, data):
    # Get first 32 chars of filename as action names are limited to 63 chars
    filename = os.path.split(acrp_props.acrjson_filepath)[1][:32]
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
                new_filename = filename+"."+str(name_index).zfill(3)
        filename = new_filename

    if "x" in data and "y" in data and "z" in data:
        # Swap Y and Z axes for Blender, and negate Z axis
        loc = [np.array(data.get("x")),
               np.negative(data.get("z")),
               np.array(data.get("y"))]
    else:
        self.report({'ERROR'}, ".json file does not contain chassis position data!")
        return {'CANCELLED'}

    if "rotX" in data and "rotY" in data and "rotZ" in data:
        # Swap Y and Z axes for Blender, and negate X and Y axes
        rot = [np.negative(data.get("rotX")),
               np.array(data.get("rotZ")),
               np.negative(data.get("rotY"))]
    else:
        self.report({'ERROR'}, ".json file does not contain chassis rotation data!")
        return {'CANCELLED'}

    if "wheelX" in data and "wheelY" in data and "wheelZ" in data:
        wheel_loc = np.array([np.array(data.get("wheelX")),
                              np.negative(data.get("wheelZ")),
                              np.array(data.get("wheelY"))])
    else:
        self.report({'ERROR'}, ".json file does not contain wheel position data!")
        return {'CANCELLED'}

    if "wheelRotX" in data and "wheelRotY" in data and "wheelRotZ" in data:
        wheel_rot = np.array([np.negative(data.get("wheelRotX")),
                              np.array(data.get("wheelRotZ")),
                              np.negative(data.get("wheelRotY"))])
    else:
        self.report({'ERROR'}, ".json file does not contain wheel rotation data!")
        return {'CANCELLED'}

    containsStaticData = False
    if "wheelStaticX" in data and "wheelStaticY" in data and "wheelStaticZ" in data and \
       "wheelStaticRotX" in data and "wheelStaticRotY" in data and "wheelStaticRotZ" in data:
        containsStaticData = True
        wheel_static_loc = np.array([np.array(data.get("wheelStaticX")),
                                    np.negative(data.get("wheelStaticZ")),
                                    np.array(data.get("wheelStaticY"))])

        wheel_static_rot = np.array([np.negative(data.get("wheelStaticRotX")),
                                    np.array(data.get("wheelStaticRotZ")),
                                    np.negative(data.get("wheelStaticRotY"))])

    factor = acrp_props.target_framerate/(1000.0/acrp_props.recording_interval)
    frames = [factor*(i+1) for i in range(0, acrp_props.num_frames)]

    if acrp_props.chassis_object:
        action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("Chassis Action")
        keyframe_loc_rot(acrp_props.chassis_object, action, frames, acrp_props.num_frames, loc, rot)
        for prop in legacy_properties:
            if prop.name in data:
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, np.array(data.get(prop.name)))
        for prop in chassis_properties:
            if prop.name in data:
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, np.array(data.get(prop.name)))
            elif prop.name == "velocity" and "velocityX" in data and "velocityY" in data and "velocityZ" in data:
                velocity = np.array([np.array(data.get("velocityX")),
                                     np.negative(data.get("velocityZ")),
                                     np.array(data.get("velocityY"))])
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, velocity)
        for prop in extra_properties:
            if prop.name in data:
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, np.array(data.get(prop.name)))
            elif prop.name == "highBeams" and "lowBeams" in data:
                keyframe_custom_property(acrp_props.chassis_object, action, frames, acrp_props.num_frames, prop, np.array(data.get("lowBeams")))

    wheel_props = []
    for prop in wheel_properties:
        if prop.name in data:
            wheel_props.append((prop, np.array(data.get(prop.name))))

    if acrp_props.wheelfl_object:
        action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("FL Wheel Action")
        keyframe_loc_rot(acrp_props.wheelfl_object, action, frames, acrp_props.num_frames, wheel_loc[:,0], wheel_rot[:,0])
        for prop in wheel_props:
            keyframe_custom_property(acrp_props.wheelfl_object, action, frames, acrp_props.num_frames, prop[0], prop[1][0])

    if acrp_props.wheelfr_object:
        action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("FR Wheel Action")
        keyframe_loc_rot(acrp_props.wheelfr_object, action, frames, acrp_props.num_frames, wheel_loc[:,1], wheel_rot[:,1])
        for prop in wheel_props:
            keyframe_custom_property(acrp_props.wheelfr_object, action, frames, acrp_props.num_frames, prop[0], prop[1][1])

    if acrp_props.wheelrl_object:
        action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("RL Wheel Action")
        keyframe_loc_rot(acrp_props.wheelrl_object, action, frames, acrp_props.num_frames, wheel_loc[:,2], wheel_rot[:,2])
        for prop in wheel_props:
            keyframe_custom_property(acrp_props.wheelrl_object, action, frames, acrp_props.num_frames, prop[0], prop[1][2])

    if acrp_props.wheelrr_object:
        action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("RR Wheel Action")
        keyframe_loc_rot(acrp_props.wheelrr_object, action, frames, acrp_props.num_frames, wheel_loc[:,3], wheel_rot[:,3])
        for prop in wheel_props:
            keyframe_custom_property(acrp_props.wheelrr_object, action, frames, acrp_props.num_frames, prop[0], prop[1][3])

    if containsStaticData:
        if acrp_props.wheelstaticfl_object:
            action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("FL Wheel Static Action")
            keyframe_loc_rot(acrp_props.wheelstaticfl_object, action, frames, acrp_props.num_frames, wheel_static_loc[:,0], wheel_static_rot[:,0])
        if acrp_props.wheelstaticfr_object:
            action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("FR Wheel Static Action")
            keyframe_loc_rot(acrp_props.wheelstaticfr_object, action, frames, acrp_props.num_frames, wheel_static_loc[:,1], wheel_static_rot[:,1])
        if acrp_props.wheelstaticrl_object:
            action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("RL Wheel Static Action")
            keyframe_loc_rot(acrp_props.wheelstaticrl_object, action, frames, acrp_props.num_frames, wheel_static_loc[:,2], wheel_static_rot[:,2])
        if acrp_props.wheelstaticrr_object:
            action = bpy.data.actions.get(filename) if use_slots else bpy.data.actions.new("RR Wheel Static Action")
            keyframe_loc_rot(acrp_props.wheelstaticrr_object, action, frames, acrp_props.num_frames, wheel_static_loc[:,3], wheel_static_rot[:,3])

    return {'FINISHED'}
