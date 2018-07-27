import json
import StageBlender
import imp

# Initialize
display = {}
folders = {}

# Current Session
sessionFile = 'C:\\Users\\winnubstj\\Desktop\\Blender test\\session1.json'

# Display Settings.
display["brainColor"] = [1,1,1]
display["axonWidth"] = 20
display["dendWidth"] = 25
display["somaSize"] = 25
display["slicePlaneFlag"] = True

# Folder locations.
folders["meshFolder"] = "Z:\\Allen_compartments\\Horta Obj"
folders["swcFolder"] = "Z:\\neuronSwcs\\"

# Stage Blender
imp.reload(StageBlender)
StageBlender.StageSession(json.load(open(sessionFile)),display,folders)