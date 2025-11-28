import bpy
from bpy.props import StringProperty, IntProperty, FloatProperty, PointerProperty
from . import operators, panel


class ACReplayImporterProperties(bpy.types.PropertyGroup):
	acrcsv_filepath:        StringProperty(default="")
	num_frames:             IntProperty(default=0)
	recording_interval:     FloatProperty(default=0.0) # in Hz
	target_framerate:       FloatProperty(name="Target Frame Rate", default=30.0, min=1.0, precision=2)
	chassis_object:         PointerProperty(name="Chassis", type=bpy.types.Object)
	wheelfl_object:         PointerProperty(name="FL Wheel",  description="Front-left wheel",   type=bpy.types.Object)
	wheelfr_object:         PointerProperty(name="FR Wheel",  description="Front-right wheel",  type=bpy.types.Object)
	wheelrl_object:         PointerProperty(name="RL Wheel",  description="Rear-left wheel",    type=bpy.types.Object)
	wheelrr_object:         PointerProperty(name="RR Wheel",  description="Rear-right wheel",   type=bpy.types.Object)
	wheelstaticfl_object:   PointerProperty(name="FL Static", description="Front-left wheel static object(s)",  type=bpy.types.Object)
	wheelstaticfr_object:   PointerProperty(name="FR Static", description="Front-right wheel static object(s)", type=bpy.types.Object)
	wheelstaticrl_object:   PointerProperty(name="RL Static", description="Rear-left wheel static object(s)",   type=bpy.types.Object)
	wheelstaticrr_object:   PointerProperty(name="RR Static", description="Rear-right wheel static object(s)",  type=bpy.types.Object)

def manual_map():
    url_manual_prefix = "https://github.com/abchouhan/acreplay-parser?tab=readme-ov-file#addon"
    url_manual_mapping = (("bpy.ops.scene.acreplay_import_csv", ""),
						  ("bpy.ops.scene.acreplay_animate", ""),)
    return url_manual_prefix, url_manual_mapping

modules = [operators, panel]


def register():
    bpy.utils.register_class(ACReplayImporterProperties)
    bpy.types.Scene.acreplay_importer_props = bpy.props.PointerProperty(type=ACReplayImporterProperties)
    for m in modules:
        m.register()
    bpy.utils.register_manual_map(manual_map)

def unregister():
    bpy.utils.unregister_manual_map(manual_map)
    for m in reversed(modules):
        m.unregister()
    del bpy.types.Scene.acreplay_importer_props
    bpy.utils.unregister_class(ACReplayImporterProperties)
