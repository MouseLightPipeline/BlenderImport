import bpy
import os
import sys
from math import radians
import imp

mainFolder = "C:\\Users\\winnubstj\\Desktop\\Blender\\"
meshFolder = "Z:\\Allen_compartments\\Horta Obj"
swcFolder = "Z:\\for jayaram"

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

# Import materials.
with bpy.data.libraries.load(os.path.join(mainFolder, "Materials","cache.blend")) as (data_from, data_to):
    data_to.materials = data_from.materials
rootMat = bpy.data.materials.get("RootMaterial")
dendMat = bpy.data.materials.get("DendriteMaterial")

# Brain Mesh.
#Load (Use Horta OBJs)
rootObj = IM.HortaObj(os.path.join(meshFolder, "root_997.obj"))
rootObj.data.materials.append(rootMat)

# Create Cameras
camC = IM.CreateCam("Coronal Camera",[0,-50,0],[radians(90), 0, 0],15)
#camS = IM.CreateCam("Sagittal Camera",[50,0,0],[radians(90),0, radians(90)],15)
#camH = IM.CreateCam("Horizontal Camera",[0,0,50],[0,0, radians(-180)],15)

# Create bezier circle for axons.
bpy.ops.curve.primitive_bezier_circle_add()
axBev = bpy.context.active_object
axBev.name = "AxonBevel"
axBev.scale = ((10,10,10))
axBev.select = False
# dendrites.
bpy.ops.curve.primitive_bezier_circle_add()
dendBev = bpy.context.active_object
dendBev.name = "DendBevel"
dendBev.scale = ((15,15,15))
dendBev.select = False

# Import SWC
axon1 = IM.importSwc(os.path.join(swcFolder,"AA0227_axon.swc"), axBev)
dend1 = IM.importSwc(os.path.join(swcFolder,"AA0227_dendrite.swc"), dendBev)
dend1.data.materials.append(dendMat)




