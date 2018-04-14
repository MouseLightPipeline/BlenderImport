import bpy
import os
import sys
from math import radians
def HortaObj(fileLoc):
	print("HELLO!")
	# Brain Mesh.
	#Load (Use Horta OBJs)
	bpy.ops.import_scene.obj(filepath=fileLoc)
	obj= bpy.context.selected_objects[0]
	obj = bpy.data.objects[obj.name]
	#scale
	#bpy.ops.transform.resize(value=(0.001,0.001,0.001))
	obj.scale = (0.001, 0.001, 0.001)
	obj.rotation_euler = (radians(-90), 0, 0 )
	obj.location = ( -5.692, -6.56, 3.972 )
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj
	bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
	bpy.ops.object.select_all(action='DESELECT')
	obj.data.use_auto_smooth = 0
	return obj

def CreateCam(name,pos,rot,scale):
	bpy.ops.object.camera_add(view_align=False,
                          location=pos,
                          rotation=rot)
	cam = bpy.context.object
	cam.name = name
	cam.data.type = 'ORTHO'
	cam.data.ortho_scale = scale
	return cam

def CreateLight(nameLight,pos,typeLight):
	scene = bpy.context.scene
	bpy.ops.object.lamp_add(type='AREA')
	obj= bpy.context.selected_objects[0]
	obj = bpy.data.lamps[obj.name]
	obj.node_tree.nodes["Emission"].inputs[0].default_value =(1,0,0,1)
	return obj
	# Create new lamp datablock
	#lamp_data = bpy.data.lamps.new(name=nameLight, type=typeLight)

	# Create new object with our lamp datablock
	#lamp_object = bpy.data.objects.new(name=nameLight, object_data=lamp_data)

	# Link lamp object to the scene so it'll appear in this scene
	#scene.objects.link(lamp_object)

	# Place lamp to a specified location
	#lamp_object.location = pos
	#return lamp_object

