import bpy
import os
import sys
from math import radians
import imp
import time
import json
from pprint import pprint
import ImportBlender as IM
import LegacyStage as legacy

def testBlend():
	print("HELLO!")

def StageSession(sessionFolder,display):
	# check for older blender versions.
	if (2,80,0)> bpy.app.version:
		imp.reload(legacy)
		legacy.StageSession(sessionFolder,display)
		return

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
	bpy.context.scene.render.engine = 'BLENDER_EEVEE'
	bpy.context.scene.render.film_transparent = True
	bpy.context.scene.view_settings.view_transform = 'Standard'

	# Create collections
	neuronCol = bpy.data.collections.new('Neurons')
	bpy.context.scene.collection.children.link(neuronCol)
	if 'Anatomy' not in bpy.data.collections:
		bpy.context.scene.collection.children.link(bpy.data.collections.new('Anatomy'))
	anatomyCol = bpy.data.collections['Anatomy'] 
	if 'Cameras' not in bpy.data.collections:
		bpy.context.scene.collection.children.link(bpy.data.collections.new('Cameras'))
	camCol = bpy.data.collections['Cameras'] 			
	if 'Bevels' not in bpy.data.collections:
		bpy.context.scene.collection.children.link(bpy.data.collections.new('Bevels'))
	bevCol = bpy.data.collections['Bevels'] 		


	# Set world emmission (or lighting)
	world = bpy.data.worlds['World']
	world.use_nodes = True
	bg = world.node_tree.nodes['Background']
	bg.inputs[0].default_value[:3] = (1, 1, 1)
	bg.inputs[1].default_value = 1.0

	# Import materials (if necessary).
	if bpy.data.materials.get("DendriteMaterial") is None:
		with bpy.data.libraries.load(os.path.join(mainFolder, "Materials","cache.blend")) as (data_from, data_to):
			data_to.materials = data_from.materials
	else:
		print("Materials already loaded")	

	# set references.
	rootMat = bpy.data.materials.get("RootMaterial")
	rootMat.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(display["brainColor"]) + (1,)
	dendMat = bpy.data.materials.get("DendriteMaterial")
	anaMat = bpy.data.materials.get("AnatomyMaterial")
	axonMat = bpy.data.materials.get("AxonMaterial")
	rootMat.blend_method = 'BLEND'
	dendMat.blend_method = 'BLEND'
	anaMat.blend_method = 'BLEND'
	axonMat.blend_method = 'BLEND'

	# set group display properties.
	shadeGroup = bpy.data.node_groups ["ShadeGroup"]
	opacityGroup = bpy.data.node_groups ["OpacityGroup"]
	shadeGroup.nodes["ShadeWeight"].inputs[0].default_value = display["shadeWeight"]
	shadeGroup.nodes["ShadeColor"].inputs[0].default_value = tuple(display["shadeColor"]) + (1,)
	opacityGroup.nodes["OpacityValue"].inputs[0].default_value = display["axonOpacity"]
		
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
	bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Anatomy"]
	if "Area_root" not in anatomyCol.objects:
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
			if display["sliceAxonbyArea"]:
				obj.hide_render = True
	print("Done!")

	# create standard materials for slice by area.
	if display["sliceAxonbyArea"]:
		axMatDefault = axonMat.copy()
		axMatDefault.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(display["brainColor"]) + (1,)
		axMatDefault.name = "Mat_Axon"
		dendMatDefault = dendMat.copy()
		dendMatDefault.node_tree.nodes.get("RGB").outputs[0].default_value = tuple([1,0,0]) + (1,)	
		dendMatDefault.name = "Mat_Dend"
		axAreas = {}
		for area in areas:
			axTemp = axonMat.copy()
			axTemp.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(area["color"]) + (1,)
			axTemp.name = "Mat_%s" % area["acronym"]
			axAreas[area["acronym"]]=axTemp

	# Import slice plane
	if display["slicePlaneFlag"]:
		blendfile = os.path.join(mainFolder, "Materials","cache.blend")
		section   = '\\Object\\'
		directory = blendfile + section
		bpy.ops.wm.append(filename='Slice plane', directory=directory)

	# Create Cameras
	bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Cameras"]
	if "Coronal Camera" not in camCol.objects:
		camC = IM.CreateCam("Coronal Camera",[0,-50,0],[radians(90), 0, 0],15)
	if "Sagittal Camera" not in camCol.objects:		
		camS = IM.CreateCam("Sagittal Camera",[-50,0,0],[radians(-90),radians(180), radians(90)],15)
	if "Horizontal Camera" not in camCol.objects:			
		camH = IM.CreateCam("Horizontal Camera",[0,0,50],[0,0, radians(-90)],20)
	if "Oblique Camera" not in camCol.objects:			
		camO = IM.CreateCam("Oblique Camera",[-50,-50,50],[radians(55),0, radians(-45)],20)

	# Create bezier circles
	bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Bevels"]
	# Axons.
	if "AxonBevel" not in bevCol.objects:
		bpy.ops.curve.primitive_bezier_circle_add()
		axBev = bpy.context.active_object
		axBev.name = "AxonBevel"
		axBev.scale = ((display["axonWidth"],display["axonWidth"],display["axonWidth"]))
		axBev.hide_viewport =True
		axBev.hide_render = True
		axBev.select_set(False)
	axBev = bevCol.objects["AxonBevel"]
	# Dendrites.
	if "DendBevel" not in bevCol.objects:		
		bpy.ops.curve.primitive_bezier_circle_add()
		dendBev = bpy.context.active_object
		dendBev.name = "DendBevel"
		dendBev.scale = ((display["dendWidth"],display["dendWidth"],display["dendWidth"]))
		dendBev.hide_viewport =True
		dendBev.hide_render = True
		dendBev.select_set(False)
	dendBev = bevCol.objects["AxonBevel"]		

	# Import SWC
	bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[neuronCol.name]
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
			neuronCol.objects.link(axon)
			bpy.context.scene.collection.objects.unlink(axon)
			if display["sliceAxonbyArea"]:
				axon.data.materials.append(axMatDefault)
			else:
				axCopy = axonMat.copy()
				axon.data.materials.append(axCopy)
				axCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
		else:
			print("Could not find axon file!\n{}".format(axFile))
		# Make sliced axon if requested.
		if display["sliceAxonbyArea"]:
			print("Slicing..")
			for area in areas:
				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.view_layer.objects.active = None
				if "acronym" in area:
					# new mesh obj.
					depsgraph = bpy.context.evaluated_depsgraph_get()
					object_eval = axon.evaluated_get(depsgraph)
					tmpMesh = bpy.data.meshes.new_from_object(object_eval)
					axM = bpy.data.objects.new('{0}_axon_{1}'.format(neuron["id"],area["acronym"]), tmpMesh)
					axObj = neuronCol.objects.link(axM)
					axM.matrix_world = axon.matrix_world
					axM.data.materials[0] = axAreas[area["acronym"]]
					# find area
					bpy.ops.object.select_pattern(pattern="Area_%s*" % area["acronym"])
					cArea = bpy.context.selected_objects
					# add boolean
					cBool = axM.modifiers.new(type="BOOLEAN", name="bool area")
					cBool.object = cArea[0]
					cBool.operation = 'INTERSECT'
					# apply boolean.
					bpy.context.view_layer.objects.active = axM
					bpy.ops.object.modifier_apply(modifier="bool area", apply_as='DATA')
			# Make no area axon.
			depsgraph = bpy.context.evaluated_depsgraph_get()
			object_eval = axon.evaluated_get(depsgraph)
			tmpMesh = bpy.data.meshes.new_from_object(object_eval)
			axM = bpy.data.objects.new('{0}_axon_outside'.format(neuron["id"]), tmpMesh)
			neuronCol.objects.link(axM)
			neuronCol.objects.unlink(axon)
			axM.name = "%s_axon" % neuron["id"]
			axM.matrix_world = axon.matrix_world
			for area in areas:
				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.view_layer.objects.active = None
				if "acronym" in area:
					bpy.ops.object.select_pattern(pattern="Area_%s" % area["acronym"])
					cArea = bpy.context.selected_objects
					cBool = axM.modifiers.new(type="BOOLEAN", name="bool area")
					cBool.object = cArea[0]
					cBool.operation = 'DIFFERENCE'
			# apply difference modifiers.
			bpy.ops.object.select_all(action='DESELECT')
			bpy.context.view_layer.objects.active = axM
			for modifier in axM.modifiers:
				bpy.ops.object.modifier_apply(modifier=modifier.name)

		# Dendrite.
		dendFile = os.path.join(folders["swcFolder"],'{0}_dendrite.swc'.format(neuron["id"]))
		if display["sliceAxonbyArea"]:
			dendCopy = dendMatDefault
		else:
			dendCopy = dendMat.copy()
			dendCopy.node_tree.nodes.get("RGB").outputs[0].default_value = tuple(neuron["color"]) + (1,)
		if os.path.isfile(dendFile):
			[dend,root] = IM.importSwc(dendFile, dendBev)
			neuronCol.objects.link(dend)
			bpy.context.scene.collection.objects.unlink(dend)
			dend.data.materials.append(dendCopy)	
		# Soma.
		soma = IM.createSoma(root,neuron["id"],display["somaSize"])
		soma.data.materials.append(dendCopy)

		elapsedTime = time.time()-start_time
		print("Elapsed Time: %.2f secs" % elapsedTime)
