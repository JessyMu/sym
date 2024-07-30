from svgpathtools import svg2paths
import svgpathtools
# 使用wsvg函数加载SVG文件
filename = '/home/jesse/Project/SymPoint/data/a22002_pdf2svg.sg'  # 替换为你的SVG文件路径
paths, attrs = svg2paths(filename)

lines=[]
arcs=[]
for id,path in enumerate(paths):
    # 打印路径的d属性值
    for item in path:
        if type(item)==svgpathtools.path.Line:
            lines.append({'elem':item,"attr":attrs[id],'id':attrs[id]['semanticId']})
        elif type(item)==svgpathtools.path.Arc:
            arcs.append({"elem":item,"attr":attrs[id],'id':attrs[id]['semanticId']})