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


def keyframe_loc_rot(obj, action_name, frames, num_frames, loc, rot):
    anim_data = obj.animation_data_create()
    action = bpy.data.actions.new(action_name)
    anim_data.action = action
    if use_slots:
        slot = action.slots.new(id_type="OBJECT", name=obj.name)
        layer = action.layers.new("Layer")
        strip = layer.strips.new(type="KEYFRAME")
        transforms_group = action.groups.new("Object Transforms")
        custom_props_group = action.groups.new("Custom Properties")
        anim_data.action_slot = slot
    interpolation_values = np.full(shape=num_frames, fill_value=bpy.types.Keyframe.bl_rna.properties["interpolation"].enum_items["LINEAR"].value)

    # Keyframe translations
    for i in range(0, 3):
        if use_slots:
            fc_loc = strip.channelbag(slot, ensure=True).fcurves.new(data_path="location", index=i)
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
            fc_rot = action.layers[0].strips[0].channelbag(slot, ensure=True).fcurves.new(data_path="rotation_quaternion", index=i)
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

def keyframe_custom_property(obj, frames, num_frames, prop, data):
    action = obj.animation_data.action
    interpolation_values = np.full(shape=num_frames, fill_value=bpy.types.Keyframe.bl_rna.properties["interpolation"].enum_items[prop.interpolation].value)
    if prop.name not in obj:
        obj[prop.name] = prop.default
    ui_prop = obj.id_properties_ui(prop.name)
    prop.assign(ui_prop)
    if use_slots:
        custom_props_group = action.groups["Custom Properties"]

    if len(data) == num_frames:
        if use_slots:
            slot = action.slots["OB"+obj.name]
            fc = action.layers[0].strips[0].channelbag(slot, ensure=True).fcurves.new(data_path='["' + prop.name + '"]', index=0)
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
                slot = action.slots["OB"+obj.name]
                fc = action.layers[0].strips[0].channelbag(slot, ensure=True).fcurves.new(data_path='["' + prop.name + '"]', index=i)
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

def animate(self, scn, data):
    filename = os.path.split(scn.acrjson_filepath)[1]

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

    factor = scn.target_framerate/(1000.0/scn.recording_interval)
    frames = [factor*(i+1) for i in range(0, scn.num_frames)]

    if scn.chassis_object:
        keyframe_loc_rot(scn.chassis_object, filename if use_slots else "Chassis Action", frames, scn.num_frames, loc, rot)
        for prop in legacy_properties:
            if prop.name in data:
                keyframe_custom_property(scn.chassis_object, frames, scn.num_frames, prop, np.array(data.get(prop.name)))
        for prop in chassis_properties:
            if prop.name in data:
                keyframe_custom_property(scn.chassis_object, frames, scn.num_frames, prop, np.array(data.get(prop.name)))
            elif prop.name == "velocity" and "velocityX" in data and "velocityY" in data and "velocityZ" in data:
                velocity = np.array([np.array(data.get("velocityX")),
                                     np.negative(data.get("velocityZ")),
                                     np.array(data.get("velocityY"))])
                keyframe_custom_property(scn.chassis_object, frames, scn.num_frames, prop, velocity)
        for prop in extra_properties:
            if prop.name in data:
                keyframe_custom_property(scn.chassis_object, frames, scn.num_frames, prop, np.array(data.get(prop.name)))
            elif prop.name == "highBeams" and "lowBeams" in data:
                keyframe_custom_property(scn.chassis_object, frames, scn.num_frames, prop, np.array(data.get("lowBeams")))

    wheel_props = []
    for prop in wheel_properties:
        if prop.name in data:
            wheel_props.append((prop, np.array(data.get(prop.name))))

    if scn.wheelfl_object:
        keyframe_loc_rot(scn.wheelfl_object, filename if use_slots else "FL Wheel Action", frames, scn.num_frames, wheel_loc[:,0], wheel_rot[:,0])
        for prop in wheel_props:
            keyframe_custom_property(scn.wheelfl_object, frames, scn.num_frames, prop[0], prop[1][0])

    if scn.wheelfr_object:
        keyframe_loc_rot(scn.wheelfr_object, filename if use_slots else "FR Wheel Action", frames, scn.num_frames, wheel_loc[:,1], wheel_rot[:,1])
        for prop in wheel_props:
            keyframe_custom_property(scn.wheelfr_object, frames, scn.num_frames, prop[0], prop[1][1])

    if scn.wheelrl_object:
        keyframe_loc_rot(scn.wheelrl_object, filename if use_slots else "RL Wheel Action", frames, scn.num_frames, wheel_loc[:,2], wheel_rot[:,2])
        for prop in wheel_props:
            keyframe_custom_property(scn.wheelrl_object, frames, scn.num_frames, prop[0], prop[1][2])

    if scn.wheelrr_object:
        keyframe_loc_rot(scn.wheelrr_object, filename if use_slots else "RR Wheel Action", frames, scn.num_frames, wheel_loc[:,3], wheel_rot[:,3])
        for prop in wheel_props:
            keyframe_custom_property(scn.wheelrr_object, frames, scn.num_frames, prop[0], prop[1][3])

    if containsStaticData:
        if scn.wheelstaticfl_object:
            keyframe_loc_rot(scn.wheelstaticfl_object, filename if use_slots else "FL Wheel Static Action", frames, scn.num_frames, wheel_static_loc[:,0], wheel_static_rot[:,0])
        if scn.wheelstaticfr_object:
            keyframe_loc_rot(scn.wheelstaticfr_object, filename if use_slots else "FR Wheel Static Action", frames, scn.num_frames, wheel_static_loc[:,1], wheel_static_rot[:,1])
        if scn.wheelstaticrl_object:
            keyframe_loc_rot(scn.wheelstaticrl_object, filename if use_slots else "RL Wheel Static Action", frames, scn.num_frames, wheel_static_loc[:,2], wheel_static_rot[:,2])
        if scn.wheelstaticrr_object:
            keyframe_loc_rot(scn.wheelstaticrr_object, filename if use_slots else "RR Wheel Static Action", frames, scn.num_frames, wheel_static_loc[:,3], wheel_static_rot[:,3])

    return {'FINISHED'}
