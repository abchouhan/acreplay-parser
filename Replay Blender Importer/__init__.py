bl_info = {
    "name": "AC Replay Importer",
    "author": "Abhyudaya Chouhan",
    "version": (0, 2, 1),
    "blender": (3, 0, 0),
    "location": "3D View > Toolbox > Animation tab > AC Replay Importer",
    "description": "Animate your cars using Assetto Corsa replays",
    #"warning": "",
    "doc_url": "https://github.com/abchouhan/acreplay-parser",
    "category": "Animation",
}

import bpy
from bpy.props import StringProperty, IntProperty, FloatProperty, PointerProperty
from . import operators, panel


class ACReplayImporterProperties(bpy.types.PropertyGroup):
	acrjson_filepath:       StringProperty(default="")
	num_frames:             IntProperty(default=0)
	recording_interval:     FloatProperty(default=0.0) # in Hz
	target_framerate:       FloatProperty(name="Target Frame Rate", default=30.0, min=1.0, precision=2)
	chassis_object:         PointerProperty(name="Chassis", type=bpy.types.Object)
	wheelfl_object:         PointerProperty(name="FL Wheel", type=bpy.types.Object)
	wheelfr_object:         PointerProperty(name="FR Wheel", type=bpy.types.Object)
	wheelrl_object:         PointerProperty(name="RL Wheel", type=bpy.types.Object)
	wheelrr_object:         PointerProperty(name="RR Wheel", type=bpy.types.Object)
	wheelstaticfl_object:   PointerProperty(name="FL Static", type=bpy.types.Object)
	wheelstaticfr_object:   PointerProperty(name="FR Static", type=bpy.types.Object)
	wheelstaticrl_object:   PointerProperty(name="RL Static", type=bpy.types.Object)
	wheelstaticrr_object:   PointerProperty(name="RR Static", type=bpy.types.Object)

def manual_map():
    url_manual_prefix = "https://github.com/abchouhan/acreplay-parser?tab=readme-ov-file#addon"
    url_manual_mapping = (("bpy.ops.scene.acreplay_import_json", ""),
						  ("bpy.ops.scene.acreplay_animate", ""),)
    return url_manual_prefix, url_manual_mapping

modules = (operators, panel)


def register():
    bpy.utils.register_class(ACReplayImporterProperties)
    bpy.types.Scene.acreplay_importer_props = bpy.props.PointerProperty(type=ACReplayImporterProperties)
    for m in modules:
        m.register()
    bpy.utils.register_manual_map(manual_map)

def unregister():
    bpy.utils.unregister_manual_map(manual_map)
    for m in modules:
        m.unregister()
    del bpy.types.Scene.acreplay_importer_props
    bpy.utils.unregister_class(ACReplayImporterProperties)


if __name__ == "__main__":
    register()
