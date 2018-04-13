import bpy
import os
import sys
from math import radians
import imp

mainFolder = "C:\\Users\\winnubstj\\Desktop\\Blender\\MainFunctions"
meshFolder = "Z:\\Allen_compartments\\Horta Obj"

# Get custom functions.
sys.path.append(mainFolder)
import ImportBlender as IM
imp.reload(IM) # So you can change script on the fly.

# Set Cycles Render.
bpy.context.scene.render.engine = 'CYCLES'

# Brain Mesh.
#Load (Use Horta OBJs)
rootObj = IM.HortaObj(os.path.join(meshFolder, "root_997.obj"))

# Create Cameras
camC = IM.CreateCam("Coronal Camera",[0,-50,0],[radians(90), 0, 0],15)
camS = IM.CreateCam("Sagittal Camera",[50,0,0],[radians(90),0, radians(90)],15)
camH = IM.CreateCam("Horizontal Camera",[0,0,50],[0,0, radians(-180)],15)
# Create Lights
IM.CreateLight("BackTopRight",[7,7,15],'POINT')