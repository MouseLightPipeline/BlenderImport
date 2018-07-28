import bpy
import os
import sys
from math import radians
import imp
import json
from pprint import pprint
import ImportBlender as IM

def testBlend():
	print("HELLO!")

def StageSession(sessionFolder,display):
	print("Im here!")
	# Get main repo folder.
	mainFolder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

	# set folders
	folders = {}
	folders["meshFolder"] = os.path.join(sessionFolder,"meshes")
	folders["swcFolder"] = os.path.join(sessionFolder,"swcs")
	# Load scene info.
	scene = json.load(open(os.path.join(sessionFolder,'session_info.json')))
	imp.reload(IM) # So you can change script on the fly.

	# Set Cycles Render.
	bpy.context.scene.render.engine = 'CYCLES'
	bpy.context.scene.cycles.film_transparent = True # set transparency for easy background change

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
	rootMat.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(display["brainColor"]) + (1,)
	dendMat = bpy.data.materials.get("DendriteMaterial")
	axonMat = bpy.data.materials.get("AxonMaterial")
	anaMat = bpy.data.materials.get("AnatomyMaterial")

	# Brain Mesh.
	#Load (Use Horta OBJs)
	rootObj = IM.HortaObj(folders["meshFolder"], "root")
	rootObj.data.materials.append(rootMat)

	# Import slice plane
	if display["slicePlaneFlag"]:
		blendfile = os.path.join(mainFolder, "Materials","cache.blend")
		section   = '\\Object\\'
		directory = blendfile + section
		bpy.ops.wm.append(filename='Slice plane', directory=directory)

	# Create Cameras
	camC = IM.CreateCam("Coronal Camera",[0,-50,0],[radians(90), 0, 0],15)
	camS = IM.CreateCam("Sagittal Camera",[-50,0,0],[radians(-90),radians(180), radians(90)],15)
	camH = IM.CreateCam("Horizontal Camera",[0,0,50],[0,0, radians(-90)],20)
	camO = IM.CreateCam("ObliqueCamera",[-50,-50,50],[radians(55),0, radians(-45)],20)

	# Create bezier circles
	# Axons.
	bpy.ops.curve.primitive_bezier_circle_add()
	axBev = bpy.context.active_object
	axBev.name = "AxonBevel"
	axBev.scale = ((display["axonWidth"],display["axonWidth"],display["axonWidth"]))
	axBev.hide =True
	axBev.hide_render = True
	axBev.select = False
	# Dendrites.
	bpy.ops.curve.primitive_bezier_circle_add()
	dendBev = bpy.context.active_object
	dendBev.name = "DendBevel"
	dendBev.scale = ((display["dendWidth"],display["dendWidth"],display["dendWidth"]))
	dendBev.hide =True
	dendBev.hide_render = True
	dendBev.select = False

	# Import SWC
	neurons = scene["neurons"] if isinstance(scene["neurons"],list) else [scene["neurons"]]
	areas = scene["anatomy"] if isinstance(scene["anatomy"],list) else [scene["anatomy"]]
	counter = 0
	for neuron in neurons:
		counter = counter+1
		print('Neuron {} of {}'.format(counter,len(neurons)))
		# Axon.
		axFile = os.path.join(folders["swcFolder"],'{0}_axon.swc'.format(neuron["id"]))
		if os.path.isfile(axFile):
			[axon,root] = IM.importSwc(axFile, axBev)
			axCopy = axonMat.copy()
			axon.data.materials.append(axCopy)
			axCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
		# Dendrite.
		dendFile = os.path.join(folders["swcFolder"],'{0}_dendrite.swc'.format(neuron["id"]))
		if os.path.isfile(dendFile):
			[dend,root] = IM.importSwc(dendFile, dendBev)
			dendCopy = axonMat.copy()
			dend.data.materials.append(dendCopy)
			dendCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
		# Soma.
		soma = IM.createSoma(root,neuron["id"],display["somaSize"])
		soma.data.materials.append(dendCopy)
		
	# Import Anatomy
	counter = 0
	for area in areas:
		counter = counter+1
		print('Area {} of {}'.format(counter,len(areas)))
		obj = IM.HortaObj(folders["meshFolder"], area["acronym"])
		anaCopy = anaMat.copy()
		obj.data.materials.append(anaCopy)
		anaCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(area["color"]) + (1,)

	print("Done!")



