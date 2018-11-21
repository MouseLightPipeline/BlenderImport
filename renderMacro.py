import bpy
import os

def RenderObj(pattern,hide):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="%s*" % pattern)
    obs = bpy.context.selected_objects
    for ob in obs:
        ob.hide_render = hide
        
neuronList = []
areas = ["root"]
outputFolder = os.path.join(os.path.dirname(bpy.context.space_data.text.filepath),"renders")

# Get Neuronlist.
bpy.ops.object.select_pattern(pattern="AA*")
neurons = bpy.context.selected_objects
neuronList = []
for neuron in neurons:
    neuronList = neuronList + [neuron.name[0:6]]
neuronList = list(set(neuronList))    
print(neuronList)

# generate output dir.
if os.path.isdir(outputFolder)==False:
    os.makedirs(outputFolder)

# Turn off all objects.
RenderObj("*",True)

# turn on areas.
for area in areas:
    print(area)
    RenderObj("Area_%s*" % area,False)
    
# Go through neurons.
count = 0
for neuron in neuronList:
    count =count+1
    print("Neuron [%i\\%i]" % (count, len(neuronList)))
    # Turn on neuron
    RenderObj("%s*" % neuron,False)
    # Render
    bpy.context.scene.render.filepath = os.path.join(outputFolder,"%s.png" % neuron)
    bpy.ops.render.render( write_still=True )
    # Turn off neuron
    RenderObj("%s*" % neuron,True)