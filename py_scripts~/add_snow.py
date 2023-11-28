import bpy
import sys
from os import environ, path, makedirs

sys.path.insert(0, './py_scripts~')

from import_export import import_scene, export_scene
from value_getters import get_float

import_scene()

bpy.context.scene.snow.coverage = get_float('coverage %')
bpy.context.scene.snow.height = get_float('height')

#bpy.context.scene.snow.coverage = 2
#bpy.context.scene.snow.height = 0

bpy.ops.object.select_all(action='SELECT')
My_objs = bpy.context.selected_objects[:]

bpy.ops.snow.create()

objs = bpy.context.selected_objects[:]
bpy.ops.object.select_all(action='DESELECT')


bpy.ops.object.select_all(action='DESELECT')

bpy.ops.mesh.primitive_cube_add(size=2)
cube = bpy.context.active_object
    # # 放大 cube
cube.scale *= 4
cube.scale.y *=2
cube.scale.x *=2
bpy.ops.object.select_all(action='DESELECT')

#cube.select_set(True)
#boolean_cube.select_set(True)
##沒用的雪
for obj in objs:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_remove(modifier="Subdiv")
    bpy.context.object.modifiers["Decimate"].ratio = 1 - get_float(
        'mesh reduction')
    if (obj.type == 'MESH'):
        bpy.data.objects.remove(obj)

bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_all(action='SELECT')

objs = bpy.context.selected_objects[:]
bpy.ops.object.select_all(action='DESELECT')
for obj in My_objs:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if (obj.type == 'MESH'):
        boolean_cube = obj
        bpy.context.view_layer.objects.active = boolean_cube
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
        bpy.context.object.modifiers["Boolean"].object = cube

        # 執行布林操作
        bpy.ops.object.modifier_apply({"object": boolean_cube}, modifier="Boolean")
        #bpy.data.objects.remove(obj)
bpy.context.view_layer.update()

        #bpy.data.objects.remove(boolean_cube)
bpy.data.objects.remove(cube)


export_scene()
