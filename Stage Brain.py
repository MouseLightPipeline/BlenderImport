import bpy
import os
import sys
from math import radians
import imp

mainFolder = "C:\\Users\\winnubstj\\Desktop\\Blender\\"
meshFolder = "Z:\\Allen_compartments\\Horta Obj"

# Get custom functions.
sys.path.append(os.path.join(mainFolder, "MainFunctions"))
import ImportBlender as IM
imp.reload(IM) # So you can change script on the fly.

# Set Cycles Render.
bpy.context.scene.render.engine = 'CYCLES'

# Set world emmission (or lighting)
world = bpy.data.worlds['World']
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs[0].default_value[:3] = (1, 1, 1)
bg.inputs[1].default_value = 1.0

# Brain Mesh.
#Load (Use Horta OBJs)
rootObj = IM.HortaObj(os.path.join(meshFolder, "root_997.obj"))

# Create Cameras
#camC = IM.CreateCam("Coronal Camera",[0,-50,0],[radians(90), 0, 0],15)
#camS = IM.CreateCam("Sagittal Camera",[50,0,0],[radians(90),0, radians(90)],15)
#camH = IM.CreateCam("Horizontal Camera",[0,0,50],[0,0, radians(-180)],15)


