import bpy
import os
import sys
from math import radians
import imp
import json
from pprint import pprint

# Current  
scene = json.load(open('C:\\Users\\winnubstj\\Desktop\\Blender\\Scene.json'))

# Folder locations.
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
axonMat = bpy.data.materials.get("AxonMaterial")
anaMat = bpy.data.materials.get("AnatomyMaterial")

# Brain Mesh.
#Load (Use Horta OBJs)
rootObj = IM.HortaObj(meshFolder, "root")
rootObj.data.materials.append(rootMat)

# Create Cameras
camC = IM.CreateCam("Coronal Camera",[0,-50,0],[radians(90), 0, 0],15)
camS = IM.CreateCam("Sagittal Camera",[50,0,0],[radians(90),0, radians(90)],15)
camH = IM.CreateCam("Horizontal Camera",[0,0,50],[0,0, radians(-180)],15)

# Create bezier circle for axons.
bpy.ops.curve.primitive_bezier_circle_add()
axBev = bpy.context.active_object
axBev.name = "AxonBevel"
rad = scene["settings"][0]["axonWidth"]
axBev.scale = ((rad,rad,rad))
axBev.hide =True
axBev.hide_render = True
axBev.select = False
# dendrites.
bpy.ops.curve.primitive_bezier_circle_add()
dendBev = bpy.context.active_object
dendBev.name = "DendBevel"
rad = scene["settings"][0]["dendWidth"]
dendBev.scale = ((rad,rad,rad))
dendBev.hide =True
dendBev.hide_render = True
dendBev.select = False

# Import SWC
for neuron in scene["neurons"]:
    axon = IM.importSwc(os.path.join(swcFolder,'{0}_axon.swc'.format(neuron["id"])), axBev)
    axCopy = axonMat.copy()
    axon.data.materials.append(axCopy)
    axCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
    dend = IM.importSwc(os.path.join(swcFolder,'{0}_dendrite.swc'.format(neuron["id"])), dendBev)
    dendCopy = dendMat.copy()
    dend.data.materials.append(dendCopy)
    dendCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
    
# Import Anatomy
for area in scene["anatomy"]:
    obj = IM.HortaObj(meshFolder, area["acronym"])
    anaCopy = anaMat.copy()
    obj.data.materials.append(anaCopy)
    anaCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(area["color"]) + (1,)
    
    



