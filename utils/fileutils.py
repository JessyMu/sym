def write_svg_json(filename,line_list,circle_list,arc_list,ellipse_list):
    import json
    json_dict={
        "line":line_list,
        "circle":circle_list,
        "arc":arc_list,
        "ellipse":ellipse_list
    }
    with open(f'{filename}.json','w') as writer:
        writer.write(json.dumps(json_dict,indent=4))

def read_json(path):
    import json
    with open(path,'r') as reader:
        return json.loads(reader.read())