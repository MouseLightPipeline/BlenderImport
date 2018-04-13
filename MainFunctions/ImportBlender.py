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
	obj.scale = (0.001, 0.001, 0.001)
	obj.rotation_euler = (radians(-90), 0, 0 )
	obj.location = ( -5.692, -6.56, 3.972 )
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