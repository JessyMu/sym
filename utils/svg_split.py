
# svg分块，并且删除不在区域内坐标，并且修改坐标始终保持参考系为0，0
def svg_parse(x,y,h,w,filepath):
    '''
    解析svg中x-x+h,y-y+w区域内的元素
    '''
    import xml.etree.ElementTree as ET
    from svgpathtools import parse_path

    tree = ET.parse(filepath)
    root = tree.getroot()

    xrange=[x,x+w]
    yrange=[y,y+h]
    

    line_list=[]
    arc_list=[]
    circle_list=[]
    ellipse_list=[]
    layerId=0
    ns = root.tag[:-3]
    for g in root.iter(ns + 'g'):
        layerId+=1
        for path in g.iter(ns + 'path'):
            try:
                path_repre = parse_path(path.attrib['d'])
                startpoint = path_repre.point(0)
                endpoint = path_repre.point(1)
                path_type = path_repre[0].__class__.__name__
                if path_type=='Line' and xrange[0]<=startpoint.real<=xrange[1] and yrange[0]<=startpoint.imag<=yrange[1]:
                    data={
                        'layer':str(layerId),
                        'sx':startpoint.real,
                        'sy':startpoint.imag,
                        'ex':endpoint.real,
                        'ey':endpoint.imag
                    }
                    line_list.append(data)
                elif path_type=='Arc' and xrange[0]<=startpoint.real<=xrange[1] and yrange[0]<=startpoint.imag<=yrange[1]:
                    # print(path_repre)
                    data={
                        'layer':str(layerId),
                        'sx':startpoint.real,
                        'sy':startpoint.imag,
                        'r':path_repre[0].radius.real,
                        # 'angle':1 if path_repre[0].large_arc else 0,
                        'isLarge':path_repre[0].large_arc,
                        'isSweep':path_repre[0].sweep,
                        'ex':endpoint.real,
                        'ey':endpoint.imag
                    }
                    arc_list.append(data)
            except Exception as e:
                raise RuntimeError("Parse path failed!")

        for circle in g.iter(ns + 'circle'):
            try:
                cx = float(circle.attrib['cx'])
                cy = float(circle.attrib['cy'])
                r = float(circle.attrib['r'])
                if xrange[0]<=cx<=xrange[1] and yrange[0]<=cy<=yrange[1]:
                    data = {
                        'layer':str(layerId),
                        'cx':cx,
                        'cy':cy,
                        'r':r
                    }
                    circle_list.append(data)
            except Exception as e:
                raise RuntimeError("Parse path failed!")
            
        for ellipse in g.iter(ns + 'ellipse'):
            try:
                cx = float(ellipse.attrib['cx'])
                cy = float(ellipse.attrib['cy'])
                rx = float(ellipse.attrib['rx'])
                ry = float(ellipse.attrib['ry'])
                if xrange[0]<=cx<=xrange[1] and yrange[0]<=cy<=yrange[1]:
                    data = {
                        'layer':str(layerId),
                        'cx':cx,
                        'cy':cy,
                        'rx':rx,
                        'ry':ry
                    }
                    ellipse_list.append(data)
            except Exception as e:
                raise RuntimeError("Parse path failed!")
    return line_list,arc_list,circle_list,ellipse_list

def move(mx,my,dx,dy,line_list,arc_list,circle_list,ellipse_list):
    for line in line_list:
        line['sx']=line['sx']/dx+mx
        line['sy']=line['sy']/dy+my
        line['ex']=line['ex']/dx+mx
        line['ey']=line['ey']/dy+my
    for arc in arc_list:
        arc['sx']=arc['sx']/dx+mx
        arc['sy']=arc['sy']/dy+my
        arc['ex']=arc['ex']/dx+mx
        arc['ey']=arc['ey']/dy+my
        arc['r']=arc['r']/dx
    for circle in circle_list:
        circle['cx']=circle['cx']/dx+mx
        circle['cy']=circle['cy']/dy+my
        circle['r'] = circle['r']/dx
    for ellipse in ellipse_list:
        ellipse['cx']=ellipse['cx']/dx+mx
        ellipse['cy']=ellipse['cy']/dy+my
    return line_list,arc_list,circle_list,ellipse_list

def svg_combin(input_dir,h,w):
    import os
    filelist = os.listdir(input_dir)
    
    line_list=[]
    arc_list=[]
    circle_list=[]
    ellipse_list=[]

    for file in filelist:
        coord = file.replace('.svg','').split('_')
        lines,arcs,circles,ellipses = svg_parse(0,0,h,w,os.path.join(dir,file))
        lines,arcs,circles,ellipses = move(int(coord[0]),int(coord[1]),lines,arcs,circles,ellipses)
        line_list.extend(lines)
        arc_list.extend(arcs)
        circle_list.extend(circles)
        ellipse_list.extend(ellipses)
    return line_list,arc_list,circle_list,ellipse_list

def svg_write(outpath,targetH,targetW,line_list,arc_list,circle_list,ellipse_list):
    import svgwrite
    from collections import defaultdict
    dwg = svgwrite.Drawing(outpath, viewBox=f'0 0 {targetH} {targetW}')
    svg_list = defaultdict(list)
    for item in line_list:
        if item['sx']==item['ex'] and item['sy']==item['ey']:
            continue
        line = dwg.path(
            d=f"M {item['sx']},{item['sy']} L {item['ex']},{item['ey']}",
            fill="none",
            stroke="black",
        )
        line['stroke-width']='0.1'
        # svg_list[item["layer"]].append(line)
        svg_list["layer"].append(line)
    for item in circle_list:
        if item['r'] == 0:
            continue
        circle = dwg.circle(
            center=(item["cx"], item["cy"]),
            r=item["r"],
            fill="none",
            stroke="black",
        )
        circle['stroke-width']='0.1'
        # svg_list[item["layer"]].append(circle)
        svg_list["layer"].append(circle)
    for item in ellipse_list:
        if item['rx'] or item['ry']:
            continue
        ellipse = dwg.ellipse(
            center=(item["cx"], item["cy"]),
            r=(item["rx"], item["ry"]),
            fill="none",
            stroke="black",
        )
        ellipse['stroke-width']='0.1'
        # svg_list[item["layer"]].append(ellipse)
        svg_list["layer"].append(ellipse)
    for item in arc_list:
        if item['sx']==item['ex'] and item['sy']==item['ey']:
            continue
        arc = dwg.path(
            # d=f"M {item['sx']},{item['sy']} A {item['r']},{item['r']} 0 {1 if item['angle']>180 else 0} 0 {item['ex']},{item['ey']}",
            d=f"M {item['sx']},{item['sy']} A {item['r']},{item['r']} 0 {1 if item['isLarge'] else 0} {1 if item['isSweep'] else 0} {item['ex']},{item['ey']}",
            fill="none",
            stroke="black",
        )
        arc['stroke-width']='0.1'
        # svg_list[item["layer"]].append(arc)
        svg_list["layer"].append(arc)
    for item in svg_list.items():
        g = dwg.g()
        for elem in item[1]:
            g.add(elem)
        dwg.add(g)
    dwg.save()

def get_minmax(line_list,arc_list,circle_list,ellipse_list):
    xmin=line_list[0]['ex']
    xmax=line_list[0]['ex']
    ymin=line_list[0]['ey']
    ymax=line_list[0]['ey']
    for line in line_list:
        if xmin>min(line['ex'],line['sx']):
            xmin=min(line['ex'],line['sx'])
        if xmax<max(line['ex'],line['sx']):
            xmax=max(line['ex'],line['sx'])
        if ymin>min(line['ey'],line['sy']):
            xmin=min(line['ey'],line['sy'])
        if ymax<max(line['ey'],line['sy']):
            ymax=max(line['ey'],line['sy'])
    for circle in circle_list:
        if xmin>circle['cx']:
            xmin=circle['cx']
        if xmax<circle['cx']:
            xmax=circle['cx']
        if ymin>circle['cy']:
            ymin=circle['cy']
        if ymax<circle['cy']:
            ymax=circle['cy']
    for arc in arc_list:
        if xmin>arc['sx']:
            xmin=arc['sx']
        if xmax<arc['sx']:
            xmax=arc['sx']
        if ymin>arc['sy']:
            ymin=arc['sy']
        if ymax<arc['sy']:
            ymax=arc['sy']
    for ellipse in ellipse_list:
        if xmin>ellipse['cx']:
            xmin=ellipse['cx']
        if xmax<ellipse['cx']:
            xmax=ellipse['cx']
        if ymin>ellipse['cy']:
            ymin=ellipse['cy']
        if ymax<ellipse['cy']:
            ymax=ellipse['cy']
    return xmin,xmax,ymin,ymax