import bpy
import os
import re
import numpy as np 
from mathutils import Vector
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
	#bpy.ops.transform.resize(value=(0.001,0.001,0.001))
	obj.scale = (0.001, 0.001, 0.001)
	obj.rotation_euler = (radians(-90), 0, 0 )
	obj.location = ( -5.692, -6.56, 3.972 )
	bpy.ops.object.select_all(action='DESELECT')
	obj.select = True
	bpy.context.scene.objects.active = obj
	bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
	bpy.ops.object.select_all(action='DESELECT')
	obj.data.use_auto_smooth = 0
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

def importSwc(filePath, radius):
    # Get file info.
    fileName    = os.path.basename(filePath)
    cFile       = filePath
 
    # Read swc.
    patternHeader   = re.compile("#")           # Header pattern for regexp
    patternValues   = re.compile("[^\t\s]+")    # Value delimiter for regexp
    swc             = []
    f = open(cFile)
    for line in f:
        line = line.rstrip()    # remove newline character.
        # Check for comments.
        header = patternHeader.findall(line)
        if not header:
            values = np.array(patternValues.findall(line))
            swc.append(values)
    swc         = np.array(swc)
    swc         = swc.astype(float)
    # Walk through Tree.
    nodeList    = swc[:,0]
    drawnList   = []    # Holds list of nodes already drawn.
    nNodes      = len(swc)
    nodeCounter = 0
    pathCounter = 0
    paths       = np.hstack((swc[0,2:5],1)) # Holds all paths (3d is path number)
    while nodeCounter<nNodes-1:
        nodeCounter = nodeCounter+1
        # check if we already did this node.
        if not nodeCounter in drawnList:
            # start new path.
            pathCounter = pathCounter + 1
            # add branch point (if it isnt root).
            indPrev     = swc[nodeCounter-1,6].astype(int).item(0)
            if indPrev>0:
                entry = np.hstack((swc[indPrev-1,2:5],pathCounter))
                paths = np.vstack((paths,entry))
                drawnList.append(indPrev)
            # Loop while there is a next point on the path
            nextPoint   = nodeCounter
            while nextPoint>0:
                # add current point.bpy.ops.mesh.primitive_uv_sphere_add
                cPoint      = nextPoint
                if cPoint>1:
                    entry = np.hstack((swc[cPoint-1,2:5],pathCounter))
                    paths = np.vstack((paths,entry))
                drawnList.append(cPoint)
                # Attempt to find next point.
                nextPoint   = swc[np.where(swc[:,6]==cPoint),0]
                # If there are multiple paths pick first.
                if nextPoint.shape[1]>0:
                    nextPoint   = nextPoint[0].astype(int).item(0)
                # If there are no more nodes to then flag next path.
                else:
                    nextPoint = 0
 	# actually start building shape here.
    # Generate paths.
    nPaths = paths[:,3].max().astype(int)
    for iPath in range(1,nPaths+1):
        # Collect nodes current path.
        ind   = np.where( paths[:,3]==iPath )
        nodes = paths[ind,0:3].squeeze(0)
        # Create object
        w = 1 # weight
        curvedata = bpy.data.curves.new(name='Curve', type='CURVE')
        curvedata.dimensions = '3D'
 
        objectdata = bpy.data.objects.new(fileName + "Curve", curvedata)
        objectdata.location = (0,0,0) #object origin
        objectdata.data.fill_mode           = 'FULL'
        objectdata.data.bevel_depth         = radius
        objectdata.data.bevel_resolution    = 4
        objectdata.scale=((0.001,0.001,0.001))
        objectdata.location = ( -5.692, -6.56, 3.972 )
        objectdata.rotation_euler = (radians(-90), 0, 0 )

        bpy.context.scene.objects.link(objectdata)
 
        polyline = curvedata.splines.new('POLY')
        polyline.points.add(nodes.shape[0]-1)
         
        # First sphere
        values = [nodes[0,0].astype(float).item(0), nodes[0,1].astype(float).item(0), nodes[0,2].astype(float).item(0)]
 #       bpy.ops.mesh.primitive_uv_sphere_add(segments=34,size=objectdata.data.bevel_depth/1000,location=(values[0]/1000, values[1]/1000, values[2]/1000))
 #       rootSphere = bpy.context.selected_objects
 #       bpy.context.active_object.name = fileName + "Sphere"
 #       endCap = bpy.context.object
 #       setMaterial(endCap, materialObj)
 #       endCap = bpy.context.object
 #       for p in endCap.data.polygons:
 #           p.use_smooth = True
        polyline.points[0].co = (values[0], values[1], values[2], 1)
        for iNode in range(1,nodes.shape[0]):
        	values = [nodes[iNode,0].astype(float).item(0), nodes[iNode,1].astype(float).item(0), nodes[iNode,2].astype(float).item(0)]
        	polyline.points[iNode].co = (values[0], values[1], values[2], 1)
 #       # add sphere.
 #       bpy.ops.object.select_all(action='DESELECT')
 #       rootSphere[0].select = True
 #       bpy.ops.object.duplicate(linked=True)
 #       bpy.context.object.location = (values[0]/1000, values[1]/1000, values[2]/1000)
 #       bpy.context.active_object.name = fileName + "Sphere"
# Join together.


    bpy.ops.object.select_pattern(pattern=fileName+"Curve*")
    bpy.context.scene.objects.active = objectdata
    bpy.ops.object.join()
    objectdata.name = fileName
    objectdata.select = False
     
    # Group together.
    bpy.ops.object.select_pattern(pattern=fileName+"*")
    # Apply transform.
    bpy.context.scene.objects.active = objectdata
    bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
    bpy.ops.object.select_all(action='DESELECT')
