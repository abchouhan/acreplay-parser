import bpy
import math


# Prevents 0 wrapping to 360 and vice versa
def fix_rotation_wrapping(curr, prev):
    delta = curr-prev
    if delta >= 330.0*math.pi/180.0:
        return curr-2.0*math.pi
    elif delta <= -330.0*math.pi/180.0:
        return curr+2.0*math.pi
    return curr

def chassis(obj, frames, num_frames, loc, rot):
    obj.animation_data_create()
    obj.animation_data.action = bpy.data.actions.new("Chassis Action")
    for i in range(0, 3):
        fc_loc = obj.animation_data.action.fcurves.new(data_path="location", index=i, action_group="Object Transforms")
        fc_rot = obj.animation_data.action.fcurves.new(data_path="rotation_euler", index=i, action_group="Object Transforms")
        fc_loc.keyframe_points.add(count=num_frames)
        fc_rot.keyframe_points.add(count=num_frames)
        fc_loc.keyframe_points.foreach_set("co", [j for co in zip(frames, loc[i]) for j in co])
        if i != 2:
            fc_rot.keyframe_points.foreach_set("co", [j for co in zip(frames, rot[i]) for j in co])
        else:
            prev_rot = 0.0
            for j in range(0, num_frames):
                rot_z = fix_rotation_wrapping(rot[i][j], prev_rot)
                prev_rot = rot_z
                fc_rot.keyframe_points[j].co = frames[j], rot_z
        fc_loc.update()
        fc_rot.update()

def wheel(obj, wheel_index, frames, num_frames, loc, rot, mod, debug_info=False):
    obj.animation_data_create()
    obj.animation_data.action = bpy.data.actions.new("Wheel Action")

    if debug_info:
        obj["prev_rot_x"] = 0.0
        obj["delta"] = 0.0
        obj["prev_mod"] = 0
        obj["curr_mod"] = 0
        obj["prev_val"] = 0.0
        obj["curr_val"] = 0.0
        fc_prev_rot_x = obj.animation_data.action.fcurves.new(data_path='["prev_rot_x"]',   index=0, action_group="Custom Properties")
        fc_delta =      obj.animation_data.action.fcurves.new(data_path='["delta"]',        index=0, action_group="Custom Properties")
        fc_prev_mod =   obj.animation_data.action.fcurves.new(data_path='["prev_mod"]',     index=0, action_group="Custom Properties")
        fc_curr_mod =   obj.animation_data.action.fcurves.new(data_path='["curr_mod"]',     index=0, action_group="Custom Properties")
        fc_prev_val =   obj.animation_data.action.fcurves.new(data_path='["prev_val"]',     index=0, action_group="Custom Properties")
        fc_curr_val =   obj.animation_data.action.fcurves.new(data_path='["curr_val"]',     index=0, action_group="Custom Properties")
        fc_prev_rot_x.keyframe_points.add(count=num_frames)
        fc_delta.     keyframe_points.add(count=num_frames)
        fc_prev_mod.  keyframe_points.add(count=num_frames)
        fc_curr_mod.  keyframe_points.add(count=num_frames)
        fc_prev_val.  keyframe_points.add(count=num_frames)
        fc_curr_val.  keyframe_points.add(count=num_frames)

    for i in range(0, 3):
        fc_loc = obj.animation_data.action.fcurves.new(data_path="location", index=i, action_group="Object Transforms")
        fc_rot = obj.animation_data.action.fcurves.new(data_path="rotation_euler", index=i, action_group="Object Transforms")
        fc_loc.keyframe_points.add(count=num_frames)
        fc_rot.keyframe_points.add(count=num_frames)
        fc_loc.keyframe_points.foreach_set("co", [j for co in zip(frames, loc[i][wheel_index]) for j in co])
        if i == 1:
            fc_rot.keyframe_points.foreach_set("co", [j for co in zip(frames, rot[i][wheel_index]) for j in co])
        elif i == 2:
            prev_rot = 0.0
            for j in range(0, num_frames):
                rot_z = fix_rotation_wrapping(rot[i][wheel_index][j], prev_rot)
                prev_rot = rot_z
                fc_rot.keyframe_points[j].co = frames[j], rot_z
        elif i == 0:
            prev_rot_x = 0.0
            prev_delta = 0.0
            for j in range(0, num_frames):
                if j == 0:
                    rot_x = rot[i][wheel_index][j]
                else:
                    prev_mod = round(mod[wheel_index][j-1]/math.pi) != 0
                    curr_mod = round(mod[wheel_index][j]/math.pi) != 0
                    prev_val = rot[i][wheel_index][j-1]
                    curr_val = rot[i][wheel_index][j]

                    if curr_mod and prev_mod:
                        delta = -curr_val+prev_val
                    elif curr_mod and (not prev_mod):
                        delta = -curr_val-prev_val+math.pi
                    elif (not curr_mod) and prev_mod:
                        delta = curr_val+prev_val+math.pi
                    elif (not curr_mod) and (not prev_mod):
                        delta = curr_val-prev_val

                    delta = fix_rotation_wrapping(delta, prev_delta)

                    if debug_info:
                        fc_prev_rot_x.keyframe_points[j].co = frames[j], (prev_rot_x*180.0/math.pi)
                        fc_delta.     keyframe_points[j].co = frames[j], (delta*180.0/math.pi)
                        fc_prev_mod.  keyframe_points[j].co = frames[j], round(mod[wheel_index][j-1]/math.pi)
                        fc_curr_mod.  keyframe_points[j].co = frames[j], round(mod[wheel_index][j]/math.pi)
                        fc_prev_val.  keyframe_points[j].co = frames[j], (prev_val*180.0/math.pi)
                        fc_curr_val.  keyframe_points[j].co = frames[j], (curr_val*180.0/math.pi)
                        fc_prev_rot_x.keyframe_points[j].interpolation = 'LINEAR'
                        fc_delta.     keyframe_points[j].interpolation = 'LINEAR'
                        fc_prev_mod.  keyframe_points[j].interpolation = 'LINEAR'
                        fc_curr_mod.  keyframe_points[j].interpolation = 'LINEAR'
                        fc_prev_val.  keyframe_points[j].interpolation = 'LINEAR'
                        fc_curr_val.  keyframe_points[j].interpolation = 'LINEAR'

                    rot_x = prev_rot_x + delta
                    prev_delta = delta
                prev_rot_x = rot_x
                fc_rot.keyframe_points[j].co = frames[j], rot_x
        fc_loc.update()
        fc_rot.update()

        if debug_info:
            fc_prev_rot_x.update()
            fc_delta.     update()
            fc_prev_mod.  update()
            fc_curr_mod.  update()
            fc_prev_val.  update()
            fc_curr_val.  update()

def custom_properties(obj, frames, num_frames, fuel, gear, rpm, steering, boost, speed_x, speed_z, damage_rear, damage_front, gas, brake, headlights):
    obj["fuel"] = 0.0
    obj["gear"] = 0
    obj["rpm"] = 0.0
    obj["steering"] = 0.0
    obj["boost"] = 0.0
    obj["speed_x"] = 0.0
    obj["speed_y"] = 0.0
    obj["damage_rear"] = 0.0
    obj["damage_front"] = 0.0
    obj["gas"] = 0.0
    obj["brake"] = 0.0
    obj["headlights"] = False

    fc_fuel =       obj.animation_data.action.fcurves.new(data_path='["fuel"]',         index=0, action_group="Custom Properties")
    fc_gear =       obj.animation_data.action.fcurves.new(data_path='["gear"]',         index=0, action_group="Custom Properties")
    fc_rpm =        obj.animation_data.action.fcurves.new(data_path='["rpm"]',          index=0, action_group="Custom Properties")
    fc_steering =   obj.animation_data.action.fcurves.new(data_path='["steering"]',     index=0, action_group="Custom Properties")
    fc_boost =      obj.animation_data.action.fcurves.new(data_path='["boost"]',        index=0, action_group="Custom Properties")
    fc_speed_x =    obj.animation_data.action.fcurves.new(data_path='["speed_x"]',      index=0, action_group="Custom Properties")
    fc_speed_z =    obj.animation_data.action.fcurves.new(data_path='["speed_y"]',      index=0, action_group="Custom Properties")
    fc_damage_r =   obj.animation_data.action.fcurves.new(data_path='["damage_rear"]',  index=0, action_group="Custom Properties")
    fc_damage_f =   obj.animation_data.action.fcurves.new(data_path='["damage_front"]', index=0, action_group="Custom Properties")
    fc_gas =        obj.animation_data.action.fcurves.new(data_path='["gas"]',          index=0, action_group="Custom Properties")
    fc_brake =      obj.animation_data.action.fcurves.new(data_path='["brake"]',        index=0, action_group="Custom Properties")
    fc_headlights = obj.animation_data.action.fcurves.new(data_path='["headlights"]',   index=0, action_group="Custom Properties")

    fcurves = [fc_fuel, fc_gear, fc_rpm, fc_steering, fc_boost, fc_speed_x, fc_speed_z, fc_damage_r, fc_damage_f, fc_gas, fc_brake, fc_headlights]
    keyframe_points = []

    for i in range(0, len(fcurves)):
        keyframe_points.append(fcurves[i].keyframe_points)
        keyframe_points[i].add(count=num_frames)

    for i in range(0, num_frames):
        keyframe_points[0] [i].co = frames[i], (fuel[i]/255)
        keyframe_points[1] [i].co = frames[i], (gear[i]-1)
        keyframe_points[2] [i].co = frames[i], rpm[i]
        keyframe_points[3] [i].co = frames[i], steering[i]
        keyframe_points[4] [i].co = frames[i], (boost[i]/255)
        keyframe_points[5] [i].co = frames[i], speed_x[i]
        keyframe_points[6] [i].co = frames[i], speed_z[i]
        keyframe_points[7] [i].co = frames[i], damage_rear[i]
        keyframe_points[8] [i].co = frames[i], damage_front[i]
        keyframe_points[9] [i].co = frames[i], (gas[i]/255)
        keyframe_points[10][i].co = frames[i], (brake[i]/255)
        keyframe_points[11][i].co = frames[i], (headlights[i]==1)

        for k in keyframe_points:
            k[i].interpolation = 'LINEAR'

    for fc in fcurves:
        fc.update()

def animate(scn, data):
    loc, rot = [data.get("x"), data.get("z"), data.get("y")], [data.get("rotX"), data.get("rotZ"), data.get("rotY")]
    wheel_loc, wheel_rot = [data.get("wheelX"), data.get("wheelZ"), data.get("wheelY")], [data.get("wheelRotX"), data.get("wheelRotZ"), data.get("wheelRotY")]
    wheel_rot_x_modifier = data.get("wheelRotXModifier")

    fuel, gear, rpm, steering, boost = data.get("fuel"), data.get("gear"), data.get("rpm"), data.get("steering"), data.get("boost")
    speed_x, speed_z, damage_rear, damage_front = data.get("speedX"), data.get("speedZ"), data.get("damageRear"), data.get("damageFront")
    gas, brake, headlights = data.get("gas"), data.get("brake"), data.get("headlights")

    factor = scn.target_framerate/(1000.0/scn.recording_interval)
    frames = [factor*(i+1) for i in range(0, scn.num_frames)]

    if scn.chassis_object:
        chassis(scn.chassis_object, frames, scn.num_frames, loc, rot)
        custom_properties(scn.chassis_object, frames, scn.num_frames, fuel, gear, rpm, steering, boost, speed_x, speed_z, damage_rear, damage_front, gas, brake, headlights)

    if scn.wheelfl_object:
        wheel(scn.wheelfl_object, 0, frames, scn.num_frames, wheel_loc, wheel_rot, wheel_rot_x_modifier)
    if scn.wheelfr_object:
        wheel(scn.wheelfr_object, 1, frames, scn.num_frames, wheel_loc, wheel_rot, wheel_rot_x_modifier)
    if scn.wheelrl_object:
        wheel(scn.wheelrl_object, 2, frames, scn.num_frames, wheel_loc, wheel_rot, wheel_rot_x_modifier)
    if scn.wheelrr_object:
        wheel(scn.wheelrr_object, 3, frames, scn.num_frames, wheel_loc, wheel_rot, wheel_rot_x_modifier)
