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
light1 = IM.CreateLight("Light-BackTopRight",[7,7,7],'SPOT')
#light2 = IM.CreateLight("Light-BackTopLeft",[-7,7,7],'POINT')
#light3 = IM.CreateLight("Light-BackBotLeft",[-7,7,-7],'POINT')
#light4 = IM.CreateLight("Light-BackBotRight",[7,7,-7],'POINT')

#light5 = IM.CreateLight("Light-FrontTopRight",[7,-7,7],'POINT')
#light6 = IM.CreateLight("Light-FrontTopLeft",[-7,-7,7],'POINT')
#light7 = IM.CreateLight("Light-FrontBotLeft",[-7,-7,-7],'POINT')
#light8 = IM.CreateLight("Light-FrontBotRight",[7,-7,-7],'POINT')
