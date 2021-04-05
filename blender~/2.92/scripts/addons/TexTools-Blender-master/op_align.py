import bpy
import bmesh
import operator
from mathutils import Vector
from collections import defaultdict
from math import pi, sqrt

from . import utilities_uv



class op(bpy.types.Operator):
	bl_idname = "uv.textools_align"
	bl_label = "Align"
	bl_description = "Align vertices, edges or shells"
	bl_options = {'REGISTER', 'UNDO'}
	
	direction : bpy.props.StringProperty(name="Direction", default="top")

	@classmethod
	def poll(cls, context):
		if not bpy.context.active_object:
			return False

		#Only in Edit mode
		if bpy.context.active_object.mode != 'EDIT':
			return False

		#Only in UV editor mode
		if bpy.context.area.type != 'IMAGE_EDITOR':
			return False
		
		#Requires UV map
		if not bpy.context.object.data.uv_layers:
			return False

		# Not in Synced mode
		if bpy.context.scene.tool_settings.use_uv_select_sync:
			return False

		return True


	def execute(self, context):
		align_mode = bpy.context.scene.texToolsSettings.align_mode

		if align_mode == 'SELECTION':
			all_ob_bounds = utilities_uv.multi_object_loop(utilities_uv.getSelectionBBox, need_results=True)

			select = False
			for ob_bounds in all_ob_bounds:
				if len(ob_bounds) > 0 :
					select = True
					break
			if not select:
				return {'CANCELLED'}

			boundsAll = utilities_uv.getMultiObjectSelectionBBox(all_ob_bounds)

			utilities_uv.multi_object_loop(align, context, align_mode, self.direction, boundsAll=boundsAll)
		
		else:
			utilities_uv.multi_object_loop(align, context, align_mode, self.direction)
		
		return {'FINISHED'}


def align(context, align_mode, direction, boundsAll={}):

	prepivot = bpy.context.space_data.pivot_point
	bpy.context.space_data.pivot_point = 'CURSOR'

	obj = bpy.context.active_object
	bm = bmesh.from_edit_mesh(obj.data)
	uv_layers = bm.loops.layers.uv.verify()

	if align_mode == 'SELECTION':
		center_all = boundsAll['center']
	elif align_mode == 'CURSOR':
		cursor = Vector(bpy.context.space_data.cursor_location.copy())
		center_all = boundsAll['min'] = boundsAll['max'] = cursor
	else:	#CANVAS
		if direction == "bottom" or direction == "left" or direction == "bottomleft":
			center_all = boundsAll['min'] = boundsAll['max'] = Vector((0.0, 0.0))
		elif direction == "top" or direction == "topleft":
			center_all = boundsAll['min'] = boundsAll['max'] = Vector((0.0, 1.0))
		elif direction == "right" or direction == "topright":
			center_all = boundsAll['min'] = boundsAll['max'] = Vector((1.0, 1.0))
		elif direction == "bottomright":
			center_all = boundsAll['min'] = boundsAll['max'] = Vector((1.0, 0.0))
		elif direction == "horizontal" or direction == "vertical" or direction == "center":
			center_all = boundsAll['min'] = boundsAll['max'] = Vector((0.5, 0.5))

	selection_mode = bpy.context.scene.tool_settings.uv_select_mode
	if selection_mode == 'FACE' or selection_mode == 'ISLAND':
		#Collect UV islands
		islands = utilities_uv.getSelectionIslands()

		for island in islands:
			bounds = utilities_uv.get_island_BBOX(island)
			center = bounds['center']

			if direction == "bottom":
				delta = boundsAll['min'] - bounds['min'] 				
				utilities_uv.move_island(island, 0, delta.y)
			
			elif direction == "top":
				delta = boundsAll['max'] - bounds['max']
				utilities_uv.move_island(island, 0, delta.y)
			
			elif direction == "left":
				delta = boundsAll['min'] - bounds['min'] 
				utilities_uv.move_island(island, delta.x, 0)
			
			elif direction == "right":
				delta = boundsAll['max'] - bounds['max']
				utilities_uv.move_island(island, delta.x, 0)
			
			elif direction == "center":
				delta = Vector((center_all - center))
				utilities_uv.move_island(island, delta.x, delta.y)
			
			elif direction == "horizontal":
				delta = Vector((center_all - center))
				utilities_uv.move_island(island, 0, delta.y)
			
			elif direction == "vertical":
				delta = Vector((center_all - center))
				utilities_uv.move_island(island, delta.x, 0)	

			elif direction == "bottomleft":
				delta = boundsAll['min'] - bounds['min']
				utilities_uv.move_island(island, delta.x, delta.y)

			elif direction == "topright":
				delta = boundsAll['max'] - bounds['max']
				utilities_uv.move_island(island, delta.x, delta.y)

			elif direction == "topleft":
				delta_x = boundsAll['min'] - bounds['min']
				delta_y = boundsAll['max'] - bounds['max']
				utilities_uv.move_island(island, delta_x.x, delta_y.y)

			elif direction == "bottomright":
				delta_x = boundsAll['max'] - bounds['max']
				delta_y = boundsAll['min'] - bounds['min']
				utilities_uv.move_island(island, delta_x.x, delta_y.y)
			
			else:
				print("Unknown direction: "+str(direction))


	elif selection_mode == 'EDGE' or selection_mode == 'VERTEX':
		for f in bm.faces:
			if f.select:
				for l in f.loops:
					luv = l[uv_layers]
					if luv.select:
						# print("Idx: "+str(luv.uv))
						if direction == "top":
							luv.uv[1] = boundsAll['max'].y
						elif direction == "bottom":
							luv.uv[1] = boundsAll['min'].y
						elif direction == "left":
							luv.uv[0] = boundsAll['min'].x
						elif direction == "right":
							luv.uv[0] = boundsAll['max'].x
						elif direction == "center":
							luv.uv[0] = center_all.x
							luv.uv[1] = center_all.y
						elif direction == "horizontal":
							luv.uv[1] = center_all.y
						elif direction == "vertical":
							luv.uv[0] = center_all.x
						elif direction == "bottomleft":
							luv.uv[0] = boundsAll['min'].x
							luv.uv[1] = boundsAll['min'].y
						elif direction == "topright":
							luv.uv[0] = boundsAll['max'].x
							luv.uv[1] = boundsAll['max'].y
						elif direction == "topleft":
							luv.uv[0] = boundsAll['min'].x
							luv.uv[1] = boundsAll['max'].y
						elif direction == "bottomright":
							luv.uv[0] = boundsAll['max'].x
							luv.uv[1] = boundsAll['min'].y
						else:
							print("Unknown direction: "+str(direction))

		bmesh.update_edit_mesh(obj.data)

	bpy.context.space_data.pivot_point = prepivot


bpy.utils.register_class(op)
