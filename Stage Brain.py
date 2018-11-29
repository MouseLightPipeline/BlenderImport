import os
import bpy
import json
import StageBlender
import imp

# Initialize
display = {}

# Display Settings.
display["brainColor"] = [1,1,1]
display["backgroundColor"] = [0,0,0]
display["shadeWeight"] = 0
display["shadeColor"] = [1,1,1]
display["axonOpacity"] = 1
display["axonWidth"] = 20
display["dendWidth"] = 25
display["somaSize"] = 25
display["slicePlaneFlag"] = False
display["sliceAxonbyArea"] = True

# Stage Blender
imp.reload(StageBlender)
StageBlender.StageSession(os.path.dirname(bpy.context.space_data.text.filepath),display)