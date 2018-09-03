import os
import bpy
import json
import StageBlender
import imp

# Initialize
display = {}

# Display Settings.
display["brainColor"] = [1,1,1]
display["BackgroundColor"] = [0,0,0]
display["axonWidth"] = 20
display["dendWidth"] = 25
display["somaSize"] = 25
display["slicePlaneFlag"] = True

# Stage Blender
imp.reload(StageBlender)
StageBlender.StageSession(os.path.dirname(bpy.context.space_data.text.filepath),display)