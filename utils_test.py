import json
import random
def read_json(path):
    with open(path,'r') as reader:
        return json.loads(reader.read())
    

def write_json(path,data):
    with open(path,'w') as writer:
        writer.write(json.dumps(data,indent=4))

path='/home/jesse/Project/SymPoint/dataset/temp/jsons/1323-0004.json'
outpath='/home/jesse/Project/SymPoint/dataset/temp_random/jsons/1323-0004.json'
data = read_json(path)
for key,value in data.items():
    if key=='args' or key=='lengths'  or key == 'commands':
        continue
    if key == 'widths':
        # pass
        data[key]=[2]*len(data[key])
    if key!='width' and key!='height':
        random.shuffle(data[key])
write_json(outpath,data)
'''
commands
args
lengths
semanticIds
instanceIds
width
height
obj_cts
boxes
rgb
layerIds
widths
'''