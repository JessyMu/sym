from svgpathtools import svg2paths
# 使用wsvg函数加载SVG文件
filename = '/home/jesse/Project/SymPoint/dataset/ours/test/svg_gt/A22001.svg'
paths, attrs = svg2paths(filename)

for id,path in enumerate(paths):
    # 打印路径的d属性值
    path_type = path[0].__class__.__name__
    if path_type!='Line':
        print(path_type,id)