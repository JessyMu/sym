from svgpathtools import svg2paths

# 读取SVG文件
paths, attributes = svg2paths('/home/jesse/Project/SymPoint/out/test/gt/0001-0023.svg')
from svgpathtools import Path

# 创建一个新的3D路径列表
new_paths = []

# 遍历每个2D路径
for path in paths:
    # 将2D路径转换为3D路径
    # 根据需要进行3D转换操作
    new_path = path.copy()  # 示例中将2D路径复制到3D路径
    new_paths.append(new_path)