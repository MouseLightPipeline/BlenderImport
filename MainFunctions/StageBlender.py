import bpy
import os
import sys
from math import radians
import imp
import time
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

	# Setup Composite Background.
	# Switch on nodes and get references.
	bpy.data.scenes["Scene"].use_nodes = True
	tree = bpy.context.scene.node_tree

	# clear default nodes
	for node in tree.nodes:
	    tree.nodes.remove(node)
	# Create RGB Background Color Node.
	RGBNode = tree.nodes.new(type="CompositorNodeRGB")
	RGBNode.location = 200,800

	# Create render Layers.
	RenderNode = tree.nodes.new(type="CompositorNodeRLayers")
	RenderNode.location = 200,400

	# Create Alpha Over Node.
	AlphaNode = tree.nodes.new(type="CompositorNodeAlphaOver")
	AlphaNode.location = 400,600
	AlphaNode.use_premultiply = True

	# Create compositer
	CompositeNode = tree.nodes.new(type="CompositorNodeComposite")
	CompositeNode.location = 600,600

	# link nodes
	links = tree.links
	linkRGB = links.new(RGBNode.outputs[0],AlphaNode.inputs[1])
	linkRender = links.new(RenderNode.outputs[0],AlphaNode.inputs[2])
	linkAlpha = links.new(AlphaNode.outputs[0],CompositeNode.inputs[0])

	# Check if background color key excists (for backwards compatibility)
	if "backgroundColor" in display:
		RGBNode.outputs[0].default_value = tuple(display["backgroundColor"]) + (1,)
	else:
		# set to defualt transparency but leave "plumbing" intact.
		links.new(RenderNode.outputs[0],CompositeNode.inputs[0])

	# Brain Mesh.
	#Load (Use Horta OBJs)
	rootObj = IM.HortaObj(folders["meshFolder"], "root")
	rootObj.data.materials.append(rootMat)

	# Import Anatomy
	areas = scene["anatomy"] if isinstance(scene["anatomy"],list) else [scene["anatomy"]]	
	counter = 0
	for area in areas:
		counter = counter+1
		if "acronym" in area:
			print('Area {} of {}'.format(counter,len(areas)))
			obj = IM.HortaObj(folders["meshFolder"], area["acronym"])
			anaCopy = anaMat.copy()
			obj.data.materials.append(anaCopy)
			anaCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(area["color"]) + (1,)
	print("Done!")

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
	counter = 0
	for neuron in neurons:
		counter = counter+1
		start_time = time.time()
		print('Neuron {} of {}'.format(counter,len(neurons)))
		# Axon.
		axFile = os.path.join(folders["swcFolder"],'{0}_axon.swc'.format(neuron["id"]))
		if os.path.isfile(axFile):
			[axon,root] = IM.importSwc(axFile, axBev)
			axCopy = axonMat.copy()
			axon.data.materials.append(axCopy)
			axCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
		# Make sliced axon if requested.
		if display["sliceAxonbyArea"]:
			print("Slicing..")
			for area in areas:
				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.scene.objects.active = None
				if "acronym" in area:
					# new mesh obj.
					axM = axon.to_mesh(bpy.context.scene, False, 'PREVIEW')
					axM = bpy.data.objects.new('{0}_axon_{1}'.format(neuron["id"],area["acronym"]), axM)
					bpy.context.scene.objects.link(axM)
					axM.matrix_world = axon.matrix_world
					# find area
					bpy.ops.object.select_pattern(pattern="Area_%s*" % area["acronym"])
					cArea = bpy.context.selected_objects
					# add boolean
					cBool = axM.modifiers.new(type="BOOLEAN", name="bool area")
					cBool.object = cArea[0]
					cBool.operation = 'INTERSECT'
					# apply boolean.
					bpy.context.scene.objects.active = axM
					bpy.ops.object.modifier_apply(modifier="bool area", apply_as='DATA')
			# Make no area axon.
			axM = axon.to_mesh(bpy.context.scene, False, 'PREVIEW')
			axM = bpy.data.objects.new('{0}_axon_outside'.format(neuron["id"]), axM)
			bpy.context.scene.objects.link(axM)
			bpy.context.scene.objects.unlink(axon)
			axM.name = "%s_axon" % neuron["id"]
			axM.matrix_world = axon.matrix_world
			for area in areas:
				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.scene.objects.active = None
				if "acronym" in area:
					bpy.ops.object.select_pattern(pattern="Area_%s" % area["acronym"])
					cArea = bpy.context.selected_objects
					cBool = axM.modifiers.new(type="BOOLEAN", name="bool area")
					cBool.object = cArea[0]
					cBool.operation = 'DIFFERENCE'
			# apply difference modifiers.
			bpy.ops.object.select_all(action='DESELECT')
			bpy.context.scene.objects.active = axM
			for modifier in axM.modifiers:
				bpy.ops.object.modifier_apply(modifier=modifier.name)

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
		elapsedTime = time.time()-start_time
		print("Elapsed Time: %.2f secs" % elapsedTime)
