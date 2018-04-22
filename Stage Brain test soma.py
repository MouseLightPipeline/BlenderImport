import bpy
import os
import sys
from math import radians
import imp
import numpy
import json
from pprint import pprint

# Current  
scene = json.load(open('C:\\Users\\winnubstj\\Desktop\\Blender\\Scene.json'))

# Folder locations.
mainFolder = "C:\\Users\\winnubstj\\Desktop\\Blender\\"
meshFolder = "Z:\\Allen_compartments\\Horta Obj"
swcFolder = "Z:\\neuronSwcs"

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
bg.inputs[0].default_value[:3] = (0, 0, 0)
bg.inputs[1].default_value = 1.0

# Import materials.
with bpy.data.libraries.load(os.path.join(mainFolder, "Materials","cache.blend")) as (data_from, data_to):
    data_to.materials = data_from.materials
rootMat = bpy.data.materials.get("RootMaterial")
dendMat = bpy.data.materials.get("DendriteMaterial")
axonMat = bpy.data.materials.get("AxonMaterial")
anaMat = bpy.data.materials.get("AnatomyMaterial")

# Create sun light (Position is irrelevant)
sunObj = IM.createLight("SUN","Sun Light",(0,0,7.5),3)

# Brain Mesh.
#Load (Use Horta OBJs)
#rootObj = IM.HortaObj(meshFolder, "root")
#rootObj.data.materials.append(rootMat)
# Create bezier circle for axons.
bpy.ops.curve.primitive_bezier_circle_add()
axBev = bpy.context.active_object
axBev.name = "AxonBevel"
rad = scene["settings"]["axonWidth"]
axBev.scale = ((rad,rad,rad))
axBev.hide =True
axBev.hide_render = True
axBev.select = False
# dendrites.
bpy.ops.curve.primitive_bezier_circle_add()
dendBev = bpy.context.active_object
dendBev.name = "DendBevel"
rad = scene["settings"]["dendWidth"]
dendBev.scale = ((rad,rad,rad))
dendBev.hide =True
dendBev.hide_render = True
dendBev.select = False

# Import SWC
for neuron in scene["neurons"]:
    [axon,root] = IM.importSwc(os.path.join(swcFolder,'{0}_axon.swc'.format(neuron["id"])), axBev)
    axCopy = axonMat.copy()
    axon.data.materials.append(axCopy)
    axCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
    dendFile = os.path.join(swcFolder,'{0}_dendrite.swc'.format(neuron["id"]))
    if os.path.isfile(dendFile):
        [dend,root] = IM.importSwc(dendFile, dendBev)
        dendCopy = dendMat.copy()
        dend.data.materials.append(dendCopy)
        dendCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
    # create soma.
    root = (root[0]/1000,root[2]/1000,root[1]/1000)
    to_origin = ( -5.692, -6.56, 3.972 )
    root = (root[0] + to_origin[0],root[1] + to_origin[1], -root[2] + to_origin[2])
    bpy.ops.mesh.primitive_uv_sphere_add(segments=34,size=20,location=(root[0], root[1], root[2]))
    somaSphere = bpy.context.active_object
    somaSphere.name = neuron["id"] + "_Soma"
    somaSphere.data.materials.append(dendCopy)
    somaSize = scene["settings"]["somaSize"]/1000
    somaSphere.dimensions=((somaSize,somaSize,somaSize))
    somaSphere.data.polygons[0].use_smooth= True
# Import Anatomy
if (len(scene["anatomy"])>1):
    for area in scene["anatomy"]:
        obj = IM.HortaObj(meshFolder, area["acronym"])
        anaCopy = anaMat.copy()
        obj.data.materials.append(anaCopy)
        anaCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(area["color"]) + (1,)
elif len(scene["anatomy"])==1:
    obj = IM.HortaObj(meshFolder, scene["anatomy"]["acronym"])
    anaCopy = anaMat.copy()
    obj.data.materials.append(anaCopy)
    anaCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(scene["anatomy"]["color"]) + (1,)
        
    



