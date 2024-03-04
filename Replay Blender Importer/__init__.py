bl_info = {
    "name": "AC Replay Importer",
    "author": "Abhyudaya Chouhan (abchouhan)",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Toolbox > Animation tab > AC Replay Importer",
    "description": "Apply exported AC Replay animation data to objects",
    #"warning": "",
    #"doc_url": "",
    "category": "Animation",
}

import bpy
from bpy.props import StringProperty, IntProperty, FloatProperty, PointerProperty
from . import operators, panel


bpy.types.Scene.acrjson_filepath = StringProperty(default="")
bpy.types.Scene.num_frames = IntProperty(default=0)
bpy.types.Scene.recording_interval = FloatProperty(default=0.0) # in Hz
bpy.types.Scene.target_framerate = FloatProperty(name="Target Frame Rate", default=30.0, min=1.0, precision=2)
bpy.types.Scene.chassis_object = PointerProperty(type=bpy.types.Object)
bpy.types.Scene.wheelfl_object = PointerProperty(type=bpy.types.Object)
bpy.types.Scene.wheelfr_object = PointerProperty(type=bpy.types.Object)
bpy.types.Scene.wheelrl_object = PointerProperty(type=bpy.types.Object)
bpy.types.Scene.wheelrr_object = PointerProperty(type=bpy.types.Object)

modules = (operators, panel)


def register():
    for m in modules:
        m.register()

def unregister():
    for m in modules:
        m.unregister()
    bpy.context.scene.acrjson_filepath = ""
    bpy.context.scene.num_frames = 0
    bpy.context.scene.recording_interval = 0.0
    bpy.context.scene.target_framerate = 30.0
    bpy.context.scene.chassis_object = None
    bpy.context.scene.wheelfl_object = None
    bpy.context.scene.wheelfr_object = None
    bpy.context.scene.wheelrl_object = None
    bpy.context.scene.wheelrr_object = None


if __name__ == "__main__":
    register()
