from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os
import re
SVG_CATEGORIES = [
    #1-6 doors
    {"color": [224, 62, 155], "isthing": 1, "id": 1, "name": "single door"},
    {"color": [157, 34, 101], "isthing": 1, "id": 2, "name": "double door"},
    {"color": [232, 116, 91], "isthing": 1, "id": 3, "name": "sliding door"},
    {"color": [101, 54, 72], "isthing": 1, "id": 4, "name": "folding door"},
    {"color": [172, 107, 133], "isthing": 1, "id": 5, "name": "revolving door"},
    {"color": [142, 76, 101], "isthing": 1, "id": 6, "name": "rolling door"},
    #7-10 window
    {"color": [96, 78, 245], "isthing": 1, "id": 7, "name": "window"},
    {"color": [26, 2, 219], "isthing": 1, "id": 8, "name": "bay window"},
    {"color": [63, 140, 221], "isthing": 1, "id": 9, "name": "blind window"},
    {"color": [233, 59, 217], "isthing": 1, "id": 10, "name": "opening symbol"},
    #11-27: furniture
    {"color": [122, 181, 145], "isthing": 1, "id": 11, "name": "sofa"},
    {"color": [94, 150, 113], "isthing": 1, "id": 12, "name": "bed"},
    {"color": [66, 107, 81], "isthing": 1, "id": 13, "name": "chair"},
    {"color": [123, 181, 114], "isthing": 1, "id": 14, "name": "table"},
    {"color": [94, 150, 83], "isthing": 1, "id": 15, "name": "TV cabinet"},
    {"color": [66, 107, 59], "isthing": 1, "id": 16, "name": "Wardrobe"},
    {"color": [145, 182, 112], "isthing": 1, "id": 17, "name": "cabinet"},
    {"color": [152, 147, 200], "isthing": 1, "id": 18, "name": "gas stove"},
    {"color": [113, 151, 82], "isthing": 1, "id": 19, "name": "sink"},
    {"color": [112, 103, 178], "isthing": 1, "id": 20, "name": "refrigerator"},
    {"color": [81, 107, 58], "isthing": 1, "id": 21, "name": "airconditioner"},
    {"color": [172, 183, 113], "isthing": 1, "id": 22, "name": "bath"},
    {"color": [141, 152, 83], "isthing": 1, "id": 23, "name": "bath tub"},
    {"color": [80, 72, 147], "isthing": 1, "id": 24, "name": "washing machine"},
    {"color": [100, 108, 59], "isthing": 1, "id": 25, "name": "squat toilet"},
    {"color": [182, 170, 112], "isthing": 1, "id": 26, "name": "urinal"},
    {"color": [238, 124, 162], "isthing": 1, "id": 27, "name": "toilet"},
    #28:stairs
    {"color": [247, 206, 75], "isthing": 1, "id": 28, "name": "stairs"},
    #29-30: equipment
    {"color": [237, 112, 45], "isthing": 1, "id": 29, "name": "elevator"},
    {"color": [233, 59, 46], "isthing": 1, "id": 30, "name": "escalator"},

    #31-35: uncountable
    {"color": [172, 107, 151], "isthing": 0, "id": 31, "name": "row chairs"},
    {"color": [102, 67, 62], "isthing": 0, "id": 32, "name": "parking spot"},
    {"color": [167, 92, 32], "isthing": 0, "id": 33, "name": "wall"},
    {"color": [121, 104, 178], "isthing": 0, "id": 34, "name": "curtain wall"},
    {"color": [64, 52, 105], "isthing": 0, "id": 35, "name": "railing"},
    {"color": [0, 0, 0], "isthing": 0, "id": 36, "name": "bg"},
]
def set_color(semanticId):
    return SVG_CATEGORIES[semanticId]['color']
def svg_reader(svg_path):
    svg_list = list()
    try:
        tree = ET.parse(svg_path)
    except Exception as e:
        print("Read{} failed!".format(svg_path))
        return svg_list
    root = tree.getroot()
    for elem in root.iter():
        line = elem.attrib
        line["tag"] = elem.tag
        svg_list.append(line)
    return svg_list
def svg_writer(svg_list, svg_path):
    for idx, line in enumerate(svg_list):
        tag = line["tag"]
        line.pop("tag")
        if idx == 0:
            root = ET.Element(tag)
            root.attrib = line
        else:
            if "}g" in tag:
                group = ET.SubElement(root, tag)
                group.attrib = line
            else:
                node = ET.SubElement(group, tag)
                node.attrib = line
    prettyxml = BeautifulSoup(ET.tostring(root, "utf-8"), "xml").prettify()
    with open(svg_path, "w") as f:
        f.write(prettyxml)
def cvt_all_color(svg_path,semanticIds, output_dir=None):
    """Convert line color into black to align with other floorplan dataset"""
    tmp = svg_reader(svg_path)
    id=0
    for _, line in enumerate(tmp):
        if "stroke" in line.keys():
            rgb=set_color(semanticIds[id])
            line["stroke"] = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"
            line['semanticId']=str(semanticIds[id])
            id+=1
    svg_writer(tmp, os.path.join(output_dir,svg_path.split('/')[-1]))
def cvt_line_color(svg_path,semanticIds, output_dir=None):
    """Convert line color into black to align with other floorplan dataset"""
    tmp = svg_reader(svg_path)
    id=0
    for _, line in enumerate(tmp):
        if "stroke" in line.keys() and 'semanticId' in line.keys() and 'instanceId' in line.keys():
            rgb=set_color(semanticIds[id])
            line["stroke"] = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"
            line['semanticId']=str(semanticIds[id])
            id+=1
    print(os.path.join(output_dir,svg_path.split('/')[-1]))
    svg_writer(tmp, os.path.join(output_dir,svg_path.split('/')[-1]))

def count_stroke(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()

    elements_with_stroke = root.findall('.//*[@stroke]')
    return len(elements_with_stroke)

def seg1_line(semantic_pred,semantic_gt):
    out=[]
    for idx,gt in enumerate(semantic_gt):
        if gt!=35:
            out.append(semantic_pred[idx])
    return out
def seg2_all(semantic_pred,num):
    return semantic_pred[:num]

colors = [
    x['color']
    for x in SVG_CATEGORIES
]
def onlySeeById(targetIds,ids):
    out = []
    for id in ids:
        if id not in targetIds:
            out.append(35)
        else:
            out.append(id)
    return out
def save(preds,path,outpath):
    

    with open(path) as f:
        fs = f.read()

    i = 0

    st = 0

    while True:
        # print(i)

        st =  fs.find('stroke=', st)
        if st == -1:
            break

        m = re.match(r'stroke=\"[^\"]+\"', fs[st:])
        assert m is not None

        _, delta = m.span()
        ed = st + delta

        r, g, b = colors[preds[i]]
        # s_ins = m.group() # debug
        s_ins = f'stroke="rgb({r},{g},{b})"'
        len_ins = len(s_ins)

        fs = fs[:st] + s_ins + fs[ed:]
        st += len_ins

        i += 1

    with open(outpath, 'w') as f:
        f.write(fs)

# path='/home/jesse/Project/SymPoint/dataset/test/test/svg_gt/0612-0299.svg'
# path='/home/jesse/Project/SymPoint/dataset/test/test/svg_gt/1332-0021.svg'
# out_dir=''
# semantic_pred=[]
# semantic_gt=[]
# #Test1
# semanticIds = seg1_line(semantic_pred,semantic_gt)
# cvt_line_color(path,semanticIds,out_dir)
# #Test2
# stroke_num = count_stroke(path)
# semanticIds=seg2_all(semantic_pred,stroke_num)
# cvt_all_color(path,semanticIds,out_dir)
